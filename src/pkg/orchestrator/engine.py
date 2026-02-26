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

"""Core orchestrator engine with AAA enforcement on task submission."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from pkg.orchestrator.audit_trail import OrchestratorAuditTrail
from pkg.orchestrator.manifest import (
    ExecutionManifest,
    parse_and_validate_manifest_submission,
)
from pkg.orchestrator.task_scheduler import OrchestratorTask, TaskScheduler
from pkg.orchestrator.telemetry_ingestion import TelemetryIngestionPipeline
from pkg.security.aaa_framework import AAAService


@dataclass(slots=True)
class TaskSubmissionRequest:
    """Task submission payload received by the orchestrator engine."""

    source: str
    tool: str
    action: str
    payload: dict[str, Any]
    requested_by: str
    required_role: str
    priority: int = 100
    max_retries: int = 3


class OrchestratorEngine:
    """Orchestrator control plane that enforces AAA and queues tasks."""

    def __init__(
        self,
        aaa_service: AAAService,
        scheduler: TaskScheduler,
        telemetry: TelemetryIngestionPipeline,
        audit_trail: OrchestratorAuditTrail,
    ) -> None:
        self._aaa = aaa_service
        self._scheduler = scheduler
        self._telemetry = telemetry
        self._audit_trail = audit_trail

    def submit_task(
        self,
        request: TaskSubmissionRequest,
        secret: str,
    ) -> OrchestratorTask:
        """Authenticate, authorize, account, and enqueue an orchestrator task."""
        principal = self._aaa.authenticate(request.requested_by, secret)
        self._aaa.authorize(
            principal,
            required_role=request.required_role,
            action=request.action,
            target=request.tool,
            policy_context={
                "tenant_id": str(request.payload.get("tenant_id", "")),
                "tool_sha256": str(request.payload.get("tool_sha256", "")),
                "target_urn": str(request.payload.get("target_urn", "")),
            },
        )

        task = OrchestratorTask(
            task_id=str(uuid4()),
            source=request.source,
            tool=request.tool,
            action=request.action,
            payload=request.payload,
            requested_by=request.requested_by,
            required_role=request.required_role,
            priority=request.priority,
            max_retries=request.max_retries,
        )

        self._aaa.account(
            principal,
            action="task_submit",
            target=request.tool,
            status="success",
            task_id=task.task_id,
            requested_action=request.action,
        )
        self._audit_trail.task_received(
            task_id=task.task_id,
            actor=request.requested_by,
            target=request.tool,
            source=request.source,
            requested_action=request.action,
        )
        self._telemetry.ingest(
            event_type="task_submitted",
            actor=request.requested_by,
            target=request.tool,
            status="success",
            tenant_id=str(request.payload.get("tenant_id", "")),
            task_id=task.task_id,
            action=request.action,
        )
        self._scheduler.enqueue(task)
        return task

    def next_task(self) -> OrchestratorTask:
        """Return next scheduled task for execution."""
        return self._scheduler.dequeue()

    def validate_manifest_submission(self, raw_manifest: str) -> ExecutionManifest:
        """Validate and parse submitted manifest JSON with canonical checks."""
        return parse_and_validate_manifest_submission(raw_manifest)
