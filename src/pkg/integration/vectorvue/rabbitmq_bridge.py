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

"""RabbitMQ-backed forwarding bridge from SpectraStrike telemetry to VectorVue."""

from __future__ import annotations

import json
import ssl
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from pkg.integration.vectorvue.client import VectorVueClient
from pkg.orchestrator.messaging import (
    BrokerEnvelope,
    InMemoryRabbitBroker,
    RabbitMQConnectionConfig,
    RabbitRoutingModel,
)

try:
    import pika
except ImportError:  # pragma: no cover - optional dependency for live broker mode
    pika = None


@dataclass(slots=True)
class BridgeDrainResult:
    """Summary of a VectorVue bridge drain execution."""

    consumed: int = 0
    forwarded_events: int = 0
    forwarded_findings: int = 0
    failed: int = 0
    event_statuses: list[str] = field(default_factory=list)
    finding_statuses: list[str] = field(default_factory=list)
    status_poll_statuses: list[str] = field(default_factory=list)


class InMemoryVectorVueBridge:
    """Bridge adapter for in-memory RabbitMQ broker queues."""

    def __init__(
        self,
        *,
        broker: InMemoryRabbitBroker,
        client: VectorVueClient,
        queue: str = "telemetry.events",
        emit_findings_for_all: bool = False,
    ) -> None:
        self._broker = broker
        self._client = client
        self._queue = queue
        self._emit_findings_for_all = emit_findings_for_all

    def drain(self, limit: int | None = None) -> BridgeDrainResult:
        result = BridgeDrainResult()
        envelopes = self._broker.consume(self._queue, limit=limit)
        for envelope in envelopes:
            result.consumed += 1
            self._forward_one(envelope, result)
        return result

    def _forward_one(self, envelope: BrokerEnvelope, result: BridgeDrainResult) -> None:
        try:
            event_response = self._client.send_event(
                _build_event_payload(envelope),
                idempotency_key=envelope.idempotency_key,
            )
            result.forwarded_events += 1
            result.event_statuses.append(event_response.status)

            if event_response.request_id:
                status_response = self._client.get_ingest_status(event_response.request_id)
                result.status_poll_statuses.append(status_response.status)

            if self._emit_findings_for_all or _should_emit_finding(envelope):
                finding_response = self._client.send_finding(
                    _build_finding_payload(envelope)
                )
                result.forwarded_findings += 1
                result.finding_statuses.append(finding_response.status)
        except Exception:
            result.failed += 1


class PikaVectorVueBridge:
    """Bridge adapter for live RabbitMQ queues via pika basic_get polling."""

    def __init__(
        self,
        *,
        client: VectorVueClient,
        connection: RabbitMQConnectionConfig | None = None,
        routing: RabbitRoutingModel | None = None,
        emit_findings_for_all: bool = False,
    ) -> None:
        if pika is None:
            raise RuntimeError("pika package is required for PikaVectorVueBridge")
        self._client = client
        self._connection = connection or RabbitMQConnectionConfig.from_env()
        self._routing = routing or RabbitRoutingModel()
        self._emit_findings_for_all = emit_findings_for_all

    def drain(self, limit: int = 100) -> BridgeDrainResult:
        if limit <= 0:
            raise ValueError("limit must be greater than zero")

        result = BridgeDrainResult()
        connection = self._open_connection()
        try:
            channel = connection.channel()
            queue_name = self._routing.queue
            for _ in range(limit):
                method_frame, _, body = channel.basic_get(queue=queue_name, auto_ack=False)
                if method_frame is None:
                    break

                result.consumed += 1
                envelope = _decode_envelope(body)
                try:
                    event_response = self._client.send_event(
                        _build_event_payload(envelope),
                        idempotency_key=envelope.idempotency_key,
                    )
                    result.forwarded_events += 1
                    result.event_statuses.append(event_response.status)

                    if event_response.request_id:
                        status_response = self._client.get_ingest_status(
                            event_response.request_id
                        )
                        result.status_poll_statuses.append(status_response.status)

                    if self._emit_findings_for_all or _should_emit_finding(envelope):
                        finding_response = self._client.send_finding(
                            _build_finding_payload(envelope)
                        )
                        result.forwarded_findings += 1
                        result.finding_statuses.append(finding_response.status)

                    channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                except Exception:
                    result.failed += 1
                    channel.basic_nack(delivery_tag=method_frame.delivery_tag, requeue=False)
        finally:
            connection.close()
        return result

    def _open_connection(self) -> "pika.BlockingConnection":
        credentials = pika.PlainCredentials(
            self._connection.username, self._connection.password
        )
        ssl_options = None
        if self._connection.ssl_enabled:
            context = ssl.create_default_context(cafile=self._connection.ssl_ca_file)
            if self._connection.ssl_cert_file and self._connection.ssl_key_file:
                context.load_cert_chain(
                    certfile=self._connection.ssl_cert_file,
                    keyfile=self._connection.ssl_key_file,
                )
            ssl_options = pika.SSLOptions(context, self._connection.host)
        parameters = pika.ConnectionParameters(
            host=self._connection.host,
            port=self._connection.port,
            virtual_host=self._connection.virtual_host,
            credentials=credentials,
            heartbeat=self._connection.heartbeat,
            blocked_connection_timeout=self._connection.blocked_connection_timeout,
            ssl_options=ssl_options,
        )
        return pika.BlockingConnection(parameters)


