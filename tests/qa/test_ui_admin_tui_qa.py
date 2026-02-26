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

import pytest

from pkg.ui_admin.client import AuthSession, TelemetryEvent
from pkg.ui_admin.shell import AdminShell


class _QaClientStub:
    def __init__(self) -> None:
        self.task_calls = 0
        self.sync_calls = 0
        self.telemetry_calls = 0

    def health(self) -> dict[str, str]:
        return {"status": "ok"}

    def demo_login(self) -> AuthSession:
        return AuthSession(
            access_token="qa-token",
            expires_at="2026-01-01T00:00:00Z",
            roles=["operator"],
            username="qa_operator",
        )

    def telemetry_events(
        self, access_token: str, limit: int = 10
    ) -> list[TelemetryEvent]:
        del access_token, limit
        self.telemetry_calls += 1
        return [
            TelemetryEvent(
                event_id="evt-qa-1",
                event_type="qa_event",
                status="success",
                actor="qa_operator",
                target="qa_target",
                timestamp="2026-01-01T00:00:00Z",
            )
        ]

    def submit_task(
        self,
        access_token: str,
        tool: str,
        target: str,
        parameters: dict[str, object] | None = None,
        tenant_id: str | None = None,
    ) -> dict[str, str]:
        del access_token, tool, target, parameters, tenant_id
        self.task_calls += 1
        return {"task_id": "qa-task"}

    def manual_sync(
        self, access_token: str, actor: str, tenant_id: str | None = None
    ) -> dict[str, str]:
        del access_token, actor, tenant_id
        self.sync_calls += 1
        return {"status": "ok"}


def test_admin_tui_command_workflows_smoke(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _QaClientStub()
    shell = AdminShell(client)  # type: ignore[arg-type]

    shell.onecmd("demo")
    shell.onecmd("task nmap 10.0.9.0/24")
    shell.onecmd("sync")
    monkeypatch.setattr("pkg.ui_admin.shell.time.sleep", lambda _: None)
    shell.onecmd("telemetry watch 2 0.1 2")

    assert client.task_calls == 1
    assert client.sync_calls == 1
    assert client.telemetry_calls == 2
