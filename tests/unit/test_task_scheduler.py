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

"""Unit tests for orchestrator task scheduler behavior."""

from __future__ import annotations

import pytest

from pkg.orchestrator.task_scheduler import OrchestratorTask, TaskScheduler


def _task(task_id: str, priority: int) -> OrchestratorTask:
    return OrchestratorTask(
        task_id=task_id,
        source="api",
        tool="nmap",
        action="scan",
        payload={"target": "127.0.0.1"},
        requested_by="alice",
        required_role="operator",
        priority=priority,
    )


def test_scheduler_dequeues_highest_priority_first() -> None:
    scheduler = TaskScheduler()
    low = _task("low", priority=200)
    high = _task("high", priority=10)

    scheduler.enqueue(low)
    scheduler.enqueue(high)

    assert scheduler.dequeue().task_id == "high"
    assert scheduler.dequeue().task_id == "low"


def test_scheduler_preserves_fifo_for_same_priority() -> None:
    scheduler = TaskScheduler()
    first = _task("first", priority=50)
    second = _task("second", priority=50)

    scheduler.enqueue(first)
    scheduler.enqueue(second)

    assert scheduler.dequeue().task_id == "first"
    assert scheduler.dequeue().task_id == "second"


def test_scheduler_retry_budget() -> None:
    scheduler = TaskScheduler()
    task = _task("retry", priority=20)
    task.max_retries = 1

    assert scheduler.retry(task, reason="transient_error") is True
    assert task.retry_count == 1
    assert scheduler.retry(task, reason="still_failing") is False


def test_dequeue_empty_queue_raises() -> None:
    scheduler = TaskScheduler()

    with pytest.raises(IndexError):
        scheduler.dequeue()
