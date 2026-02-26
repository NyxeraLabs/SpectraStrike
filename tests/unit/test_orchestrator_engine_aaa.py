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

from pkg.orchestrator.manifest import (
    NonCanonicalManifestError,
    canonical_manifest_json,
)

from pkg.orchestrator.audit_trail import OrchestratorAuditTrail
from pkg.orchestrator.engine import OrchestratorEngine, TaskSubmissionRequest
from pkg.orchestrator.task_scheduler import TaskScheduler
from pkg.orchestrator.telemetry_ingestion import TelemetryIngestionPipeline
from pkg.security.aaa_framework import (
    AAAService,
    AuthenticationError,
    AuthorizationError,
)


class _DenyPolicyAuthorizer:
    def authorize_execution(self, **_: object) -> None:
        raise PermissionError("denied")


def _engine_with_user(
    role: str = "operator",
    *,
    policy_authorizer: object | None = None,
) -> OrchestratorEngine:
    aaa = AAAService(
        users={"alice": "pw"},
        role_bindings={"alice": {role}},
        policy_authorizer=policy_authorizer,
    )
    scheduler = TaskScheduler()
    telemetry = TelemetryIngestionPipeline(batch_size=10)
    audit = OrchestratorAuditTrail()
    return OrchestratorEngine(aaa, scheduler, telemetry, audit)


def _request(
    required_role: str = "operator",
    payload: dict[str, object] | None = None,
) -> TaskSubmissionRequest:
    return TaskSubmissionRequest(
        source="api",
        tool="nmap",
        action="scan",
        payload=payload or {"target": "127.0.0.1", "tenant_id": "tenant-a"},
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


def test_submit_task_policy_authorizer_denial() -> None:
    engine = _engine_with_user(
        role="operator",
        policy_authorizer=_DenyPolicyAuthorizer(),
    )
    request = _request(
        payload={
            "tenant_id": "tenant-a",
            "tool_sha256": "sha256:" + ("a" * 64),
            "target_urn": "urn:target:ip:10.0.0.5",
        }
    )

    with pytest.raises(AuthorizationError, match="Policy denied execution"):
        engine.submit_task(request, secret="pw")


def test_validate_manifest_submission_rejects_non_canonical() -> None:
    engine = _engine_with_user()
    raw = (
        '{"tool_sha256":"sha256:'
        + ("a" * 64)
        + '","manifest_version":"1.0.0","issued_at":"2026-02-26T00:00:05+00:00",'
        + '"nonce":"nonce-0001","parameters":{"aggressive":true},"target_urn":"urn:target:ip:10.0.0.5",'
        + '"task_context":{"action":"run","correlation_id":"bc8d85ff-31f2-4b57-9adf-3ce24227de97",'
        + '"operator_id":"alice","requested_at":"2026-02-26T00:00:00+00:00","source":"api",'
        + '"task_id":"task-001","tenant_id":"tenant-a"}}'
    )

    with pytest.raises(NonCanonicalManifestError):
        engine.validate_manifest_submission(raw)


def test_validate_manifest_submission_accepts_canonical() -> None:
    engine = _engine_with_user()
    raw = canonical_manifest_json(
        {
            "issued_at": "2026-02-26T00:00:05+00:00",
            "manifest_version": "1.0.0",
            "nonce": "nonce-0001",
            "parameters": {"aggressive": True},
            "target_urn": "urn:target:ip:10.0.0.5",
            "task_context": {
                "action": "run",
                "correlation_id": "bc8d85ff-31f2-4b57-9adf-3ce24227de97",
                "operator_id": "alice",
                "requested_at": "2026-02-26T00:00:00+00:00",
                "source": "api",
                "task_id": "task-001",
                "tenant_id": "tenant-a",
            },
            "tool_sha256": "sha256:" + ("a" * 64),
        }
    )

    parsed = engine.validate_manifest_submission(raw)
    assert parsed.manifest_version == "1.0.0"
