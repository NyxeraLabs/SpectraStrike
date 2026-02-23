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

"""Broker-agnostic telemetry publishing contracts and RabbitMQ-first adapter."""

from __future__ import annotations

import asyncio
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, replace
from enum import Enum
import json
import os
import ssl
from threading import Lock
from typing import Protocol

try:
    import pika
except ImportError:  # pragma: no cover - optional dependency for real broker adapter
    pika = None


@dataclass(slots=True, frozen=True)
class BrokerEnvelope:
    """Standardized telemetry envelope for broker transport."""

    event_id: str
    event_type: str
    timestamp: str
    actor: str
    target: str
    status: str
    attributes: dict[str, object]
    idempotency_key: str
    attempt: int = 1


class PublishStatus(str, Enum):
    """Result status for a single publish request."""

    PUBLISHED = "published"
    DEDUPLICATED = "deduplicated"
    DEAD_LETTERED = "dead_lettered"


@dataclass(slots=True, frozen=True)
class PublishAttemptResult:
    """Result for a single envelope publish operation."""

    status: PublishStatus
    attempts: int
    error: str | None = None


@dataclass(slots=True, frozen=True)
class TelemetryPublishResult:
    """Aggregated publish outcome for a telemetry flush operation."""

    published: int
    deduplicated: int
    dead_lettered: int
    retries: int


@dataclass(slots=True, frozen=True)
class RabbitRoutingModel:
    """Logical RabbitMQ routing model for telemetry events."""

    exchange: str = "spectrastrike.telemetry"
    routing_key: str = "telemetry.events"
    queue: str = "telemetry.events"
    dead_letter_queue: str = "telemetry.events.dlq"


@dataclass(slots=True, frozen=True)
class RabbitMQConnectionConfig:
    """Connection config for dockerized RabbitMQ broker."""

    host: str = "rabbitmq"
    port: int = 5672
    username: str = "spectra"
    password: str = "spectra"
    virtual_host: str = "/"
    heartbeat: int = 60
    blocked_connection_timeout: int = 30
    ssl_enabled: bool = True
    ssl_ca_file: str | None = "/app/docker/pki/ca.crt"
    ssl_cert_file: str | None = "/app/docker/pki/app/client.crt"
    ssl_key_file: str | None = "/app/docker/pki/app/client.key"

    @classmethod
    def from_env(cls, prefix: str = "RABBITMQ_") -> RabbitMQConnectionConfig:
        """Build connection config from environment variables."""
        host = os.getenv(f"{prefix}HOST", "rabbitmq")
        port = int(os.getenv(f"{prefix}PORT", "5672"))
        username = os.getenv(f"{prefix}USER", "spectra")
        password = os.getenv(f"{prefix}PASSWORD", "spectra")
        virtual_host = os.getenv(f"{prefix}VHOST", "/")
        heartbeat = int(os.getenv(f"{prefix}HEARTBEAT", "60"))
        ssl_raw = os.getenv(f"{prefix}SSL", "true").strip().lower()
        ssl_enabled = ssl_raw in {"1", "true", "yes", "on"}
        ssl_ca_file = os.getenv(f"{prefix}SSL_CA_FILE", "/app/docker/pki/ca.crt")
        ssl_cert_file = os.getenv(
            f"{prefix}SSL_CERT_FILE", "/app/docker/pki/app/client.crt"
        )
        ssl_key_file = os.getenv(
            f"{prefix}SSL_KEY_FILE", "/app/docker/pki/app/client.key"
        )
        blocked_connection_timeout = int(
            os.getenv(
                f"{prefix}BLOCKED_CONNECTION_TIMEOUT",
                "30",
            )
        )
        return cls(
            host=host,
            port=port,
            username=username,
            password=password,
            virtual_host=virtual_host,
            heartbeat=heartbeat,
            blocked_connection_timeout=blocked_connection_timeout,
            ssl_enabled=ssl_enabled,
            ssl_ca_file=ssl_ca_file,
            ssl_cert_file=ssl_cert_file,
            ssl_key_file=ssl_key_file,
        )


class TelemetryPublisher(Protocol):
    """Broker transport abstraction for telemetry publishing."""

    async def publish(self, envelope: BrokerEnvelope) -> PublishAttemptResult:
        """Publish one envelope using broker delivery policy."""


class InMemoryRabbitBroker:
    """In-memory RabbitMQ-style broker for deterministic local/integration tests."""

    def __init__(self) -> None:
        self._queues: dict[str, deque[BrokerEnvelope]] = defaultdict(deque)
        self._bindings: dict[tuple[str, str], list[str]] = defaultdict(list)
        self._lock = Lock()

    def declare_queue(self, queue: str) -> None:
        with self._lock:
            self._queues[queue]

    def bind_queue(self, exchange: str, routing_key: str, queue: str) -> None:
        with self._lock:
            if queue not in self._bindings[(exchange, routing_key)]:
                self._bindings[(exchange, routing_key)].append(queue)
            self._queues[queue]

    def publish(self, exchange: str, routing_key: str, envelope: BrokerEnvelope) -> None:
        with self._lock:
            queues = self._bindings.get((exchange, routing_key), [])
            for queue in queues:
                self._queues[queue].append(envelope)

    def push(self, queue: str, envelope: BrokerEnvelope) -> None:
        with self._lock:
            self._queues[queue].append(envelope)

    def consume(self, queue: str, limit: int | None = None) -> list[BrokerEnvelope]:
        with self._lock:
            out: list[BrokerEnvelope] = []
            items = self._queues[queue]
            if limit is None:
                limit = len(items)
            for _ in range(min(limit, len(items))):
                out.append(items.popleft())
            return out

    def queue_size(self, queue: str) -> int:
        with self._lock:
            return len(self._queues[queue])


