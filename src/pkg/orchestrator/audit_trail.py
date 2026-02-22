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

"""Orchestrator audit trail helpers for task lifecycle observability."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from threading import Lock
from typing import Any

from pkg.logging.framework import emit_audit_event, get_logger

logger = get_logger("spectrastrike.orchestrator.audit")


@dataclass(slots=True)
class AuditTrailRecord:
    """Single audit record for orchestrator lifecycle actions."""

    task_id: str
    action: str
    actor: str
    target: str
    status: str
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class OrchestratorAuditTrail:
    """In-memory audit trail that emits structured logs and audit events."""

    def __init__(self) -> None:
        self._records: list[AuditTrailRecord] = []
        self._lock = Lock()

    def task_received(
        self, task_id: str, actor: str, target: str, **details: Any
    ) -> AuditTrailRecord:
        """Record task acceptance into orchestrator."""
        return self._record(
            task_id=task_id,
            action="task_received",
            actor=actor,
            target=target,
            status="accepted",
            **details,
        )

    def task_started(
        self, task_id: str, actor: str, target: str, **details: Any
    ) -> AuditTrailRecord:
        """Record task execution start."""
        return self._record(
            task_id=task_id,
            action="task_started",
            actor=actor,
            target=target,
            status="running",
            **details,
        )

    def task_completed(
        self, task_id: str, actor: str, target: str, **details: Any
    ) -> AuditTrailRecord:
        """Record successful task completion."""
        return self._record(
            task_id=task_id,
            action="task_completed",
            actor=actor,
            target=target,
            status="success",
            **details,
        )

    def task_failed(
        self, task_id: str, actor: str, target: str, **details: Any
    ) -> AuditTrailRecord:
        """Record failed task completion."""
        return self._record(
            task_id=task_id,
            action="task_failed",
            actor=actor,
            target=target,
            status="failed",
            **details,
        )

    def _record(
        self,
        task_id: str,
        action: str,
        actor: str,
        target: str,
        status: str,
        **details: Any,
    ) -> AuditTrailRecord:
        record = AuditTrailRecord(
            task_id=task_id,
            action=action,
            actor=actor,
            target=target,
            status=status,
            details=details,
        )
        with self._lock:
            self._records.append(record)

        logger.info("Audit trail event: %s (%s)", action, task_id)
        emit_audit_event(
            action=action,
            actor=actor,
            target=target,
            status=status,
            task_id=task_id,
            **details,
        )
        return record

    @property
    def records(self) -> list[AuditTrailRecord]:
        """Return a copy of recorded audit events."""
        with self._lock:
            return list(self._records)
