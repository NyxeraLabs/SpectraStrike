# Copyright (c) 2026 NyxeraLabs
# Author: José María Micoli
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

"""Telemetry ingestion pipeline for orchestrator runtime events."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from threading import Lock
from typing import Any
from uuid import uuid4

from pkg.logging.framework import emit_audit_event, get_logger

logger = get_logger("spectrastrike.orchestrator.telemetry")


@dataclass(slots=True)
class TelemetryEvent:
    """Normalized telemetry event model."""

    event_type: str
    actor: str
    target: str
    status: str
    attributes: dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class TelemetryIngestionPipeline:
    """Thread-safe telemetry ingestion with buffered batch flushing."""

    def __init__(self, batch_size: int = 50) -> None:
        if batch_size <= 0:
            raise ValueError("batch_size must be greater than zero")
        self._batch_size = batch_size
        self._buffer: list[TelemetryEvent] = []
        self._lock = Lock()

    def ingest(
        self,
        event_type: str,
        actor: str,
        target: str,
        status: str,
        **attributes: Any,
    ) -> TelemetryEvent:
        """Normalize and ingest a telemetry event into the buffer."""
        event = TelemetryEvent(
            event_type=event_type,
            actor=actor,
            target=target,
            status=status,
            attributes=attributes,
        )

        with self._lock:
            self._buffer.append(event)

        logger.info("Telemetry event ingested: %s", event.event_id)
        emit_audit_event(
            action="telemetry_ingest",
            actor=actor,
            target=target,
            status=status,
            event_id=event.event_id,
            event_type=event_type,
        )
        return event

    def flush_ready(self) -> list[TelemetryEvent]:
        """Flush a full batch when enough events are buffered."""
        with self._lock:
            if len(self._buffer) < self._batch_size:
                return []
            batch = self._buffer[: self._batch_size]
            self._buffer = self._buffer[self._batch_size :]

        logger.info("Telemetry batch flushed: %s events", len(batch))
        return batch

    def flush_all(self) -> list[TelemetryEvent]:
        """Flush all buffered events regardless of batch size."""
        with self._lock:
            batch = list(self._buffer)
            self._buffer.clear()

        if batch:
            logger.info("Telemetry full flush: %s events", len(batch))
        return batch

    @property
    def buffered_count(self) -> int:
        """Return number of currently buffered events."""
        with self._lock:
            return len(self._buffer)
