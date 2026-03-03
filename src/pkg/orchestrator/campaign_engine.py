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

"""Stateful campaign architecture models and lifecycle service."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from enum import Enum
from threading import Lock
from typing import Any
from uuid import uuid4


class CampaignEngineError(ValueError):
    """Raised when campaign lifecycle rules are violated."""


class CampaignStatus(str, Enum):
    """Campaign status lifecycle."""

    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class StepStatus(str, Enum):
    """Campaign step lifecycle state."""

    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"


class ExecutionStatus(str, Enum):
    """Technique execution lifecycle state."""

    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"


ALLOWED_CAMPAIGN_STATUS_TRANSITIONS: dict[CampaignStatus, set[CampaignStatus]] = {
    CampaignStatus.DRAFT: {CampaignStatus.SCHEDULED, CampaignStatus.RUNNING, CampaignStatus.CANCELED},
    CampaignStatus.SCHEDULED: {CampaignStatus.RUNNING, CampaignStatus.CANCELED},
    CampaignStatus.RUNNING: {CampaignStatus.COMPLETED, CampaignStatus.FAILED, CampaignStatus.CANCELED},
    CampaignStatus.COMPLETED: set(),
    CampaignStatus.FAILED: set(),
    CampaignStatus.CANCELED: set(),
}


def validate_lifecycle_transition(
    previous: CampaignStatus,
    current: CampaignStatus,
) -> None:
    """Validate campaign lifecycle transition."""
    allowed = ALLOWED_CAMPAIGN_STATUS_TRANSITIONS.get(previous, set())
    if current not in allowed:
        raise CampaignEngineError(
            f"invalid campaign status transition: {previous.value} -> {current.value}"
        )


@dataclass(slots=True, frozen=True)
class CampaignConfiguration:
    """Versioned campaign configuration model."""

    objective: str
    target_scope: tuple[str, ...]
    execution_window_start: datetime | None = None
    execution_window_end: datetime | None = None
    auto_start: bool = False
    max_parallel_steps: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.objective.strip():
            raise CampaignEngineError("campaign objective is required")
        if not self.target_scope:
            raise CampaignEngineError("campaign target_scope is required")
        if self.max_parallel_steps < 1:
            raise CampaignEngineError("max_parallel_steps must be >= 1")
        if (
            self.execution_window_start is not None
            and self.execution_window_end is not None
            and self.execution_window_end < self.execution_window_start
        ):
            raise CampaignEngineError("execution_window_end cannot be before execution_window_start")


@dataclass(slots=True, frozen=True)
class CampaignRecord:
    """Campaign table row."""

    campaign_id: str
    name: str
    created_by: str
    created_at: datetime
    configuration: CampaignConfiguration
    status: CampaignStatus = CampaignStatus.DRAFT
    scheduled_for: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    failure_reason: str | None = None


@dataclass(slots=True, frozen=True)
class CampaignStepRecord:
    """Campaign step table row."""

    step_id: str
    campaign_id: str
    step_order: int
    name: str
    technique_id: str
    asset_selector: tuple[str, ...]
    status: StepStatus = StepStatus.PENDING
    correlation_key: str = ""


@dataclass(slots=True, frozen=True)
class TechniqueExecutionRecord:
    """Technique execution table row."""

    execution_id: str
    campaign_id: str
    step_id: str
    technique_id: str
    asset_id: str
    correlation_group_id: str
    status: ExecutionStatus
    started_at: datetime
    stopped_at: datetime | None = None
    failure_reason: str | None = None

    def __post_init__(self) -> None:
        if self.stopped_at is not None and self.stopped_at < self.started_at:
            raise CampaignEngineError("execution stopped_at cannot be earlier than started_at")
        if self.failure_reason and self.status != ExecutionStatus.FAILED:
            raise CampaignEngineError("failure_reason is only valid for failed executions")


@dataclass(slots=True, frozen=True)
class CrossAssetCorrelation:
    """Cross-asset execution correlation output."""

    correlation_group_id: str
    campaign_id: str
    step_id: str
    asset_ids: tuple[str, ...]
    execution_ids: tuple[str, ...]


class CampaignEngine:
    """Thread-safe stateful campaign manager with lifecycle guarantees."""

    def __init__(self) -> None:
        self._campaign_table: dict[str, CampaignRecord] = {}
        self._campaign_steps_table: dict[str, CampaignStepRecord] = {}
        self._technique_execution_table: dict[str, TechniqueExecutionRecord] = {}
        self._correlation_index: dict[str, set[str]] = {}
        self._lock = Lock()

    def create_campaign(
        self,
        *,
        name: str,
        created_by: str,
        configuration: CampaignConfiguration,
    ) -> CampaignRecord:
        """Create campaign table record."""
        if not name.strip():
            raise CampaignEngineError("campaign name is required")
        if not created_by.strip():
            raise CampaignEngineError("created_by is required")
        now = datetime.now(UTC)
        campaign = CampaignRecord(
            campaign_id=f"cmp-{uuid4()}",
            name=name.strip(),
            created_by=created_by.strip(),
            created_at=now,
            configuration=configuration,
            status=CampaignStatus.DRAFT,
        )
        with self._lock:
            if any(existing.name == campaign.name for existing in self._campaign_table.values()):
                raise CampaignEngineError("campaign name already exists")
            self._campaign_table[campaign.campaign_id] = campaign
        return campaign

    def update_campaign_configuration(
        self,
        *,
        campaign_id: str,
        configuration: CampaignConfiguration,
    ) -> CampaignRecord:
        """Update campaign configuration model."""
        with self._lock:
            campaign = self._campaign_table.get(campaign_id)
            if campaign is None:
                raise CampaignEngineError("campaign not found")
            updated = replace(campaign, configuration=configuration)
            self._campaign_table[campaign_id] = updated
            return updated

    def schedule_campaign(self, *, campaign_id: str, scheduled_for: datetime) -> CampaignRecord:
        """Enable campaign scheduling support."""
        now = datetime.now(UTC)
        if scheduled_for < now:
            raise CampaignEngineError("scheduled_for cannot be in the past")
        with self._lock:
            campaign = self._campaign_table.get(campaign_id)
            if campaign is None:
                raise CampaignEngineError("campaign not found")
            updated = self._transition_campaign_status(
                campaign,
                CampaignStatus.SCHEDULED,
                scheduled_for=scheduled_for,
            )
            self._campaign_table[campaign_id] = updated
            return updated

    def set_campaign_status(
        self,
        *,
        campaign_id: str,
        status: CampaignStatus,
        failure_reason: str | None = None,
    ) -> CampaignRecord:
        """Track campaign status changes with lifecycle constraints."""
        with self._lock:
            campaign = self._campaign_table.get(campaign_id)
            if campaign is None:
                raise CampaignEngineError("campaign not found")
            updated = self._transition_campaign_status(
                campaign,
                status,
                failure_reason=failure_reason,
            )
            self._campaign_table[campaign_id] = updated
            return updated

    def add_campaign_step(
        self,
        *,
        campaign_id: str,
        step_order: int,
        name: str,
        technique_id: str,
        asset_selector: tuple[str, ...],
        correlation_key: str = "",
    ) -> CampaignStepRecord:
        """Insert campaign step table record."""
        if step_order < 1:
            raise CampaignEngineError("step_order must be >= 1")
        if not name.strip() or not technique_id.strip():
            raise CampaignEngineError("step name and technique_id are required")
        if not asset_selector:
            raise CampaignEngineError("asset_selector requires at least one asset")
        with self._lock:
            if campaign_id not in self._campaign_table:
                raise CampaignEngineError("campaign not found")
            for step in self._campaign_steps_table.values():
                if step.campaign_id == campaign_id and step.step_order == step_order:
                    raise CampaignEngineError("campaign step_order must be unique per campaign")
            step = CampaignStepRecord(
                step_id=f"stp-{uuid4()}",
                campaign_id=campaign_id,
                step_order=step_order,
                name=name.strip(),
                technique_id=technique_id.strip().upper(),
                asset_selector=tuple(asset_selector),
                correlation_key=correlation_key.strip(),
            )
            self._campaign_steps_table[step.step_id] = step
            return step

    def start_technique_execution(
        self,
        *,
        campaign_id: str,
        step_id: str,
        asset_id: str,
        correlation_group_id: str,
    ) -> TechniqueExecutionRecord:
        """Create running technique execution record with start timestamp."""
        if not asset_id.strip():
            raise CampaignEngineError("asset_id is required")
        correlation_value = correlation_group_id.strip()
        if not correlation_value:
            raise CampaignEngineError("correlation_group_id is required")
        now = datetime.now(UTC)
        with self._lock:
            campaign = self._campaign_table.get(campaign_id)
            step = self._campaign_steps_table.get(step_id)
            if campaign is None:
                raise CampaignEngineError("campaign not found")
            if step is None or step.campaign_id != campaign_id:
                raise CampaignEngineError("campaign step not found")
            if campaign.status not in {CampaignStatus.RUNNING, CampaignStatus.SCHEDULED}:
                raise CampaignEngineError("campaign must be running or scheduled to start execution")

            execution = TechniqueExecutionRecord(
                execution_id=f"tex-{uuid4()}",
                campaign_id=campaign_id,
                step_id=step_id,
                technique_id=step.technique_id,
                asset_id=asset_id.strip(),
                correlation_group_id=correlation_value,
                status=ExecutionStatus.RUNNING,
                started_at=now,
            )
            self._technique_execution_table[execution.execution_id] = execution
            self._correlation_index.setdefault(correlation_value, set()).add(execution.execution_id)
            self._campaign_steps_table[step_id] = replace(step, status=StepStatus.RUNNING)
            return execution

    def stop_technique_execution(
        self,
        *,
        execution_id: str,
        status: ExecutionStatus,
        failure_reason: str | None = None,
    ) -> TechniqueExecutionRecord:
        """Stop technique execution with completion timestamps and failure reason."""
        if status not in {ExecutionStatus.SUCCEEDED, ExecutionStatus.FAILED, ExecutionStatus.CANCELED}:
            raise CampaignEngineError("final execution status must be succeeded|failed|canceled")
        with self._lock:
            execution = self._technique_execution_table.get(execution_id)
            if execution is None:
                raise CampaignEngineError("execution not found")
            if execution.status != ExecutionStatus.RUNNING:
                raise CampaignEngineError("execution is not running")

            updated = replace(
                execution,
                status=status,
                stopped_at=datetime.now(UTC),
                failure_reason=(failure_reason or "").strip() or None,
            )
            if status != ExecutionStatus.FAILED:
                updated = replace(updated, failure_reason=None)
            self._technique_execution_table[execution_id] = updated
            step = self._campaign_steps_table[execution.step_id]
            step_status = StepStatus.SUCCEEDED if status == ExecutionStatus.SUCCEEDED else StepStatus.FAILED
            self._campaign_steps_table[step.step_id] = replace(step, status=step_status)
            return updated

    def correlate_executions(self, *, correlation_group_id: str) -> CrossAssetCorrelation:
        """Return cross-asset execution correlation group."""
        with self._lock:
            execution_ids = sorted(self._correlation_index.get(correlation_group_id, set()))
            if not execution_ids:
                raise CampaignEngineError("correlation group not found")
            executions = [self._technique_execution_table[eid] for eid in execution_ids]
            campaign_id = executions[0].campaign_id
            step_id = executions[0].step_id
            asset_ids = tuple(sorted({execution.asset_id for execution in executions}))
            return CrossAssetCorrelation(
                correlation_group_id=correlation_group_id,
                campaign_id=campaign_id,
                step_id=step_id,
                asset_ids=asset_ids,
                execution_ids=tuple(execution_ids),
            )

    def list_campaign_steps(self, *, campaign_id: str) -> list[CampaignStepRecord]:
        """List campaign steps in execution order."""
        with self._lock:
            steps = [
                step
                for step in self._campaign_steps_table.values()
                if step.campaign_id == campaign_id
            ]
        return sorted(steps, key=lambda item: item.step_order)

    def list_campaign_executions(self, *, campaign_id: str) -> list[TechniqueExecutionRecord]:
        """List technique execution records for a campaign."""
        with self._lock:
            rows = [
                execution
                for execution in self._technique_execution_table.values()
                if execution.campaign_id == campaign_id
            ]
        return sorted(rows, key=lambda item: item.started_at)

    def get_campaign(self, *, campaign_id: str) -> CampaignRecord:
        """Return campaign record by id."""
        with self._lock:
            campaign = self._campaign_table.get(campaign_id)
            if campaign is None:
                raise CampaignEngineError("campaign not found")
            return campaign

    @staticmethod
    def _transition_campaign_status(
        campaign: CampaignRecord,
        target_status: CampaignStatus,
        *,
        scheduled_for: datetime | None = None,
        failure_reason: str | None = None,
    ) -> CampaignRecord:
        if target_status == campaign.status:
            return campaign
        validate_lifecycle_transition(campaign.status, target_status)

        now = datetime.now(UTC)
        started_at = campaign.started_at
        completed_at = campaign.completed_at
        failure = None
        scheduled = campaign.scheduled_for

        if target_status == CampaignStatus.SCHEDULED:
            if scheduled_for is None:
                raise CampaignEngineError("scheduled_for is required for scheduled status")
            scheduled = scheduled_for
        if target_status == CampaignStatus.RUNNING and started_at is None:
            started_at = now
        if target_status in {CampaignStatus.COMPLETED, CampaignStatus.FAILED, CampaignStatus.CANCELED}:
            completed_at = now
        if target_status == CampaignStatus.FAILED:
            failure = (failure_reason or "").strip() or "unknown_failure"

        return replace(
            campaign,
            status=target_status,
            scheduled_for=scheduled,
            started_at=started_at,
            completed_at=completed_at,
            failure_reason=failure,
        )
