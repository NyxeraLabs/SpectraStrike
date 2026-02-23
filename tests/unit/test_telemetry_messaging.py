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

"""Unit tests for messaging-backed telemetry publishing."""

from __future__ import annotations

import asyncio

from pkg.orchestrator.messaging import (
    BrokerEnvelope,
    InMemoryRabbitBroker,
    PublishStatus,
    RabbitMQTelemetryPublisher,
    RabbitRoutingModel,
)


def _envelope(event_id: str = "event-1", key: str | None = None) -> BrokerEnvelope:
    return BrokerEnvelope(
        event_id=event_id,
        event_type="task_submitted",
        timestamp="2026-02-23T10:00:00+00:00",
        actor="alice",
        target="nmap",
        status="success",
        attributes={"task_id": "t1"},
        idempotency_key=key or event_id,
    )


def test_rabbit_publisher_publishes_to_queue() -> None:
    broker = InMemoryRabbitBroker()
    publisher = RabbitMQTelemetryPublisher(broker=broker)

    result = asyncio.run(publisher.publish(_envelope()))

    assert result.status is PublishStatus.PUBLISHED
    assert broker.queue_size("telemetry.events") == 1
    assert broker.queue_size("telemetry.events.dlq") == 0


def test_rabbit_publisher_idempotency_deduplicates_replays() -> None:
    broker = InMemoryRabbitBroker()
    publisher = RabbitMQTelemetryPublisher(broker=broker)

    first = asyncio.run(publisher.publish(_envelope(event_id="evt-1", key="idem-1")))
    second = asyncio.run(publisher.publish(_envelope(event_id="evt-2", key="idem-1")))

    assert first.status is PublishStatus.PUBLISHED
    assert second.status is PublishStatus.DEDUPLICATED
    assert broker.queue_size("telemetry.events") == 1


def test_rabbit_publisher_retries_then_succeeds() -> None:
    broker = InMemoryRabbitBroker()
    publisher = RabbitMQTelemetryPublisher(
        broker=broker,
        max_retries=3,
        transient_failures={"idem-retry": 2},
    )

    result = asyncio.run(
        publisher.publish(_envelope(event_id="evt-retry", key="idem-retry"))
    )

    assert result.status is PublishStatus.PUBLISHED
    assert result.attempts == 3
    consumed = broker.consume("telemetry.events")
    assert len(consumed) == 1
    assert consumed[0].attempt == 3


def test_rabbit_publisher_dead_letters_on_retry_exhaustion() -> None:
    broker = InMemoryRabbitBroker()
    routing = RabbitRoutingModel(dead_letter_queue="telemetry.dead")
    publisher = RabbitMQTelemetryPublisher(
        broker=broker,
        routing=routing,
        max_retries=2,
        transient_failures={"idem-fail": 10},
    )

    result = asyncio.run(
        publisher.publish(_envelope(event_id="evt-fail", key="idem-fail"))
    )

    assert result.status is PublishStatus.DEAD_LETTERED
    assert result.attempts == 3
    assert broker.queue_size("telemetry.events") == 0
    dlq_items = broker.consume("telemetry.dead")
    assert len(dlq_items) == 1
    assert dlq_items[0].idempotency_key == "idem-fail"
