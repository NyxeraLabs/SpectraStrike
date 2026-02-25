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

from pkg.ui_admin.client import AdminApiClient, AdminApiError


class _FakeResponse:
    def __init__(self, status_code: int, payload: dict[str, Any]) -> None:
        self.status_code = status_code
        self._payload = payload
        self.content = b"{}"
        self.text = str(payload)

    def json(self) -> dict[str, Any]:
        return self._payload


class _FakeSession:
    def __init__(self) -> None:
        self.headers: dict[str, str] = {}
        self.calls: list[dict[str, Any]] = []

    def request(self, **kwargs: Any) -> _FakeResponse:
        self.calls.append(kwargs)
        url = kwargs["url"]
        if url.endswith("/v1/auth/login"):
            return _FakeResponse(
                200,
                {
                    "access_token": "token-1",
                    "expires_at": "2026-01-01T00:00:00Z",
                    "roles": ["operator"],
                    "user": {"username": "operator"},
                },
            )
        if url.endswith("/telemetry/events?limit=2"):
            return _FakeResponse(
                200,
                {
                    "items": [
                        {
                            "event_id": "evt-1",
                            "event_type": "task_submitted",
                            "status": "success",
                            "actor": "operator",
                            "target": "nmap",
                            "timestamp": "2026-01-01T00:00:00Z",
                        }
                    ]
                },
            )
        return _FakeResponse(400, {"error": "bad_request"})


def test_login_returns_auth_session() -> None:
    client = AdminApiClient(base_url="http://ui-web:3000/ui/api")
    fake = _FakeSession()
    client._session = fake  # type: ignore[attr-defined]

    session = client.login("operator", "Secret!123")

    assert session.username == "operator"
    assert session.access_token == "token-1"
    assert fake.calls[0]["method"] == "POST"


def test_telemetry_events_maps_response() -> None:
    client = AdminApiClient(base_url="http://ui-web:3000/ui/api")
    fake = _FakeSession()
    client._session = fake  # type: ignore[attr-defined]

    events = client.telemetry_events("token-1", limit=2)

    assert len(events) == 1
    assert events[0].event_id == "evt-1"


def test_api_error_raises_admin_error() -> None:
    client = AdminApiClient(base_url="http://ui-web:3000/ui/api")
    fake = _FakeSession()
    client._session = fake  # type: ignore[attr-defined]

    with pytest.raises(AdminApiError):
        client.auth_revoke_tenant("token-1", "tenant-a")
