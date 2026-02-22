"""Async execution runtime for orchestrator task processing."""

from __future__ import annotations

import asyncio
import threading
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any, Coroutine


class AsyncEventLoop:
    """Run submitted coroutines on a dedicated single-worker async runtime."""

    def __init__(self) -> None:
        self._executor: ThreadPoolExecutor | None = None
        self._lock = threading.Lock()

    @property
    def is_running(self) -> bool:
        """Return whether the async runtime is active."""
        return self._executor is not None

    def start(self) -> None:
        """Start the async runtime if it is not already active."""
        with self._lock:
            if self._executor is not None:
                return
            self._executor = ThreadPoolExecutor(
                max_workers=1,
                thread_name_prefix="spectrastrike-async-runtime",
            )

    def submit(self, coro: Coroutine[Any, Any, Any]) -> Future[Any]:
        """Submit a coroutine for asynchronous execution."""
        executor = self._executor
        if executor is None:
            coro.close()
            raise RuntimeError("Async event loop is not running")

        return executor.submit(self._run_coroutine, coro)

    @staticmethod
    def _run_coroutine(coro: Coroutine[Any, Any, Any]) -> Any:
        return asyncio.run(coro)

    def stop(self, timeout: float = 5.0) -> None:
        """Stop the async runtime and wait for worker shutdown."""
        del timeout  # Preserved for API compatibility with future runtime upgrades.

        with self._lock:
            executor = self._executor
            self._executor = None

        if executor is not None:
            executor.shutdown(wait=True, cancel_futures=False)

    def __enter__(self) -> AsyncEventLoop:
        """Start runtime on context entry."""
        self.start()
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        """Stop runtime on context exit."""
        self.stop()
