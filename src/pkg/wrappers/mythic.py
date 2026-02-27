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

"""Mythic CLI wrapper for normalized command telemetry emission."""

from __future__ import annotations

import json
import os
import subprocess
import time
from dataclasses import dataclass, field
from typing import Any, Callable

from pkg.logging.framework import get_logger
from pkg.orchestrator.telemetry_ingestion import (
    TelemetryEvent,
    TelemetryIngestionPipeline,
)
from pkg.telemetry.sdk import build_internal_telemetry_event

logger = get_logger("spectrastrike.wrappers.mythic")


class MythicExecutionError(RuntimeError):
    """Raised when Mythic command execution fails."""


@dataclass(slots=True, frozen=True)
class MythicTaskRequest:
    """Normalized Mythic task request contract."""

    target: str
    operation: str
    command: str
    callback_id: str | None = None
    extra_args: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.target.strip():
            raise ValueError("target is required")
        if not self.operation.strip():
            raise ValueError("operation is required")
        if not self.command.strip():
            raise ValueError("command is required")


@dataclass(slots=True, frozen=True)
class MythicTaskResult:
    """Normalized Mythic task response."""

    target: str
    operation: str
    command: str
    status: str
    output: str
    task_id: str
    callback_id: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class _CommandResult:
    returncode: int
    stdout: str
    stderr: str


Runner = Callable[[list[str], float], _CommandResult]


class MythicWrapper:
    """Wrapper around local Mythic CLI for SDK-based telemetry emission."""

    def __init__(
        self,
        *,
        cli_binary: str | None = None,
        timeout_seconds: float = 15.0,
        runner: Runner | None = None,
    ) -> None:
        self._cli_binary = cli_binary or os.getenv("MYTHIC_BINARY", "mythic-cli")
        self._timeout_seconds = timeout_seconds
        self._runner = runner or self._run_command

    @staticmethod
    def _run_command(command: list[str], timeout_seconds: float) -> _CommandResult:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
        return _CommandResult(
            returncode=completed.returncode,
            stdout=completed.stdout or "",
            stderr=completed.stderr or "",
        )

    def build_command(self, request: MythicTaskRequest) -> list[str]:
        command = [
            self._cli_binary,
            "task",
            "create",
            "--target",
            request.target,
            "--operation",
            request.operation,
            "--command",
            request.command,
            "--output",
            "json",
        ]
        if request.callback_id:
            command.extend(["--callback", request.callback_id])
        command.extend(request.extra_args)
        return command

    def execute(self, request: MythicTaskRequest) -> MythicTaskResult:
        command = self.build_command(request)
        logger.info("Executing mythic task: %s", " ".join(command))
        started = int(time.time())
        completed = self._runner(command, self._timeout_seconds)
        if completed.returncode != 0:
            raise MythicExecutionError(
                (completed.stderr or completed.stdout or "mythic command failed").strip()
            )
        payload = self._parse_output(completed.stdout, request, started)
        return MythicTaskResult(
            target=request.target,
            operation=request.operation,
            command=request.command,
            status=str(payload.get("status", "success")),
            output=str(payload.get("output", completed.stdout.strip())),
            task_id=str(payload.get("task_id", f"mythic-task-{started}")),
            callback_id=str(payload.get("callback_id", request.callback_id or "")) or None,
            raw=payload,
        )

    def send_to_orchestrator(
        self,
        result: MythicTaskResult,
        *,
        telemetry: TelemetryIngestionPipeline,
        tenant_id: str,
        actor: str = "mythic-wrapper",
    ) -> TelemetryEvent:
        payload = build_internal_telemetry_event(
            event_type="mythic_task_completed",
            actor=actor,
            target="orchestrator",
            status=result.status,
            tenant_id=tenant_id,
            attributes={
                "target": result.target,
                "operation": result.operation,
                "command": result.command,
                "task_id": result.task_id,
                "callback_id": result.callback_id,
                "output": result.output,
                "adapter": "mythic",
            },
        )
        return telemetry.ingest_payload(payload)

    def _parse_output(
        self, stdout: str, request: MythicTaskRequest, started: int
    ) -> dict[str, Any]:
        text = stdout.strip()
        if not text:
            return {
                "status": "success",
                "task_id": f"mythic-task-{started}",
                "callback_id": request.callback_id,
                "output": "",
            }
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return {
                "status": "success",
                "task_id": f"mythic-task-{started}",
                "callback_id": request.callback_id,
                "output": text,
            }
        if isinstance(parsed, dict):
            return parsed
        return {
            "status": "success",
            "task_id": f"mythic-task-{started}",
            "callback_id": request.callback_id,
            "output": text,
        }
