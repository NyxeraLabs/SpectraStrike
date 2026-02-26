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

"""Sprint 17 Zero-Trust QA checks for OPA denials and runner containment."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest

from pkg.orchestrator.opa import OPAConfig, OPAAAAPolicyAdapter, OPAAuthorizationError
from pkg.runner.network_policy import CiliumPolicyManager
from pkg.security.aaa_framework import Principal


@dataclass
class _FakeResponse:
    status_code: int
    payload: dict[str, Any] = field(default_factory=dict)

    def json(self) -> dict[str, Any]:
        return self.payload


class _FakeSession:
    def __init__(self, queued: list[_FakeResponse]) -> None:
        self._queued = queued
        self.calls: list[dict[str, Any]] = []

    def post(self, url: str, json: dict[str, Any], timeout: float) -> _FakeResponse:
        self.calls.append({"url": url, "json": json, "timeout": timeout})
        if not self._queued:
            raise AssertionError("no queued fake response")
        return self._queued.pop(0)


def _adapter_with_session(session: _FakeSession) -> OPAAAAPolicyAdapter:
    from pkg.orchestrator.opa import OPAExecutionAuthorizer

    return OPAAAAPolicyAdapter(
        OPAExecutionAuthorizer(
            OPAConfig(url="http://opa:8181", timeout_seconds=1.0),
            session=session,
        )
    )


def test_s17_qa_opa_denies_unauthorized_tool_execution() -> None:
    session = _FakeSession(
        [
            _FakeResponse(200, {"result": True}),
            _FakeResponse(200, {"result": False}),
        ]
    )
    adapter = _adapter_with_session(session)

    with pytest.raises(OPAAuthorizationError, match="execution not authorized"):
        adapter.authorize_execution(
            principal=Principal(principal_id="operator-a", roles={"operator"}),
            action="execute",
            target="runner",
            context={
                "tenant_id": "tenant-a",
                "tool_sha256": "sha256:" + ("f" * 64),
                "target_urn": "urn:target:ip:10.0.0.5",
            },
        )

    allow_payload = session.calls[1]["json"]["input"]
    assert allow_payload["tool_sha256"] == "sha256:" + ("f" * 64)


def test_s17_qa_opa_denies_unauthorized_target_urn_for_authorized_tool() -> None:
    session = _FakeSession(
        [
            _FakeResponse(200, {"result": True}),
            _FakeResponse(200, {"result": False}),
        ]
    )
    adapter = _adapter_with_session(session)

    with pytest.raises(OPAAuthorizationError, match="execution not authorized"):
        adapter.authorize_execution(
            principal=Principal(principal_id="operator-a", roles={"operator"}),
            action="execute",
            target="runner",
            context={
                "tenant_id": "tenant-a",
                "tool_sha256": "sha256:" + ("a" * 64),
                "target_urn": "urn:target:ip:172.16.99.50",
            },
        )

    allow_payload = session.calls[1]["json"]["input"]
    assert allow_payload["tool_sha256"] == "sha256:" + ("a" * 64)
    assert allow_payload["target_urn"] == "urn:target:ip:172.16.99.50"


def test_s17_qa_runner_policy_contains_deny_by_default_containment_controls() -> None:
    manager = CiliumPolicyManager(namespace="spectra")
    doc = manager.build_policy_document(
        task_id="task-s17-001",
        tenant_id="tenant-a",
        target_urn="urn:target:ip:10.0.0.5",
    )

    # Single explicit egress allowlist target.
    assert doc["spec"]["egress"] == [{"toCIDRSet": [{"cidr": "10.0.0.5/32"}]}]
    # Explicit lateral movement blocks.
    assert doc["spec"]["egressDeny"][1]["toEntities"] == ["cluster", "host", "remote-node"]
    deny_cidrs = {item["cidr"] for item in doc["spec"]["egressDeny"][2]["toCIDRSet"]}
    assert {"127.0.0.0/8", "169.254.0.0/16", "::1/128", "fe80::/10"} <= deny_cidrs
    # Cross-tenant east/west ingress denied.
    ingress_expr = doc["spec"]["ingressDeny"][0]["fromEndpoints"][0]["matchExpressions"][0]
    assert ingress_expr["key"] == "spectrastrike.io/tenant-id"
    assert ingress_expr["operator"] == "NotIn"
    assert ingress_expr["values"] == ["tenant-a"]
