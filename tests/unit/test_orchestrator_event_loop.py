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

"""Unit tests for orchestrator async event loop runtime."""

from __future__ import annotations

import asyncio

import pytest

from pkg.orchestrator.event_loop import AsyncEventLoop


async def _sample_task(value: int) -> int:
    await asyncio.sleep(0.01)
    return value


def test_submit_requires_running_loop() -> None:
    runtime = AsyncEventLoop()

    with pytest.raises(RuntimeError):
        runtime.submit(_sample_task(1))


def test_event_loop_start_submit_stop() -> None:
    runtime = AsyncEventLoop()
    runtime.start()

    future = runtime.submit(_sample_task(7))
    assert future.result(timeout=2) == 7

    runtime.stop()
    assert runtime.is_running is False


def test_event_loop_context_manager() -> None:
    with AsyncEventLoop() as runtime:
        result = runtime.submit(_sample_task(3)).result(timeout=2)
        assert result == 3
