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

"""Sensor core runtime with secure transport and batching (Phase 7 Sprint 7.1)."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import platform
import time
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol
from uuid import uuid4

class SensorCoreError(ValueError):
    """Raised when sensor core operations fail."""


def _canonical_json(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")


@dataclass(frozen=True, slots=True)
class SensorTransportConfig:
    endpoint: str
    verify_tls: bool = True
    ca_cert_path: str | None = None
    client_cert_path: str | None = None
    client_key_path: str | None = None
    mutual_auth_required: bool = True
    timeout_seconds: int = 10

    def __post_init__(self) -> None:
        if not self.endpoint.startswith("https://"):
            raise SensorCoreError("transport endpoint must be https://")
        if not self.verify_tls:
            raise SensorCoreError("verify_tls must remain enabled")
        if self.timeout_seconds < 1:
            raise SensorCoreError("timeout_seconds must be >= 1")
        if self.mutual_auth_required:
            if not self.client_cert_path or not self.client_key_path or not self.ca_cert_path:
                raise SensorCoreError("mTLS requires client_cert_path, client_key_path, and ca_cert_path")


@dataclass(frozen=True, slots=True)
class SensorRuntimeConfig:
    sensor_id: str
    tenant_id: str
    source_system: str = "spectrastrike-sensor"
    platform_name: str = field(default_factory=lambda: platform.system().lower() or "unknown")
    platform_release: str = field(default_factory=platform.release)
    max_batch_size: int = 50
    flush_interval_seconds: int = 5
    retry_max_attempts: int = 3
    retry_backoff_seconds: float = 0.25
    labels: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.sensor_id.strip():
            raise SensorCoreError("sensor_id is required")
        if not self.tenant_id.strip():
            raise SensorCoreError("tenant_id is required")
        if self.max_batch_size < 1:
            raise SensorCoreError("max_batch_size must be >= 1")
        if self.flush_interval_seconds < 1:
            raise SensorCoreError("flush_interval_seconds must be >= 1")
        if self.retry_max_attempts < 1:
            raise SensorCoreError("retry_max_attempts must be >= 1")
        if self.retry_backoff_seconds < 0.0:
            raise SensorCoreError("retry_backoff_seconds must be >= 0")


@dataclass(frozen=True, slots=True)
class TelemetryRecord:
    event_id: str
    event_type: str
    observed_at: datetime
    payload: dict[str, Any]


@dataclass(frozen=True, slots=True)
class SignedTelemetryBatch:
    batch_id: str
    sensor_id: str
    tenant_id: str
    records: tuple[TelemetryRecord, ...]
    created_at: datetime
    payload_hash: str
    signature_b64: str
    signature_algorithm: str = "HMAC-SHA256"


@dataclass(frozen=True, slots=True)
class SensorHealthSnapshot:
    sensor_id: str
    tenant_id: str
    platform_name: str
    queued_events: int
    delivered_batches: int
    failed_batches: int
    last_delivery_at: datetime | None
    last_error: str | None
    updated_at: datetime
    healthy: bool


class TelemetryTransport(Protocol):
    def send(self, *, batch: SignedTelemetryBatch, transport: SensorTransportConfig) -> None:
        """Send signed telemetry batch."""


class SensorBatcher:
    """In-memory telemetry batching helper."""

    def __init__(self, *, max_batch_size: int) -> None:
        self._max_batch_size = max_batch_size
        self._queue: list[TelemetryRecord] = []

    def enqueue(self, record: TelemetryRecord) -> None:
        self._queue.append(record)

    def size(self) -> int:
        return len(self._queue)

    def should_flush(self) -> bool:
        return len(self._queue) >= self._max_batch_size

    def pop_batch(self, *, batch_size: int) -> tuple[TelemetryRecord, ...]:
        size = min(batch_size, len(self._queue))
        rows = tuple(self._queue[:size])
        self._queue = self._queue[size:]
        return rows

    def drain_all(self) -> tuple[TelemetryRecord, ...]:
        rows = tuple(self._queue)
        self._queue = []
        return rows


class SensorHealthMonitor:
    """Track sensor delivery health and queue behavior."""

    def __init__(self, *, runtime: SensorRuntimeConfig) -> None:
        self._runtime = runtime
        self._delivered_batches = 0
        self._failed_batches = 0
        self._last_delivery_at: datetime | None = None
        self._last_error: str | None = None
        self._updated_at: datetime = datetime.now(UTC)

    def mark_delivery(self) -> None:
        self._delivered_batches += 1
        self._last_delivery_at = datetime.now(UTC)
        self._last_error = None
        self._updated_at = datetime.now(UTC)

    def mark_failure(self, *, error: str) -> None:
        self._failed_batches += 1
        self._last_error = error
        self._updated_at = datetime.now(UTC)

    def snapshot(self, *, queued_events: int) -> SensorHealthSnapshot:
        healthy = self._failed_batches <= (self._delivered_batches + 2)
        return SensorHealthSnapshot(
            sensor_id=self._runtime.sensor_id,
            tenant_id=self._runtime.tenant_id,
            platform_name=self._runtime.platform_name,
            queued_events=queued_events,
            delivered_batches=self._delivered_batches,
            failed_batches=self._failed_batches,
            last_delivery_at=self._last_delivery_at,
            last_error=self._last_error,
            updated_at=self._updated_at,
            healthy=healthy,
        )


class RemoteSensorConfigService:
    """Apply runtime-safe remote sensor config changes."""

    ALLOWED_KEYS = {
        "max_batch_size",
        "flush_interval_seconds",
        "retry_max_attempts",
        "retry_backoff_seconds",
        "labels",
    }

    def apply_update(
        self,
        *,
        runtime: SensorRuntimeConfig,
        patch: dict[str, Any],
    ) -> SensorRuntimeConfig:
        unknown = sorted(set(patch.keys()) - self.ALLOWED_KEYS)
        if unknown:
            raise SensorCoreError(f"unsupported remote config keys: {','.join(unknown)}")
        updated = replace(
            runtime,
            max_batch_size=int(patch.get("max_batch_size", runtime.max_batch_size)),
            flush_interval_seconds=int(patch.get("flush_interval_seconds", runtime.flush_interval_seconds)),
            retry_max_attempts=int(patch.get("retry_max_attempts", runtime.retry_max_attempts)),
            retry_backoff_seconds=float(patch.get("retry_backoff_seconds", runtime.retry_backoff_seconds)),
            labels=dict(patch.get("labels", runtime.labels)),
        )
        return updated


class SensorCoreAgent:
    """Cross-platform lightweight telemetry sensor agent."""

    def __init__(
        self,
        *,
        runtime: SensorRuntimeConfig,
        transport: SensorTransportConfig,
        signing_key_path: str,
        transport_client: TelemetryTransport,
    ) -> None:
        self.runtime = runtime
        self.transport = transport
        self._transport_client = transport_client
        self._signing_key = Path(signing_key_path).read_bytes()
        if not self._signing_key:
            raise SensorCoreError("signing key file is empty")
        self._batcher = SensorBatcher(max_batch_size=self.runtime.max_batch_size)
        self._health = SensorHealthMonitor(runtime=self.runtime)
        self._last_flush_monotonic = time.monotonic()

    def ingest_event(self, *, event_type: str, payload: dict[str, Any]) -> TelemetryRecord:
        if not event_type.strip():
            raise SensorCoreError("event_type is required")
        event = TelemetryRecord(
            event_id=f"evt-{uuid4()}",
            event_type=event_type.strip(),
            observed_at=datetime.now(UTC),
            payload=dict(payload),
        )
        self._batcher.enqueue(event)
        return event

    def flush_if_needed(self, *, force: bool = False) -> list[SignedTelemetryBatch]:
        batches: list[SignedTelemetryBatch] = []
        now_mono = time.monotonic()
        interval_elapsed = (now_mono - self._last_flush_monotonic) >= float(self.runtime.flush_interval_seconds)
        should_flush = force or self._batcher.should_flush() or interval_elapsed
        if not should_flush or self._batcher.size() == 0:
            return batches
        while self._batcher.size() > 0:
            rows = self._batcher.pop_batch(batch_size=self.runtime.max_batch_size)
            batch = self._build_signed_batch(rows)
            self._deliver_with_retry(batch=batch)
            batches.append(batch)
        self._last_flush_monotonic = time.monotonic()
        return batches

    def get_health(self) -> SensorHealthSnapshot:
        return self._health.snapshot(queued_events=self._batcher.size())

    def apply_remote_config(self, *, patch: dict[str, Any]) -> SensorRuntimeConfig:
        updater = RemoteSensorConfigService()
        self.runtime = updater.apply_update(runtime=self.runtime, patch=patch)
        pending = self._batcher.drain_all()
        self._batcher = SensorBatcher(max_batch_size=self.runtime.max_batch_size)
        for row in pending:
            self._batcher.enqueue(row)
        return self.runtime

    def verify_batch_signature(self, batch: SignedTelemetryBatch) -> bool:
        payload = self._batch_payload_for_signing(batch.records, batch.batch_id, batch.created_at)
        signature = base64.b64decode(batch.signature_b64.encode("utf-8"))
        expected = hmac.new(self._signing_key, payload, hashlib.sha256).digest()
        return hmac.compare_digest(signature, expected)

    def _deliver_with_retry(self, *, batch: SignedTelemetryBatch) -> None:
        attempts = 0
        while attempts < self.runtime.retry_max_attempts:
            attempts += 1
            try:
                self._transport_client.send(batch=batch, transport=self.transport)
                self._health.mark_delivery()
                return
            except Exception as exc:
                self._health.mark_failure(error=str(exc))
                if attempts >= self.runtime.retry_max_attempts:
                    raise SensorCoreError(f"batch delivery failed after retries: {exc}") from exc
                if self.runtime.retry_backoff_seconds > 0:
                    time.sleep(self.runtime.retry_backoff_seconds)

    def _build_signed_batch(self, records: tuple[TelemetryRecord, ...]) -> SignedTelemetryBatch:
        created_at = datetime.now(UTC)
        batch_id = f"batch-{uuid4()}"
        payload = self._batch_payload_for_signing(records, batch_id, created_at)
        payload_hash = hashlib.sha256(payload).hexdigest()
        signature = hmac.new(self._signing_key, payload, hashlib.sha256).digest()
        return SignedTelemetryBatch(
            batch_id=batch_id,
            sensor_id=self.runtime.sensor_id,
            tenant_id=self.runtime.tenant_id,
            records=records,
            created_at=created_at,
            payload_hash=payload_hash,
            signature_b64=base64.b64encode(signature).decode("utf-8"),
        )

    def _batch_payload_for_signing(
        self,
        records: tuple[TelemetryRecord, ...],
        batch_id: str,
        created_at: datetime,
    ) -> bytes:
        return _canonical_json(
            {
                "batch_id": batch_id,
                "sensor_id": self.runtime.sensor_id,
                "tenant_id": self.runtime.tenant_id,
                "created_at": created_at.isoformat(),
                "records": [
                    {
                        "event_id": row.event_id,
                        "event_type": row.event_type,
                        "observed_at": row.observed_at.isoformat(),
                        "payload": row.payload,
                    }
                    for row in records
                ],
            }
        )
