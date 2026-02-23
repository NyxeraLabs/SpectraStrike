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
