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

"""Unit tests for AAA framework behavior."""

from __future__ import annotations

import pytest

from pkg.security.aaa_framework import (
    AAAService,
    AuthenticationError,
    AuthorizationError,
    MFAError,
)


class _FakePolicyAuthorizer:
    def __init__(self, *, deny: bool = False) -> None:
        self.deny = deny
        self.last_context: dict[str, object] | None = None

    def authorize_execution(
        self,
        *,
        principal: object,
        action: str,
        target: str,
        context: dict[str, object],
    ) -> None:
        del principal, action, target
        self.last_context = context
        if self.deny:
            raise PermissionError("denied")


class _FakeHardwareMFAVerifier:
    def __init__(self, valid_assertion: str) -> None:
        self.valid_assertion = valid_assertion

    def verify_assertion(
        self,
        *,
        principal_id: str,
        assertion: str,
        action: str,
        target: str,
    ) -> bool:
        del principal_id, action, target
        return assertion == self.valid_assertion


class _FakeElevationValidator:
    def __init__(self, valid_token_id: str) -> None:
        self.valid_token_id = valid_token_id

    def consume_token(self, *, token_id: str, principal_id: str, role: str) -> None:
        del principal_id, role
        if token_id != self.valid_token_id:
            raise PermissionError("invalid token")


def test_authenticate_success() -> None:
    service = AAAService(users={"alice": "pw"}, role_bindings={"alice": {"operator"}})

    principal = service.authenticate("alice", "pw")

    assert principal.principal_id == "alice"
    assert "operator" in principal.roles


def test_authenticate_failure() -> None:
    service = AAAService(users={"alice": "pw"}, role_bindings={"alice": {"operator"}})

    with pytest.raises(AuthenticationError):
        service.authenticate("alice", "wrong")


def test_authorize_and_account() -> None:
    service = AAAService(users={"alice": "pw"}, role_bindings={"alice": {"admin"}})
    principal = service.authenticate("alice", "pw")

    service.authorize(
        principal, required_role="admin", action="run_scan", target="nmap"
    )
    record = service.account(
        principal, action="run_scan", target="nmap", status="success", job_id="job-1"
    )

    assert record.action == "run_scan"
    assert record.status == "success"
    assert len(service.records) == 1
    assert service.records[0].details["job_id"] == "job-1"


def test_authorize_failure() -> None:
    service = AAAService(users={"alice": "pw"}, role_bindings={"alice": {"viewer"}})
    principal = service.authenticate("alice", "pw")

    with pytest.raises(AuthorizationError):
        service.authorize(
            principal, required_role="admin", action="run_scan", target="nmap"
        )


def test_authenticate_with_mfa_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("pkg.security.aaa_framework.time.time", lambda: 1700000000)
    service = AAAService(
        users={"alice": "pw"},
        role_bindings={"alice": {"operator"}},
        mfa_secrets={"alice": "mfa-secret"},
    )
    code = service.generate_mfa_code("alice", timestamp=1700000000)

    principal = service.authenticate("alice", "pw", mfa_code=code)

    assert principal.principal_id == "alice"


def test_authenticate_mfa_failure() -> None:
    service = AAAService(
        users={"alice": "pw"},
        role_bindings={"alice": {"operator"}},
        mfa_secrets={"alice": "mfa-secret"},
    )

    with pytest.raises(MFAError):
        service.authenticate("alice", "pw", mfa_code="000000")


def test_authenticate_lockout_after_failed_attempts() -> None:
    service = AAAService(
        users={"alice": "pw"},
        role_bindings={"alice": {"operator"}},
        max_failed_attempts=2,
        lockout_seconds=60,
    )

    with pytest.raises(AuthenticationError):
        service.authenticate("alice", "bad")
    with pytest.raises(AuthenticationError):
        service.authenticate("alice", "bad")
    with pytest.raises(AuthenticationError):
        service.authenticate("alice", "pw")


def test_authorize_delegates_to_policy_authorizer_when_context_present() -> None:
    policy = _FakePolicyAuthorizer()
    service = AAAService(
        users={"alice": "pw"},
        role_bindings={"alice": {"operator"}},
        policy_authorizer=policy,
    )
    principal = service.authenticate("alice", "pw")

    service.authorize(
        principal,
        required_role="operator",
        action="execute",
        target="runner",
        policy_context={
            "tenant_id": "tenant-a",
            "tool_sha256": "sha256:" + ("a" * 64),
            "target_urn": "urn:target:ip:10.0.0.5",
        },
    )

    assert policy.last_context is not None
    assert policy.last_context["tenant_id"] == "tenant-a"


def test_authorize_raises_when_policy_authorizer_denies() -> None:
    policy = _FakePolicyAuthorizer(deny=True)
    service = AAAService(
        users={"alice": "pw"},
        role_bindings={"alice": {"operator"}},
        policy_authorizer=policy,
    )
    principal = service.authenticate("alice", "pw")

    with pytest.raises(AuthorizationError, match="Policy denied execution"):
        service.authorize(
            principal,
            required_role="operator",
            action="execute",
            target="runner",
            policy_context={
                "tenant_id": "tenant-a",
                "tool_sha256": "sha256:" + ("a" * 64),
                "target_urn": "urn:target:ip:10.0.0.5",
            },
        )


def test_authorize_privileged_requires_hardware_mfa_assertion() -> None:
    service = AAAService(
        users={"alice": "pw"},
        role_bindings={"alice": {"admin"}},
        hardware_mfa_verifier=_FakeHardwareMFAVerifier("hw-ok"),
    )
    principal = service.authenticate("alice", "pw")

    with pytest.raises(MFAError, match="Hardware MFA assertion is required"):
        service.authorize(
            principal,
            required_role="admin",
            action="approve_ingest",
            target="armory",
            policy_context={},
        )


def test_authorize_privileged_accepts_valid_hardware_mfa_assertion() -> None:
    service = AAAService(
        users={"alice": "pw"},
        role_bindings={"alice": {"admin"}},
        hardware_mfa_verifier=_FakeHardwareMFAVerifier("hw-ok"),
    )
    principal = service.authenticate("alice", "pw")

    service.authorize(
        principal,
        required_role="admin",
        action="approve_ingest",
        target="armory",
        policy_context={"hardware_mfa_assertion": "hw-ok"},
    )


def test_authorize_privileged_requires_time_bound_elevation_token() -> None:
    service = AAAService(
        users={"alice": "pw"},
        role_bindings={"alice": {"admin"}},
        elevation_token_validator=_FakeElevationValidator("token-123"),
    )
    principal = service.authenticate("alice", "pw")

    with pytest.raises(AuthorizationError, match="Privilege elevation token is required"):
        service.authorize(
            principal,
            required_role="admin",
            action="approve_ingest",
            target="armory",
            policy_context={},
        )

    service.authorize(
        principal,
        required_role="admin",
        action="approve_ingest",
        target="armory",
        policy_context={"elevation_token_id": "token-123"},
    )
