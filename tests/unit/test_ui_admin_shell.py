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
        self.sync_actors: list[str] = []
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

    def findings(self, access_token: str, limit: int = 10) -> list[dict[str, str]]:
        del access_token, limit
        return []

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

    def manual_sync(self, access_token: str, actor: str) -> dict[str, str]:
        del access_token
        self.sync_actors.append(actor)
        return {"status": "ok"}


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


def test_sync_workflow_uses_default_and_explicit_actor() -> None:
    client = _ClientStub()
    shell = AdminShell(client)  # type: ignore[arg-type]

    shell.onecmd("demo")
    shell.onecmd("sync")
    shell.onecmd("sync operator-jmicoli")

    assert client.sync_actors == ["ui-admin-operator", "operator-jmicoli"]


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
