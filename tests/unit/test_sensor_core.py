# Copyright (c) 2026 NyxeraLabs
# Licensed under BSL 1.1
# Change Date: 2033-02-22 -> Apache-2.0

"""Unit tests for sensor core runtime and ingestion reliability."""

from __future__ import annotations

from pathlib import Path
import tempfile

from pkg.telemetry.sensor_core import (
    SensorCoreAgent,
    SensorCoreError,
    SensorRuntimeConfig,
    SensorTransportConfig,
    SignedTelemetryBatch,
    TelemetryTransport,
)


class _FlakyTransport(TelemetryTransport):
    def __init__(self, *, fail_first: int = 0) -> None:
        self.fail_first = fail_first
        self.calls = 0
        self.sent: list[SignedTelemetryBatch] = []

    def send(self, *, batch: SignedTelemetryBatch, transport: SensorTransportConfig) -> None:
        self.calls += 1
        if self.calls <= self.fail_first:
            raise RuntimeError("simulated transport failure")
        self.sent.append(batch)


def _write_temp_private_key() -> str:
    pem = b"sprint-51-sensor-signing-key"
    handle = tempfile.NamedTemporaryFile(delete=False)
    handle.write(pem)
    handle.flush()
    handle.close()
    return handle.name


def test_sensor_core_ingestion_reliability_with_retry_and_batching() -> None:
    key_path = _write_temp_private_key()
    transport = _FlakyTransport(fail_first=1)
    agent = SensorCoreAgent(
        runtime=SensorRuntimeConfig(
            sensor_id="sensor-01",
            tenant_id="tenant-a",
            max_batch_size=2,
            flush_interval_seconds=30,
            retry_max_attempts=3,
            retry_backoff_seconds=0.0,
        ),
        transport=SensorTransportConfig(
            endpoint="https://vectorvue.local/internal/telemetry",
            ca_cert_path="/tmp/ca.crt",
            client_cert_path="/tmp/client.crt",
            client_key_path="/tmp/client.key",
        ),
        signing_key_path=key_path,
        transport_client=transport,
    )
    agent.ingest_event(event_type="process_start", payload={"pid": 10})
    agent.ingest_event(event_type="process_start", payload={"pid": 11})
    batches = agent.flush_if_needed()
    assert len(batches) == 1
    assert transport.calls == 2  # first fails, second succeeds
    assert len(transport.sent) == 1
    assert agent.verify_batch_signature(batches[0]) is True
    health = agent.get_health()
    assert health.delivered_batches == 1
    assert health.failed_batches >= 1
    Path(key_path).unlink(missing_ok=True)


def test_sensor_remote_config_keeps_queued_events() -> None:
    key_path = _write_temp_private_key()
    transport = _FlakyTransport()
    agent = SensorCoreAgent(
        runtime=SensorRuntimeConfig(
            sensor_id="sensor-02",
            tenant_id="tenant-a",
            max_batch_size=10,
            flush_interval_seconds=30,
        ),
        transport=SensorTransportConfig(
            endpoint="https://vectorvue.local/internal/telemetry",
            ca_cert_path="/tmp/ca.crt",
            client_cert_path="/tmp/client.crt",
            client_key_path="/tmp/client.key",
        ),
        signing_key_path=key_path,
        transport_client=transport,
    )
    agent.ingest_event(event_type="file_create", payload={"path": "/tmp/a"})
    updated = agent.apply_remote_config(patch={"max_batch_size": 1, "retry_max_attempts": 2})
    assert updated.max_batch_size == 1
    batches = agent.flush_if_needed(force=True)
    assert len(batches) == 1
    assert len(transport.sent) == 1
    Path(key_path).unlink(missing_ok=True)


def test_sensor_transport_requires_tls_and_mtls() -> None:
    with tempfile.NamedTemporaryFile() as handle:
        try:
            SensorTransportConfig(
                endpoint="http://vectorvue.local",
                ca_cert_path=handle.name,
                client_cert_path=handle.name,
                client_key_path=handle.name,
            )
            raise AssertionError("expected SensorCoreError")
        except SensorCoreError:
            pass
