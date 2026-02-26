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
        tenant_id="tenant-a",
        task_id="task-1",
    )

    assert event.event_type == "task_started"
    assert pipeline.buffered_count == 1


def test_flush_ready_respects_batch_size() -> None:
    pipeline = TelemetryIngestionPipeline(batch_size=2)

    pipeline.ingest("task_started", "alice", "nmap", "success", tenant_id="tenant-a")
    assert pipeline.flush_ready() == []

    pipeline.ingest(
        "task_completed",
        "alice",
        "nmap",
        "success",
        tenant_id="tenant-a",
    )
    batch = pipeline.flush_ready()

    assert len(batch) == 2
    assert pipeline.buffered_count == 0


def test_flush_all_returns_all_events() -> None:
    pipeline = TelemetryIngestionPipeline(batch_size=10)

    pipeline.ingest("event_a", "alice", "module", "success", tenant_id="tenant-a")
    pipeline.ingest("event_b", "alice", "module", "success", tenant_id="tenant-a")

    batch = pipeline.flush_all()

    assert len(batch) == 2
    assert pipeline.buffered_count == 0


def test_invalid_batch_size_raises() -> None:
    with pytest.raises(ValueError):
        TelemetryIngestionPipeline(batch_size=0)


def test_ingest_requires_tenant_id() -> None:
    pipeline = TelemetryIngestionPipeline(batch_size=2)
    with pytest.raises(ValueError, match="tenant_id"):
        pipeline.ingest("task_started", "alice", "nmap", "success", tenant_id="")


def test_ingest_payload_parses_cloudevent() -> None:
    pipeline = TelemetryIngestionPipeline(batch_size=10)

    event = pipeline.ingest_payload(
        {
            "specversion": "1.0",
            "type": "com.nyxeralabs.runner.execution.v1",
            "source": "urn:spectrastrike:runner",
            "subject": "task-1",
            "data": {
                "operator_id": "alice",
                "tenant_id": "tenant-a",
                "target_urn": "urn:target:ip:10.0.0.5",
                "status": "success",
                "exit_code": 0,
            },
        }
    )

    assert event.event_type == "com.nyxeralabs.runner.execution.v1"
    assert event.actor == "alice"
    assert event.target == "urn:target:ip:10.0.0.5"
    assert event.status == "success"
    assert event.tenant_id == "tenant-a"
    assert event.attributes["exit_code"] == 0
