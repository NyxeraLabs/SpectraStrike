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

"""Typed HTTP client for SpectraStrike Admin TUI workflows."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

import requests

LOGGER = logging.getLogger("spectrastrike.ui_admin.client")


class AdminApiError(RuntimeError):
    """Raised when the UI API returns a non-success response."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


@dataclass(slots=True)
class AuthSession:
    """Authenticated session information returned by auth endpoints."""

    access_token: str
    expires_at: str
    roles: list[str]
    username: str


@dataclass(slots=True)
class TelemetryEvent:
    """Telemetry event view model for TUI rendering."""

    event_id: str
    event_type: str
    status: str
    actor: str
    target: str
    timestamp: str


def _log_json(event: str, **fields: Any) -> None:
    payload = {"event": event, **fields}
    LOGGER.info(json.dumps(payload, sort_keys=True))


class AdminApiClient:
    """Low-level API client for ui-admin workflows."""

    def __init__(self, base_url: str, timeout_seconds: float = 8.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._session = requests.Session()
        self._session.headers.update(
            {
                "content-type": "application/json",
            }
        )

    def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        access_token: str | None = None,
    ) -> dict[str, Any]:
        url = f"{self._base_url}{path}"
        headers: dict[str, str] = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"

        try:
            response = self._session.request(
                method=method,
                url=url,
                headers=headers,
                data=json.dumps(payload) if payload is not None else None,
                timeout=self._timeout_seconds,
            )
        except requests.RequestException as exc:
            _log_json("api_transport_error", method=method, path=path, error=str(exc))
            raise AdminApiError(f"transport error for {path}: {exc}") from exc

        response_data: dict[str, Any] = {}
        if response.content:
            try:
                response_data = response.json()
            except ValueError:
                response_data = {"raw_body": response.text}

        if response.status_code >= 400:
            message = str(response_data.get("error", f"http_{response.status_code}"))
            _log_json(
                "api_error",
                method=method,
                path=path,
                status_code=response.status_code,
                error=message,
            )
            raise AdminApiError(message, status_code=response.status_code)

        _log_json("api_ok", method=method, path=path, status_code=response.status_code)
        return response_data

    def health(self) -> dict[str, Any]:
        """Return health response from UI API."""
        return self._request("GET", "/health")

    def login(
        self, username: str, password: str, mfa_code: str | None = None
    ) -> AuthSession:
        """Authenticate with username/password and optional MFA."""
        response = self._request(
            "POST",
            "/v1/auth/login",
            payload={
                "username": username,
                "password": password,
                "mfa_code": mfa_code,
            },
        )
        user = response.get("user", {})
        return AuthSession(
            access_token=str(response.get("access_token", "")),
            expires_at=str(response.get("expires_at", "")),
            roles=[str(role) for role in response.get("roles", [])],
            username=str(user.get("username", username)),
        )

    def demo_login(self) -> AuthSession:
        """Request a demo session from the UI auth API."""
        response = self._request("POST", "/v1/auth/demo", payload={})
        user = response.get("user", {})
        return AuthSession(
            access_token=str(response.get("access_token", "")),
            expires_at=str(response.get("expires_at", "")),
            roles=[str(role) for role in response.get("roles", [])],
            username=str(user.get("username", "demo_operator")),
        )

    def logout(self, access_token: str) -> None:
        """Revoke current session."""
        self._request("POST", "/v1/auth/logout", payload={}, access_token=access_token)

    def telemetry_events(
        self, access_token: str, limit: int = 10, source: str | None = None
    ) -> list[TelemetryEvent]:
        """List telemetry events with optional source filter."""
        params = [f"limit={limit}"]
        if source:
            params.append(f"source={source}")
        query = "&".join(params)
        response = self._request(
            "GET",
            f"/telemetry/events?{query}",
            access_token=access_token,
        )
        items = response.get("items", [])
        return [
            TelemetryEvent(
                event_id=str(item.get("event_id", "unknown")),
                event_type=str(item.get("event_type", "unknown")),
                status=str(item.get("status", "unknown")),
                actor=str(item.get("actor", "unknown")),
                target=str(item.get("target", "unknown")),
                timestamp=str(item.get("timestamp", "unknown")),
            )
            for item in items
        ]

    def submit_task(
        self,
        access_token: str,
        tool: str,
        target: str,
        parameters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Submit orchestrator task through ui-web BFF endpoint."""
        return self._request(
            "POST",
            "/actions/tasks",
            payload={
                "tool": tool,
                "target": target,
                "parameters": parameters or {},
            },
            access_token=access_token,
        )

    def manual_sync(self, access_token: str, actor: str) -> dict[str, Any]:
        """Trigger Metasploit manual sync endpoint."""
        return self._request(
            "POST",
            "/actions/manual-sync",
            payload={"actor": actor},
            access_token=access_token,
        )

    def runner_kill_all(self, access_token: str, reason: str) -> dict[str, Any]:
        """Execute break-glass kill-all for active runners/microVMs."""
        return self._request(
            "POST",
            "/actions/runner/kill-all",
            payload={"reason": reason},
            access_token=access_token,
        )

    def queue_purge(self, access_token: str, queue: str) -> dict[str, Any]:
        """Purge a broker queue in emergency containment scenarios."""
        return self._request(
            "POST",
            "/actions/queue/purge",
            payload={"queue": queue},
            access_token=access_token,
        )

    def auth_revoke_tenant(self, access_token: str, tenant_id: str) -> dict[str, Any]:
        """Revoke all active tenant sessions and block interactive access."""
        return self._request(
            "POST",
            "/actions/auth/revoke-tenant",
            payload={"tenant_id": tenant_id},
            access_token=access_token,
        )
