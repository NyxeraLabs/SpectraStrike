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
from dataclasses import replace

from pkg.orchestrator.messaging import (
    BrokerEnvelope,
    InMemoryKafkaBroker,
    InMemoryRabbitBroker,
    KafkaRoutingModel,
    KafkaTelemetryPublisher,
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


def test_rabbit_publisher_dead_letters_out_of_order_stream() -> None:
    broker = InMemoryRabbitBroker()
    publisher = RabbitMQTelemetryPublisher(broker=broker)

    published = asyncio.run(
        publisher.publish(
            replace(
                _envelope(event_id="evt-1", key="idem-1"),
                ordering_key="tenant-a",
                stream_position=2,
            )
        )
    )
    dead_lettered = asyncio.run(
        publisher.publish(
            replace(
                _envelope(event_id="evt-2", key="idem-2"),
                ordering_key="tenant-a",
                stream_position=1,
            )
        )
    )

    assert published.status is PublishStatus.PUBLISHED
    assert dead_lettered.status is PublishStatus.DEAD_LETTERED
    assert broker.queue_size("telemetry.events") == 1
    assert broker.queue_size("telemetry.events.dlq") == 1


def test_kafka_publisher_publishes_to_topic() -> None:
    broker = InMemoryKafkaBroker()
    publisher = KafkaTelemetryPublisher(broker=broker)

    result = asyncio.run(
        publisher.publish(
            BrokerEnvelope(
                event_id="event-kafka-1",
                event_type="task_submitted",
                timestamp="2026-02-27T13:00:00+00:00",
                actor="alice",
                target="nmap",
                status="success",
                attributes={"task_id": "t1"},
                idempotency_key="event-kafka-1",
                ordering_key="tenant-a",
                stream_position=1,
            )
        )
    )

    assert result.status is PublishStatus.PUBLISHED
    assert broker.topic_size("spectrastrike.telemetry.events") == 1


def test_kafka_publisher_dead_letters_on_retry_exhaustion() -> None:
    broker = InMemoryKafkaBroker()
    routing = KafkaRoutingModel(dead_letter_topic="spectrastrike.telemetry.dlq")
    publisher = KafkaTelemetryPublisher(
        broker=broker,
        routing=routing,
        max_retries=1,
        transient_failures={"idem-fail": 5},
    )

    result = asyncio.run(
        publisher.publish(
            BrokerEnvelope(
                event_id="event-kafka-2",
                event_type="task_submitted",
                timestamp="2026-02-27T13:01:00+00:00",
                actor="alice",
                target="nmap",
                status="success",
                attributes={"task_id": "t2"},
                idempotency_key="idem-fail",
                ordering_key="tenant-a",
                stream_position=2,
            )
        )
    )

    assert result.status is PublishStatus.DEAD_LETTERED
    assert broker.topic_size("spectrastrike.telemetry.events") == 0
    assert broker.topic_size("spectrastrike.telemetry.dlq") == 1