def _decode_envelope(body: bytes) -> BrokerEnvelope:
    parsed = json.loads(body.decode("utf-8"))
    return BrokerEnvelope(
        event_id=str(parsed["event_id"]),
        event_type=str(parsed["event_type"]),
        timestamp=str(parsed["timestamp"]),
        actor=str(parsed["actor"]),
        target=str(parsed["target"]),
        status=str(parsed["status"]),
        attributes=dict(parsed.get("attributes", {})),
        idempotency_key=str(parsed["idempotency_key"]),
        attempt=int(parsed.get("attempt", 1)),
    )


def _build_event_payload(envelope: BrokerEnvelope) -> dict[str, Any]:
    now = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    tenant_id = str(envelope.attributes.get("tenant_id", ""))
    message = str(
        envelope.attributes.get(
            "message",
            f"SpectraStrike telemetry event {envelope.event_type} status={envelope.status}",
        )
    )
    severity = str(envelope.attributes.get("severity", "medium")).lower()
    return {
        "source_system": "spectrastrike",
        "event_type": envelope.event_type.upper(),
        "occurred_at": envelope.timestamp or now,
        "severity": severity,
        "asset_ref": envelope.target,
        "message": message,
        "metadata": {
            "event_id": envelope.event_id,
            "tenant_id": tenant_id,
            "actor": envelope.actor,
            "status": envelope.status,
            "attempt": envelope.attempt,
            "attributes": envelope.attributes,
        },
    }


def _build_finding_payload(envelope: BrokerEnvelope) -> dict[str, Any]:
    status = "open" if envelope.status.lower() in {"failed", "error"} else "triaged"
    first_seen = envelope.timestamp or datetime.now(UTC).isoformat()
    return {
        "title": f"Telemetry finding: {envelope.event_type}",
        "description": (
            f"Derived from broker event {envelope.event_id} "
            f"with status {envelope.status}"
        ),
        "severity": str(envelope.attributes.get("severity", "medium")).lower(),
        "status": status,
        "first_seen": first_seen,
        "asset_ref": envelope.target,
        "recommendation": "Review upstream telemetry and execution context.",
        "metadata": {
            "event_id": envelope.event_id,
            "tenant_id": envelope.attributes.get("tenant_id", ""),
            "actor": envelope.actor,
            "source": "rabbitmq-bridge",
        },
    }


def _should_emit_finding(envelope: BrokerEnvelope) -> bool:
    severity = str(envelope.attributes.get("severity", "")).lower()
    return envelope.status.lower() in {"failed", "error"} or severity in {
        "high",
        "critical",
    }