class RabbitMQTelemetryPublisher:
    """RabbitMQ-first telemetry publisher with retry, DLQ, and idempotency."""

    def __init__(
        self,
        broker: InMemoryRabbitBroker,
        routing: RabbitRoutingModel | None = None,
        max_retries: int = 3,
        transient_failures: dict[str, int] | None = None,
    ) -> None:
        if max_retries < 0:
            raise ValueError("max_retries must be greater than or equal to zero")

        self._broker = broker
        self._routing = routing or RabbitRoutingModel()
        self._max_retries = max_retries
        self._transient_failures = transient_failures or {}
        self._seen_keys: set[str] = set()

        self._broker.declare_queue(self._routing.queue)
        self._broker.declare_queue(self._routing.dead_letter_queue)
        self._broker.bind_queue(
            exchange=self._routing.exchange,
            routing_key=self._routing.routing_key,
            queue=self._routing.queue,
        )

    async def publish(self, envelope: BrokerEnvelope) -> PublishAttemptResult:
        key = envelope.idempotency_key
        if key in self._seen_keys:
            return PublishAttemptResult(status=PublishStatus.DEDUPLICATED, attempts=0)

        attempts = 0
        while attempts <= self._max_retries:
            attempts += 1
            try:
                if self._transient_failures.get(key, 0) > 0:
                    self._transient_failures[key] -= 1
                    raise RuntimeError("simulated transient broker failure")

                self._broker.publish(
                    exchange=self._routing.exchange,
                    routing_key=self._routing.routing_key,
                    envelope=replace(envelope, attempt=attempts),
                )
                self._seen_keys.add(key)
                return PublishAttemptResult(
                    status=PublishStatus.PUBLISHED,
                    attempts=attempts,
                )
            except RuntimeError as exc:
                if attempts > self._max_retries:
                    self._broker.push(
                        self._routing.dead_letter_queue,
                        replace(envelope, attempt=attempts),
                    )
                    return PublishAttemptResult(
                        status=PublishStatus.DEAD_LETTERED,
                        attempts=attempts,
                        error=str(exc),
                    )

        raise RuntimeError("unreachable publish state")


class PikaRabbitMQTelemetryPublisher:
    """RabbitMQ adapter backed by pika for dockerized runtime environments."""

    def __init__(
        self,
        connection: RabbitMQConnectionConfig | None = None,
        routing: RabbitRoutingModel | None = None,
        max_retries: int = 3,
    ) -> None:
        if pika is None:
            raise RuntimeError("pika package is required for PikaRabbitMQTelemetryPublisher")
        if max_retries < 0:
            raise ValueError("max_retries must be greater than or equal to zero")
        self._connection = connection or RabbitMQConnectionConfig()
        self._routing = routing or RabbitRoutingModel()
        self._max_retries = max_retries
        self._seen_keys: set[str] = set()
        self._declare_topology()

    async def publish(self, envelope: BrokerEnvelope) -> PublishAttemptResult:
        key = envelope.idempotency_key
        if key in self._seen_keys:
            return PublishAttemptResult(status=PublishStatus.DEDUPLICATED, attempts=0)

        attempts = 0
        while attempts <= self._max_retries:
            attempts += 1
            try:
                await asyncio.to_thread(self._publish_once, replace(envelope, attempt=attempts))
                self._seen_keys.add(key)
                return PublishAttemptResult(status=PublishStatus.PUBLISHED, attempts=attempts)
            except Exception as exc:  # pragma: no cover - requires live broker fault paths
                if attempts > self._max_retries:
                    await asyncio.to_thread(self._publish_dead_letter, replace(envelope, attempt=attempts))
                    return PublishAttemptResult(
                        status=PublishStatus.DEAD_LETTERED,
                        attempts=attempts,
                        error=str(exc),
                    )
        raise RuntimeError("unreachable publish state")

    def _declare_topology(self) -> None:
        conn = self._open_connection()
        try:
            channel = conn.channel()
            channel.exchange_declare(exchange=self._routing.exchange, exchange_type="direct", durable=True)
            channel.queue_declare(queue=self._routing.queue, durable=True)
            channel.queue_bind(
                exchange=self._routing.exchange,
                queue=self._routing.queue,
                routing_key=self._routing.routing_key,
            )
            channel.queue_declare(queue=self._routing.dead_letter_queue, durable=True)
        finally:
            conn.close()

    def _publish_once(self, envelope: BrokerEnvelope) -> None:
        payload = json.dumps(asdict(envelope), sort_keys=True).encode("utf-8")
        conn = self._open_connection()
        try:
            channel = conn.channel()
            channel.basic_publish(
                exchange=self._routing.exchange,
                routing_key=self._routing.routing_key,
                body=payload,
                properties=pika.BasicProperties(delivery_mode=2),
            )
        finally:
            conn.close()

    def _publish_dead_letter(self, envelope: BrokerEnvelope) -> None:
        payload = json.dumps(asdict(envelope), sort_keys=True).encode("utf-8")
        conn = self._open_connection()
        try:
            channel = conn.channel()
            channel.basic_publish(
                exchange="",
                routing_key=self._routing.dead_letter_queue,
                body=payload,
                properties=pika.BasicProperties(delivery_mode=2),
            )
        finally:
            conn.close()

    def _open_connection(self) -> "pika.BlockingConnection":
        credentials = pika.PlainCredentials(self._connection.username, self._connection.password)
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
