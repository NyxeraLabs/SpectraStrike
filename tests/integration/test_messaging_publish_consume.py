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

"""Integration tests for telemetry broker publish/consume flow."""

from __future__ import annotations

import asyncio

from pkg.orchestrator.messaging import InMemoryRabbitBroker, RabbitMQTelemetryPublisher
from pkg.orchestrator.telemetry_ingestion import TelemetryIngestionPipeline


def test_telemetry_flush_publish_consume_flow() -> None:
    broker = InMemoryRabbitBroker()
    publisher = RabbitMQTelemetryPublisher(broker=broker)
    pipeline = TelemetryIngestionPipeline(batch_size=2, publisher=publisher)

    pipeline.ingest("task_submitted", "alice", "nmap", "success", task_id="t1")
    pipeline.ingest("task_started", "alice", "nmap", "success", task_id="t1")
    pipeline.ingest("task_completed", "alice", "nmap", "success", task_id="t1")

    ready_result = asyncio.run(pipeline.flush_ready_async())

    assert ready_result.published == 2
    assert ready_result.dead_lettered == 0
    assert pipeline.buffered_count == 1

    ready_messages = broker.consume("telemetry.events")
    assert len(ready_messages) == 2
    assert ready_messages[0].event_type == "task_submitted"
    assert ready_messages[1].event_type == "task_started"

    all_result = asyncio.run(pipeline.flush_all_async())

    assert all_result.published == 1
    final_messages = broker.consume("telemetry.events")
    assert len(final_messages) == 1
    assert final_messages[0].event_type == "task_completed"
