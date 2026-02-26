# Copyright (c) 2026 NyxeraLabs
# Author: Jose Maria Micoli
# Licensed under BSL 1.1
# Change Date: 2033-02-22 -> Apache-2.0
#
# You may:
# Study
# Modify
# Use for internal security testing
#
# You may NOT:
# Offer as a commercial service
# Sell derived competing products

"""Unit tests for RabbitMQ-backed VectorVue bridge."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.integration.vectorvue.models import ResponseEnvelope
from pkg.integration.vectorvue.rabbitmq_bridge import InMemoryVectorVueBridge
from pkg.orchestrator.messaging import (
    BrokerEnvelope,
    InMemoryRabbitBroker,
    RabbitMQTelemetryPublisher,
    RabbitRoutingModel,
)


@dataclass(slots=True)
class _FakeVectorVueClient:
    event_status: str = "accepted"
    finding_status: str = "accepted"
    status_poll_status: str = "accepted"
    last_federated_idempotency_key: str | None = None

    def send_event(
        self, _payload: dict[str, object], idempotency_key: str | None = None
    ) -> ResponseEnvelope:
        assert idempotency_key
        return ResponseEnvelope(
            request_id="req-1",
            status=self.event_status,
            data={},
        )

    def send_finding(self, _payload: dict[str, object]) -> ResponseEnvelope:
        return ResponseEnvelope(
            request_id="req-2",
            status=self.finding_status,
            data={},
        )

    def get_ingest_status(self, _request_id: str) -> ResponseEnvelope:
        return ResponseEnvelope(
            request_id="req-3",
            status=self.status_poll_status,
            data={},
        )

    def send_federated_telemetry(
        self,
        _payload: dict[str, object],
        idempotency_key: str | None = None,
    ) -> ResponseEnvelope:
        assert idempotency_key
        self.last_federated_idempotency_key = idempotency_key
        return ResponseEnvelope(
            request_id="fed-1",
            status=self.event_status,
            data={"mode": "federated"},
        )


def _publish_sample_envelope(
    broker: InMemoryRabbitBroker,
    *,
    status: str = "success",
) -> None:
    publisher = RabbitMQTelemetryPublisher(
        broker=broker,
        routing=RabbitRoutingModel(queue="telemetry.events"),
    )
    envelope = BrokerEnvelope(
        event_id="evt-1",
        event_type="nmap_scan_completed",
        timestamp="2026-02-26T12:00:00+00:00",
        actor="operator-a",
        target="host-a",
        status=status,
        attributes={
            "tenant_id": "tenant-a",
            "severity": "high",
            "manifest_hash": "mh-" + ("a" * 16),
            "tool_sha256": "sha256:" + ("b" * 64),
            "policy_decision_hash": "ph-" + ("c" * 16),
            "nonce": "nonce-evt-1",
        },
        idempotency_key="idem-1",
    )
    import asyncio

    asyncio.run(publisher.publish(envelope))


def test_inmemory_bridge_drains_and_forwards_event_and_finding() -> None:
    broker = InMemoryRabbitBroker()
    _publish_sample_envelope(broker)
    client = _FakeVectorVueClient()
    bridge = InMemoryVectorVueBridge(
        broker=broker,
        client=client,
        emit_findings_for_all=True,
    )

    result = bridge.drain(limit=10)

    assert result.consumed == 1
    assert result.forwarded_events == 1
    assert result.forwarded_findings == 1
    assert result.failed == 0
    assert result.event_statuses == ["accepted"]
    assert result.finding_statuses == ["accepted"]
    assert result.status_poll_statuses == ["accepted"]
    assert client.last_federated_idempotency_key is not None
    assert len(client.last_federated_idempotency_key) == 64


def test_inmemory_bridge_records_failure_on_api_error() -> None:
    broker = InMemoryRabbitBroker()
    _publish_sample_envelope(broker)

    class _BrokenClient(_FakeVectorVueClient):
        def send_federated_telemetry(
            self,
            _payload: dict[str, object],
            idempotency_key: str | None = None,
        ) -> ResponseEnvelope:
            raise RuntimeError("boom")

    bridge = InMemoryVectorVueBridge(
        broker=broker,
        client=_BrokenClient(),
        emit_findings_for_all=True,
    )

    result = bridge.drain(limit=10)

    assert result.consumed == 1
    assert result.forwarded_events == 0
    assert result.forwarded_findings == 0
    assert result.failed == 1


def test_inmemory_bridge_rejects_fingerprint_mismatch() -> None:
    broker = InMemoryRabbitBroker()
    _publish_sample_envelope(broker)

    class _MismatchClient(_FakeVectorVueClient):
        pass

    # Inject mismatched fingerprint after publishing to simulate tampering.
    envelope = broker.consume("telemetry.events", limit=1)[0]
    tampered = BrokerEnvelope(
        event_id=envelope.event_id,
        event_type=envelope.event_type,
        timestamp=envelope.timestamp,
        actor=envelope.actor,
        target=envelope.target,
        status=envelope.status,
        attributes={
            **envelope.attributes,
            "execution_fingerprint": "deadbeef",
        },
        idempotency_key=envelope.idempotency_key,
        attempt=envelope.attempt,
    )
    broker.push("telemetry.events", tampered)

    bridge = InMemoryVectorVueBridge(
        broker=broker,
        client=_MismatchClient(),
        emit_findings_for_all=True,
    )
    result = bridge.drain(limit=10)
    assert result.failed == 1


def test_inmemory_bridge_rejects_replayed_nonce() -> None:
    broker = InMemoryRabbitBroker()
    _publish_sample_envelope(broker)
    _publish_sample_envelope(broker)

    # Rewrite second envelope with different idempotency key but same nonce to simulate replay.
    first, second = broker.consume("telemetry.events", limit=2)
    broker.push("telemetry.events", first)
    replayed = BrokerEnvelope(
        event_id=second.event_id + "-replay",
        event_type=second.event_type,
        timestamp=second.timestamp,
        actor=second.actor,
        target=second.target,
        status=second.status,
        attributes=second.attributes,
        idempotency_key=second.idempotency_key + "-replay",
        attempt=second.attempt,
    )
    broker.push("telemetry.events", replayed)

    bridge = InMemoryVectorVueBridge(
        broker=broker,
        client=_FakeVectorVueClient(),
        emit_findings_for_all=True,
    )

    result = bridge.drain(limit=10)
    assert result.consumed == 2
    assert result.forwarded_events == 1
    assert result.failed == 1
