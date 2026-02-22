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

"""Priority task scheduler for orchestrator execution planning."""

from __future__ import annotations

import heapq
from dataclasses import dataclass, field
from datetime import UTC, datetime
from itertools import count
from threading import Lock
from typing import Any

from pkg.logging.framework import emit_audit_event, get_logger

logger = get_logger("spectrastrike.orchestrator.scheduler")


@dataclass(slots=True)
class OrchestratorTask:
    """Normalized task model accepted by the orchestrator scheduler."""

    task_id: str
    source: str
    tool: str
    action: str
    payload: dict[str, Any]
    requested_by: str
    required_role: str
    priority: int = 100
    retry_count: int = 0
    max_retries: int = 3
    enqueued_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(order=True, slots=True)
class _QueueItem:
    priority: int
    sequence: int
    task: OrchestratorTask = field(compare=False)


class TaskScheduler:
    """Thread-safe in-memory task scheduler with bounded retry support."""

    def __init__(self) -> None:
        self._queue: list[_QueueItem] = []
        self._lock = Lock()
        self._sequence = count()

    def enqueue(self, task: OrchestratorTask) -> None:
        """Enqueue a task using priority and insertion order."""
        with self._lock:
            heapq.heappush(
                self._queue,
                _QueueItem(
                    priority=task.priority,
                    sequence=next(self._sequence),
                    task=task,
                ),
            )

        logger.info("Task enqueued: %s", task.task_id)
        emit_audit_event(
            action="task_enqueue",
            actor=task.requested_by,
            target=task.tool,
            status="queued",
            task_id=task.task_id,
            priority=task.priority,
        )

    def dequeue(self) -> OrchestratorTask:
        """Pop the highest-priority queued task."""
        with self._lock:
            if not self._queue:
                raise IndexError("Task queue is empty")
            item = heapq.heappop(self._queue)

        logger.info("Task dequeued: %s", item.task.task_id)
        return item.task

    def retry(self, task: OrchestratorTask, reason: str) -> bool:
        """Requeue task if retry budget exists; return retry decision."""
        if task.retry_count >= task.max_retries:
            logger.warning("Task retry denied: %s", task.task_id)
            emit_audit_event(
                action="task_retry",
                actor=task.requested_by,
                target=task.tool,
                status="denied",
                task_id=task.task_id,
                retry_count=task.retry_count,
                reason=reason,
            )
            return False

        task.retry_count += 1
        self.enqueue(task)
        logger.info("Task retried: %s (%s)", task.task_id, task.retry_count)
        emit_audit_event(
            action="task_retry",
            actor=task.requested_by,
            target=task.tool,
            status="requeued",
            task_id=task.task_id,
            retry_count=task.retry_count,
            reason=reason,
        )
        return True

    @property
    def size(self) -> int:
        """Return number of tasks in queue."""
        with self._lock:
            return len(self._queue)
