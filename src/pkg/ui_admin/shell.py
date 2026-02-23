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

"""Interactive terminal UI for operator workflows."""

from __future__ import annotations

import argparse
import cmd
import logging
import os
import shlex
from typing import Any

from pkg.ui_admin.client import AdminApiClient, AdminApiError, AuthSession

ANSI_RESET = "\033[0m"
ANSI_COMMAND = "\033[38;5;99m"
ANSI_SUCCESS = "\033[38;5;41m"
ANSI_WARNING = "\033[38;5;214m"
ANSI_ERROR = "\033[38;5;203m"
ANSI_TELEMETRY = "\033[38;5;45m"
ANSI_METADATA = "\033[38;5;246m"

LOGGER = logging.getLogger("spectrastrike.ui_admin.shell")


def _setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


class AdminShell(cmd.Cmd):
    """Operator-focused command shell backed by ui-web APIs."""

    intro = (
        f"{ANSI_COMMAND}SpectraStrike Admin TUI{ANSI_RESET}\n"
        "Type 'help' for available commands."
    )
    prompt = f"{ANSI_COMMAND}spectrastrike-admin>{ANSI_RESET} "

    def __init__(self, client: AdminApiClient) -> None:
        super().__init__()
        self._client = client
        self._auth: AuthSession | None = None

    def _require_auth(self) -> str | None:
        if self._auth is None:
            print(f"{ANSI_WARNING}authentication required: use login or demo{ANSI_RESET}")
            return None
        return self._auth.access_token

    def _safe_call(self, fn: Any, *args: Any, **kwargs: Any) -> Any:
        try:
            return fn(*args, **kwargs)
        except AdminApiError as exc:
            print(f"{ANSI_ERROR}API error: {exc}{ANSI_RESET}")
            LOGGER.warning("api_error action=%s error=%s", getattr(fn, "__name__", "call"), exc)
            return None

    def do_health(self, arg: str) -> bool | None:
        """health: Check UI API health endpoint."""
        del arg
        response = self._safe_call(self._client.health)
        if response is not None:
            print(f"{ANSI_SUCCESS}health:{ANSI_RESET} {response}")
        return None

    def do_login(self, arg: str) -> bool | None:
        """login <username> <password> [mfa_code]: Authenticate operator session."""
        parts = shlex.split(arg)
        if len(parts) < 2:
            print(f"{ANSI_WARNING}usage: login <username> <password> [mfa_code]{ANSI_RESET}")
            return None
        username, password = parts[0], parts[1]
        mfa_code = parts[2] if len(parts) > 2 else None

        session = self._safe_call(self._client.login, username, password, mfa_code)
        if isinstance(session, AuthSession):
            self._auth = session
            print(
                f"{ANSI_SUCCESS}authenticated{ANSI_RESET} "
                f"user={session.username} roles={','.join(session.roles)} expires={session.expires_at}"
            )
        return None

    def do_demo(self, arg: str) -> bool | None:
        """demo: Authenticate using demo session endpoint."""
        del arg
        session = self._safe_call(self._client.demo_login)
        if isinstance(session, AuthSession):
            self._auth = session
            print(
                f"{ANSI_SUCCESS}demo authenticated{ANSI_RESET} "
                f"user={session.username} roles={','.join(session.roles)} expires={session.expires_at}"
            )
        return None

    def do_logout(self, arg: str) -> bool | None:
        """logout: Revoke current auth session."""
        del arg
        token = self._require_auth()
        if token is None:
            return None
        result = self._safe_call(self._client.logout, token)
        if result is None:
            self._auth = None
            print(f"{ANSI_SUCCESS}session revoked{ANSI_RESET}")
        return None

    def do_session(self, arg: str) -> bool | None:
        """session: Display active session metadata."""
        del arg
        if self._auth is None:
            print(f"{ANSI_METADATA}no active session{ANSI_RESET}")
            return None
        print(
            f"{ANSI_METADATA}user={self._auth.username} roles={','.join(self._auth.roles)} "
            f"expires={self._auth.expires_at}{ANSI_RESET}"
        )
        return None

    def do_task(self, arg: str) -> bool | None:
        """task <tool> <target>: Submit an orchestrator task."""
        token = self._require_auth()
        if token is None:
            return None
        parts = shlex.split(arg)
        if len(parts) < 2:
            print(f"{ANSI_WARNING}usage: task <tool> <target>{ANSI_RESET}")
            return None
        response = self._safe_call(self._client.submit_task, token, parts[0], parts[1], {})
        if isinstance(response, dict):
            print(f"{ANSI_SUCCESS}task queued{ANSI_RESET} {response}")
        return None

    def do_sync(self, arg: str) -> bool | None:
        """sync [actor]: Trigger manual integration sync."""
        token = self._require_auth()
        if token is None:
            return None
        actor = shlex.split(arg)[0] if arg.strip() else "ui-admin-operator"
        response = self._safe_call(self._client.manual_sync, token, actor)
        if isinstance(response, dict):
            print(f"{ANSI_SUCCESS}manual sync completed{ANSI_RESET} {response}")
        return None

    def do_telemetry(self, arg: str) -> bool | None:
        """telemetry [limit]: List recent telemetry events."""
        token = self._require_auth()
        if token is None:
            return None
        limit = 10
        if arg.strip():
            try:
                limit = max(1, min(50, int(arg.strip())))
            except ValueError:
                print(f"{ANSI_WARNING}limit must be an integer{ANSI_RESET}")
                return None
        events = self._safe_call(self._client.telemetry_events, token, limit)
        if events is None:
            return None
        for event in events:
            print(
                f"{ANSI_TELEMETRY}{event.timestamp}{ANSI_RESET} "
                f"{event.event_type} status={event.status} actor={event.actor} target={event.target}"
            )
        return None

    def do_findings(self, arg: str) -> bool | None:
        """findings [limit]: List findings summary."""
        token = self._require_auth()
        if token is None:
            return None
        limit = 10
        if arg.strip():
            try:
                limit = max(1, min(50, int(arg.strip())))
            except ValueError:
                print(f"{ANSI_WARNING}limit must be an integer{ANSI_RESET}")
                return None
        findings = self._safe_call(self._client.findings, token, limit)
        if findings is None:
            return None
        for finding in findings:
            print(
                f"{ANSI_METADATA}{finding.get('finding_id', 'unknown')}{ANSI_RESET} "
                f"severity={finding.get('severity', 'unknown')} status={finding.get('status', 'unknown')} "
                f"title={finding.get('title', 'unknown')}"
            )
        return None

    def do_quit(self, arg: str) -> bool:
        """quit: Exit the admin shell."""
        del arg
        print(f"{ANSI_SUCCESS}goodbye{ANSI_RESET}")
        return True

    def do_exit(self, arg: str) -> bool:
        """exit: Exit the admin shell."""
        return self.do_quit(arg)

    def do_EOF(self, arg: str) -> bool:
        """Handle Ctrl+D to exit shell."""
        print()
        return self.do_quit(arg)


def _parse_args() -> argparse.Namespace:
    default_base_url = os.getenv("UI_ADMIN_API_BASE_URL", "http://ui-web:3000/ui/api")
    parser = argparse.ArgumentParser(description="SpectraStrike Admin TUI")
    parser.add_argument(
        "--base-url",
        default=default_base_url,
        help=f"ui-web API base URL (default: {default_base_url})",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=8.0,
        help="HTTP timeout in seconds",
    )
    parser.add_argument(
        "--command",
        default=None,
        help="Run a single command and exit",
    )
    return parser.parse_args()


def main() -> int:
    _setup_logging()
    args = _parse_args()
    client = AdminApiClient(base_url=args.base_url, timeout_seconds=args.timeout_seconds)
    shell = AdminShell(client)

    if args.command:
        shell.onecmd(args.command)
        return 0

    shell.cmdloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
