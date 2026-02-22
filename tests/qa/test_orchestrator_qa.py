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

"""Sprint 3 QA tests for orchestrator functional behavior and security checks."""

from __future__ import annotations

import pytest

from pkg.orchestrator.audit_trail import OrchestratorAuditTrail
from pkg.orchestrator.engine import OrchestratorEngine, TaskSubmissionRequest
from pkg.orchestrator.task_scheduler import TaskScheduler
from pkg.orchestrator.telemetry_ingestion import TelemetryIngestionPipeline
from pkg.security.aaa_framework import (
    AAAService,
    AuthenticationError,
    AuthorizationError,
)


def _build_engine(
    role: str = "operator",
) -> tuple[OrchestratorEngine, TelemetryIngestionPipeline]:
    aaa = AAAService(users={"alice": "pw"}, role_bindings={"alice": {role}})
    scheduler = TaskScheduler()
    telemetry = TelemetryIngestionPipeline(batch_size=1)
    audit = OrchestratorAuditTrail()
    return OrchestratorEngine(aaa, scheduler, telemetry, audit), telemetry


def _request(required_role: str = "operator") -> TaskSubmissionRequest:
    return TaskSubmissionRequest(
        source="qa",
        tool="nmap",
        action="scan",
        payload={"target": "127.0.0.1"},
        requested_by="alice",
        required_role=required_role,
    )


def test_qa_functional_flow_task_submission_and_dequeue() -> None:
    engine, _ = _build_engine(role="operator")

    submitted_task = engine.submit_task(_request(), secret="pw")
    dequeued_task = engine.next_task()

    assert submitted_task.task_id == dequeued_task.task_id
    assert dequeued_task.action == "scan"


def test_qa_validate_telemetry_output_shape() -> None:
    engine, telemetry = _build_engine(role="operator")

    task = engine.submit_task(_request(), secret="pw")
    batch = telemetry.flush_ready()

    assert len(batch) == 1
    event = batch[0]
    assert event.event_type == "task_submitted"
    assert event.status == "success"
    assert event.attributes["task_id"] == task.task_id


def test_qa_aaa_access_verification() -> None:
    engine_auth_fail, _ = _build_engine(role="operator")
    with pytest.raises(AuthenticationError):
        engine_auth_fail.submit_task(_request(), secret="bad-secret")

    engine_authz_fail, _ = _build_engine(role="viewer")
    with pytest.raises(AuthorizationError):
        engine_authz_fail.submit_task(_request(required_role="admin"), secret="pw")
