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

"""Sliver CLI wrapper for normalized command telemetry emission."""

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

logger = get_logger("spectrastrike.wrappers.sliver")


class SliverExecutionError(RuntimeError):
    """Raised when Sliver command execution fails."""


@dataclass(slots=True, frozen=True)
class SliverCommandRequest:
    """Normalized Sliver command request contract."""

    target: str
    command: str
    session_id: str | None = None
    profile: str | None = None
    extra_args: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.target.strip():
            raise ValueError("target is required")
        if not self.command.strip():
            raise ValueError("command is required")


@dataclass(slots=True, frozen=True)
class SliverCommandResult:
    """Normalized Sliver command response."""

    target: str
    command: str
    status: str
    output: str
    task_id: str
    session_id: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class _CommandResult:
    returncode: int
    stdout: str
    stderr: str


Runner = Callable[[list[str], float], _CommandResult]


class SliverWrapper:
    """Wrapper around local Sliver CLI for SDK-based telemetry emission."""

    def __init__(
        self,
        *,
        cli_binary: str | None = None,
        timeout_seconds: float = 15.0,
        command_mode: str | None = None,
        runner: Runner | None = None,
    ) -> None:
        self._cli_binary = cli_binary or os.getenv("SLIVER_BINARY", "sliver-client")
        self._timeout_seconds = timeout_seconds
        self._command_mode = (
            command_mode or os.getenv("SLIVER_COMMAND_MODE", "exec")
        ).strip().lower()
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

    def build_command(self, request: SliverCommandRequest) -> list[str]:
        if self._command_mode == "version":
            return [self._cli_binary, "version"]
        command = [self._cli_binary, "exec", "--target", request.target]
        if request.session_id:
            command.extend(["--session", request.session_id])
        if request.profile:
            command.extend(["--profile", request.profile])
        command.extend(["--command", request.command, "--output", "json"])
        command.extend(request.extra_args)
        return command

    def execute(self, request: SliverCommandRequest) -> SliverCommandResult:
        command = self.build_command(request)
        logger.info("Executing sliver command: %s", " ".join(command))
        started = int(time.time())
        completed = self._runner(command, self._timeout_seconds)
        if completed.returncode != 0:
            raise SliverExecutionError(
                (completed.stderr or completed.stdout or "sliver command failed").strip()
            )
        payload = self._parse_output(completed.stdout, request, started)
        return SliverCommandResult(
            target=request.target,
            command=request.command,
            status=str(payload.get("status", "success")),
            output=str(payload.get("output", completed.stdout.strip())),
            task_id=str(payload.get("task_id", f"sliver-task-{started}")),
            session_id=str(payload.get("session_id", request.session_id or "")) or None,
            raw=payload,
        )

    def send_to_orchestrator(
        self,
        result: SliverCommandResult,
        *,
        telemetry: TelemetryIngestionPipeline,
        tenant_id: str,
        actor: str = "sliver-wrapper",
    ) -> TelemetryEvent:
        payload = build_internal_telemetry_event(
            event_type="sliver_command_completed",
            actor=actor,
            target="orchestrator",
            status=result.status,
            tenant_id=tenant_id,
            attributes={
                "target": result.target,
                "command": result.command,
                "task_id": result.task_id,
                "session_id": result.session_id,
                "output": result.output,
                "adapter": "sliver",
            },
        )
        return telemetry.ingest_payload(payload)

    def _parse_output(
        self, stdout: str, request: SliverCommandRequest, started: int
    ) -> dict[str, Any]:
        text = stdout.strip()
        if not text:
            return {
                "status": "success",
                "task_id": f"sliver-task-{started}",
                "session_id": request.session_id,
                "output": "",
            }
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return {
                "status": "success",
                "task_id": f"sliver-task-{started}",
                "session_id": request.session_id,
                "output": text,
            }
        if isinstance(parsed, dict):
            return parsed
        return {
            "status": "success",
            "task_id": f"sliver-task-{started}",
            "session_id": request.session_id,
            "output": text,
        }
