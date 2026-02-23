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

"""Unit tests for orchestrator AAA enforcement at engine level."""

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


def _engine_with_user(role: str = "operator") -> OrchestratorEngine:
    aaa = AAAService(users={"alice": "pw"}, role_bindings={"alice": {role}})
    scheduler = TaskScheduler()
    telemetry = TelemetryIngestionPipeline(batch_size=10)
    audit = OrchestratorAuditTrail()
    return OrchestratorEngine(aaa, scheduler, telemetry, audit)


def _request(required_role: str = "operator") -> TaskSubmissionRequest:
    return TaskSubmissionRequest(
        source="api",
        tool="nmap",
        action="scan",
        payload={"target": "127.0.0.1"},
        requested_by="alice",
        required_role=required_role,
    )


def test_submit_task_authentication_failure() -> None:
    engine = _engine_with_user()

    with pytest.raises(AuthenticationError):
        engine.submit_task(_request(), secret="wrong")


def test_submit_task_authorization_failure() -> None:
    engine = _engine_with_user(role="viewer")

    with pytest.raises(AuthorizationError):
        engine.submit_task(_request(required_role="admin"), secret="pw")


def test_submit_task_success_enqueues_and_records() -> None:
    engine = _engine_with_user(role="operator")

    task = engine.submit_task(_request(required_role="operator"), secret="pw")

    assert task.requested_by == "alice"
    assert engine.next_task().task_id == task.task_id
