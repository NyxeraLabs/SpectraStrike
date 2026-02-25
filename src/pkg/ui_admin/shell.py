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
import json
import logging
import os
import shlex
import time
from typing import Any

from pkg.governance.legal_enforcement import assert_cli_legal_acceptance
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
    """Break-glass operator shell backed by ui-web infrastructure APIs."""

    intro = (
        f"{ANSI_COMMAND}SpectraStrike Admin TUI{ANSI_RESET}\n"
        "Type 'help' for break-glass and execution-fabric commands."
    )
    prompt = f"{ANSI_COMMAND}spectrastrike-admin>{ANSI_RESET} "

    def __init__(self, client: AdminApiClient) -> None:
        super().__init__()
        self._client = client
        self._auth: AuthSession | None = None

    def _require_auth(self) -> str | None:
        if self._auth is None:
            print(
                f"{ANSI_WARNING}authentication required: use login or demo{ANSI_RESET}"
            )
            return None
        return self._auth.access_token

    def _safe_call(self, fn: Any, *args: Any, **kwargs: Any) -> Any:
        try:
            return fn(*args, **kwargs)
        except AdminApiError as exc:
            print(f"{ANSI_ERROR}API error: {exc}{ANSI_RESET}")
            LOGGER.warning(
                "api_error action=%s error=%s", getattr(fn, "__name__", "call"), exc
            )
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
            print(
                f"{ANSI_WARNING}usage: login <username> <password> "
                f"[mfa_code]{ANSI_RESET}"
            )
            return None
        username, password = parts[0], parts[1]
        mfa_code = parts[2] if len(parts) > 2 else None

        session = self._safe_call(self._client.login, username, password, mfa_code)
        if isinstance(session, AuthSession):
            self._auth = session
            print(
                f"{ANSI_SUCCESS}authenticated{ANSI_RESET} "
                f"user={session.username} roles={','.join(session.roles)} "
                f"expires={session.expires_at}"
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
                f"user={session.username} roles={','.join(session.roles)} "
                f"expires={session.expires_at}"
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
            f"{ANSI_METADATA}user={self._auth.username} "
            f"roles={','.join(self._auth.roles)} "
            f"expires={self._auth.expires_at}{ANSI_RESET}"
        )
        return None

    def do_task(self, arg: str) -> bool | None:
        """task <tool> <target> [json_parameters]: Submit a task rapidly."""
        token = self._require_auth()
        if token is None:
            return None
        parts = shlex.split(arg)
        if len(parts) < 2:
            print(
                f"{ANSI_WARNING}usage: task <tool> <target> "
                f"[json_parameters]{ANSI_RESET}"
            )
            return None
        parameters: dict[str, Any] = {}
        if len(parts) > 2:
            try:
                loaded = json.loads(parts[2])
                if not isinstance(loaded, dict):
                    raise ValueError("parameters JSON must be an object")
                parameters = loaded
            except (json.JSONDecodeError, ValueError) as exc:
                print(f"{ANSI_WARNING}invalid parameters JSON: {exc}{ANSI_RESET}")
                return None
        response = self._safe_call(
            self._client.submit_task, token, parts[0], parts[1], parameters
        )
        if isinstance(response, dict):
            print(f"{ANSI_SUCCESS}task queued{ANSI_RESET} {response}")
        return None

    def do_manifest(self, arg: str) -> bool | None:
        """manifest <tool> <target_urn> <json_parameters>: submit a manifest task."""
        token = self._require_auth()
        if token is None:
            return None
        parts = shlex.split(arg)
        if len(parts) < 3:
            print(
                f"{ANSI_WARNING}usage: manifest <tool> <target_urn> "
                f"<json_parameters>{ANSI_RESET}"
            )
            return None
        try:
            loaded = json.loads(parts[2])
            if not isinstance(loaded, dict):
                raise ValueError("manifest parameters must be a JSON object")
        except (json.JSONDecodeError, ValueError) as exc:
            print(f"{ANSI_WARNING}invalid manifest JSON: {exc}{ANSI_RESET}")
            return None
        response = self._safe_call(
            self._client.submit_task, token, parts[0], parts[1], loaded
        )
        if isinstance(response, dict):
            print(f"{ANSI_SUCCESS}manifest queued{ANSI_RESET} {response}")
        return None

    def do_telemetry(self, arg: str) -> bool | None:
        """telemetry [limit] | telemetry watch [limit] [interval] [cycles]."""
        token = self._require_auth()
        if token is None:
            return None
        parts = shlex.split(arg)
        if parts and parts[0] in {"watch", "--watch"}:
            return self._watch_telemetry(token, parts[1:])

        limit = self._parse_limit(parts[0]) if parts else 10
        if limit is None:
            return None
        events = self._safe_call(self._client.telemetry_events, token, limit)
        self._print_telemetry_events(events)
        return None

    def do_runner(self, arg: str) -> bool | None:
        """runner kill-all [reason]: Emergency destroy active runner workloads."""
        token = self._require_auth()
        if token is None:
            return None
        parts = shlex.split(arg)
        if not parts or parts[0] != "kill-all":
            print(f"{ANSI_WARNING}usage: runner kill-all [reason]{ANSI_RESET}")
            return None
        reason = parts[1] if len(parts) > 1 else "operator_break_glass"
        result = self._safe_call(self._client.runner_kill_all, token, reason)
        if result is not None:
            print(f"{ANSI_SUCCESS}runner kill-all completed{ANSI_RESET} {result}")
        return None

    def do_queue(self, arg: str) -> bool | None:
        """queue purge [queue_name]: Emergency purge rogue broker queue."""
        token = self._require_auth()
        if token is None:
            return None
        parts = shlex.split(arg)
        if not parts or parts[0] != "purge":
            print(f"{ANSI_WARNING}usage: queue purge [queue_name]{ANSI_RESET}")
            return None
        queue_name = parts[1] if len(parts) > 1 else "telemetry.events"
        result = self._safe_call(self._client.queue_purge, token, queue_name)
        if result is not None:
            print(f"{ANSI_SUCCESS}queue purged{ANSI_RESET} {result}")
        return None

    def do_auth(self, arg: str) -> bool | None:
        """auth revoke-tenant <tenant_id>: Revoke tenant interactive access."""
        token = self._require_auth()
        if token is None:
            return None
        parts = shlex.split(arg)
        if len(parts) != 2 or parts[0] != "revoke-tenant":
            print(f"{ANSI_WARNING}usage: auth revoke-tenant <tenant_id>{ANSI_RESET}")
            return None
        result = self._safe_call(self._client.auth_revoke_tenant, token, parts[1])
        if result is not None:
            print(f"{ANSI_SUCCESS}tenant revoked{ANSI_RESET} {result}")
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

    def _parse_limit(self, raw: str) -> int | None:
        try:
            return max(1, min(50, int(raw)))
        except ValueError:
            print(f"{ANSI_WARNING}limit must be an integer{ANSI_RESET}")
            return None

    def _print_telemetry_events(self, events: list[Any] | None) -> None:
        if events is None:
            return
        for event in events:
            print(
                f"{ANSI_TELEMETRY}{event.timestamp}{ANSI_RESET} "
                f"{event.event_type} status={event.status} "
                f"actor={event.actor} target={event.target}"
            )

    def _watch_telemetry(self, token: str, args: list[str]) -> None:
        limit = 10
        interval_seconds = 2.0
        cycles = 0
        if args:
            parsed_limit = self._parse_limit(args[0])
            if parsed_limit is None:
                return
            limit = parsed_limit
        if len(args) > 1:
            try:
                interval_seconds = max(0.1, float(args[1]))
            except ValueError:
                print(f"{ANSI_WARNING}interval must be a number{ANSI_RESET}")
                return
        if len(args) > 2:
            try:
                cycles = max(0, int(args[2]))
            except ValueError:
                print(f"{ANSI_WARNING}cycles must be an integer{ANSI_RESET}")
                return

        print(
            f"{ANSI_METADATA}telemetry watch started limit={limit} "
            f"interval={interval_seconds}s "
            f"cycles={'infinite' if cycles == 0 else cycles}{ANSI_RESET}"
        )
        observed_cycles = 0
        try:
            while True:
                events = self._safe_call(self._client.telemetry_events, token, limit)
                self._print_telemetry_events(events)
                observed_cycles += 1
                if cycles and observed_cycles >= cycles:
                    break
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print(f"{ANSI_WARNING}telemetry watch interrupted{ANSI_RESET}")


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
    try:
        assert_cli_legal_acceptance()
    except RuntimeError as exc:
        print(f"{ANSI_ERROR}{exc}{ANSI_RESET}")
        print(
            f"{ANSI_WARNING}accept legal documents before using Admin TUI "
            f"(path: .spectrastrike/legal/acceptance.json){ANSI_RESET}"
        )
        return 2
    args = _parse_args()
    client = AdminApiClient(
        base_url=args.base_url, timeout_seconds=args.timeout_seconds
    )
    shell = AdminShell(client)

    if args.command:
        shell.onecmd(args.command)
        return 0

    shell.cmdloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
