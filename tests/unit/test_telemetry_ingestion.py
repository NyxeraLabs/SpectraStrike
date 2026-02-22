"""Unit tests for orchestrator telemetry ingestion pipeline."""

from __future__ import annotations

import pytest

from pkg.orchestrator.telemetry_ingestion import TelemetryIngestionPipeline


def test_ingest_increments_buffer() -> None:
    pipeline = TelemetryIngestionPipeline(batch_size=2)

    event = pipeline.ingest(
        event_type="task_started",
        actor="alice",
        target="nmap",
        status="success",
        task_id="task-1",
    )

    assert event.event_type == "task_started"
    assert pipeline.buffered_count == 1


def test_flush_ready_respects_batch_size() -> None:
    pipeline = TelemetryIngestionPipeline(batch_size=2)

    pipeline.ingest("task_started", "alice", "nmap", "success")
    assert pipeline.flush_ready() == []

    pipeline.ingest("task_completed", "alice", "nmap", "success")
    batch = pipeline.flush_ready()

    assert len(batch) == 2
    assert pipeline.buffered_count == 0


def test_flush_all_returns_all_events() -> None:
    pipeline = TelemetryIngestionPipeline(batch_size=10)

    pipeline.ingest("event_a", "alice", "module", "success")
    pipeline.ingest("event_b", "alice", "module", "success")

    batch = pipeline.flush_all()

    assert len(batch) == 2
    assert pipeline.buffered_count == 0


def test_invalid_batch_size_raises() -> None:
    with pytest.raises(ValueError):
        TelemetryIngestionPipeline(batch_size=0)
