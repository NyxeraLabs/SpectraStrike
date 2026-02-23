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

from pkg.ui_admin.client import AuthSession
from pkg.ui_admin.shell import AdminShell


class _ClientStub:
    def __init__(self) -> None:
        self.logout_calls: list[str] = []

    def health(self) -> dict[str, str]:
        return {"status": "ok"}

    def login(self, username: str, password: str, mfa_code: str | None = None) -> AuthSession:
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

    def telemetry_events(self, access_token: str, limit: int = 10) -> list[object]:
        del access_token, limit
        return []

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
        del access_token, tool, target, parameters
        return {"task_id": "task-1"}

    def manual_sync(self, access_token: str, actor: str) -> dict[str, str]:
        del access_token, actor
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

