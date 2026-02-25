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

from __future__ import annotations

from typing import Any

import pytest

from pkg.ui_admin.client import AuthSession, TelemetryEvent
from pkg.ui_admin.shell import AdminShell


class _ClientStub:
    def __init__(self) -> None:
        self.logout_calls: list[str] = []
        self.submitted_tasks: list[dict[str, Any]] = []
        self.runner_reasons: list[str] = []
        self.purged_queues: list[str] = []
        self.revoked_tenants: list[str] = []
        self.telemetry_calls: list[int] = []

    def health(self) -> dict[str, str]:
        return {"status": "ok"}

    def login(
        self, username: str, password: str, mfa_code: str | None = None
    ) -> AuthSession:
        del password, mfa_code
        return AuthSession(
            access_token="token-1",
            expires_at="2026-01-01T00:00:00Z",
            roles=["operator"],
            username=username,
        )

    def demo_login(self) -> AuthSession:
        return AuthSession(
            access_token="token-demo",
            expires_at="2026-01-01T00:00:00Z",
            roles=["operator"],
            username="demo_operator",
        )

    def logout(self, access_token: str) -> None:
        self.logout_calls.append(access_token)

    def telemetry_events(
        self, access_token: str, limit: int = 10
    ) -> list[TelemetryEvent]:
        del access_token
        self.telemetry_calls.append(limit)
        return [
            TelemetryEvent(
                event_id=f"evt-{len(self.telemetry_calls)}",
                event_type="task_submitted",
                status="success",
                actor="operator",
                target="nmap",
                timestamp="2026-01-01T00:00:00Z",
            )
        ]

    def submit_task(
        self,
        access_token: str,
        tool: str,
        target: str,
        parameters: dict[str, object] | None = None,
    ) -> dict[str, str]:
        self.submitted_tasks.append(
            {
                "access_token": access_token,
                "tool": tool,
                "target": target,
                "parameters": parameters,
            }
        )
        return {"task_id": "task-1"}

    def runner_kill_all(self, access_token: str, reason: str) -> dict[str, str]:
        del access_token
        self.runner_reasons.append(reason)
        return {"status": "completed"}

    def queue_purge(self, access_token: str, queue: str) -> dict[str, str]:
        del access_token
        self.purged_queues.append(queue)
        return {"status": "completed"}

    def auth_revoke_tenant(self, access_token: str, tenant_id: str) -> dict[str, str]:
        del access_token
        self.revoked_tenants.append(tenant_id)
        return {"status": "completed"}


def test_login_and_logout_commands() -> None:
    client = _ClientStub()
    shell = AdminShell(client)  # type: ignore[arg-type]

    shell.onecmd("login operator Secret!123")
    assert shell._auth is not None
    assert shell._auth.username == "operator"

    shell.onecmd("logout")
    assert shell._auth is None
    assert client.logout_calls == ["token-1"]


def test_demo_command_creates_session() -> None:
    client = _ClientStub()
    shell = AdminShell(client)  # type: ignore[arg-type]

    shell.onecmd("demo")
    assert shell._auth is not None
    assert shell._auth.username == "demo_operator"


def test_task_workflow_submits_command_when_authenticated(
    capsys: pytest.CaptureFixture[str],
) -> None:
    client = _ClientStub()
    shell = AdminShell(client)  # type: ignore[arg-type]

    shell.onecmd("login operator Secret!123")
    shell.onecmd("task nmap 10.0.9.0/24")

    assert len(client.submitted_tasks) == 1
    assert client.submitted_tasks[0]["tool"] == "nmap"
    assert client.submitted_tasks[0]["target"] == "10.0.9.0/24"
    output = capsys.readouterr().out
    assert "task queued" in output


def test_task_requires_authentication(capsys: pytest.CaptureFixture[str]) -> None:
    client = _ClientStub()
    shell = AdminShell(client)  # type: ignore[arg-type]

    shell.onecmd("task nmap 10.0.9.0/24")

    assert client.submitted_tasks == []
    output = capsys.readouterr().out
    assert "authentication required" in output


def test_break_glass_workflows_execute_expected_actions() -> None:
    client = _ClientStub()
    shell = AdminShell(client)  # type: ignore[arg-type]

    shell.onecmd("demo")
    shell.onecmd("runner kill-all")
    shell.onecmd("queue purge")
    shell.onecmd("auth revoke-tenant tenant-a")

    assert client.runner_reasons == ["operator_break_glass"]
    assert client.purged_queues == ["telemetry.events"]
    assert client.revoked_tenants == ["tenant-a"]


def test_manifest_submission_accepts_json_parameters() -> None:
    client = _ClientStub()
    shell = AdminShell(client)  # type: ignore[arg-type]

    shell.onecmd("demo")
    shell.onecmd("manifest nmap urn:target:ip:10.0.0.5 '{\"ports\":[443]}'")

    assert len(client.submitted_tasks) == 1
    assert client.submitted_tasks[0]["target"] == "urn:target:ip:10.0.0.5"


def test_telemetry_command_lists_and_clamps_limit() -> None:
    client = _ClientStub()
    shell = AdminShell(client)  # type: ignore[arg-type]

    shell.onecmd("demo")
    shell.onecmd("telemetry 100")

    assert client.telemetry_calls == [50]


def test_telemetry_watch_runs_fixed_cycles(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _ClientStub()
    shell = AdminShell(client)  # type: ignore[arg-type]

    shell.onecmd("demo")
    monkeypatch.setattr("pkg.ui_admin.shell.time.sleep", lambda _: None)
    shell.onecmd("telemetry watch 2 0.1 3")

    assert client.telemetry_calls == [2, 2, 2]
