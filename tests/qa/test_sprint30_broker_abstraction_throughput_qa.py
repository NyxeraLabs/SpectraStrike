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

"""Sprint 30 QA checks for broker abstraction and throughput artifacts."""

from __future__ import annotations

import asyncio
from pathlib import Path

from pkg.orchestrator.messaging import InMemoryKafkaBroker, KafkaTelemetryPublisher
from pkg.orchestrator.telemetry_ingestion import TelemetryIngestionPipeline

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_roadmap_marks_sprint30_complete_except_commit() -> None:
    content = (REPO_ROOT / "docs/ROADMAP.md").read_text(encoding="utf-8")
    section_title = "## Sprint 30 (Week 57-58): Broker Abstraction & High-Throughput Path"
    section_start = content.index(section_title)
    next_section = content.find("\n\n## Sprint 31", section_start)
    section = content[section_start:next_section]

    required_checked = [
        "- [x] Abstract broker layer (RabbitMQ/Kafka compatible)",
        "- [x] Enforce ordered execution event streaming",
        "- [x] Normalize telemetry schema for ML ingestion",
        "- [x] Add high-volume load testing",
    ]
    for line in required_checked:
        assert line in section
    assert "Commit Sprint 30 Broker Abstraction & Throughput" in section


def test_sprint30_contracts_exist() -> None:
    content = (REPO_ROOT / "src/pkg/orchestrator/messaging.py").read_text(
        encoding="utf-8"
    )
    required = [
        "class KafkaRoutingModel",
        "class InMemoryKafkaBroker",
        "class KafkaTelemetryPublisher",
        "def _ordered_violation",
    ]
    for symbol in required:
        assert symbol in content


def test_sprint30_high_volume_throughput_kafka_path() -> None:
    broker = InMemoryKafkaBroker()
    publisher = KafkaTelemetryPublisher(broker=broker)
    pipeline = TelemetryIngestionPipeline(batch_size=5000, publisher=publisher)

    for index in range(2000):
        pipeline.ingest(
            event_type="com.nyxeralabs.runner.execution.v1",
            actor="operator-1",
            target=f"urn:target:ip:10.0.1.{index % 255}",
            status="success",
            tenant_id="tenant-a",
            event_index=index,
        )

    result = asyncio.run(pipeline.flush_all_async())

    assert result.published == 2000
    assert result.dead_lettered == 0
    messages = broker.consume("spectrastrike.telemetry.events")
    assert len(messages) == 2000
    assert messages[0].stream_position == 1
    assert messages[-1].stream_position == 2000
