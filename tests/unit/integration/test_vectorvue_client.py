"""Unit tests for VectorVue integration client."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest
from requests.exceptions import Timeout

from pkg.integration.vectorvue.client import VectorVueClient
from pkg.integration.vectorvue.config import VectorVueConfig
from pkg.integration.vectorvue.exceptions import (
    VectorVueAPIError,
    VectorVueConfigError,
    VectorVueSerializationError,
    VectorVueTransportError,
)


@dataclass
class FakeResponse:
    status_code: int
    payload: dict[str, Any] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)

    def json(self) -> dict[str, Any]:
        return self.payload


class FakeSession:
    def __init__(self, queued: list[Any]) -> None:
        self._queued = queued
        self.calls: list[dict[str, Any]] = []

    def request(self, **kwargs: Any) -> FakeResponse:
        self.calls.append(kwargs)
        if not self._queued:
            raise AssertionError("no queued fake responses available")
        item = self._queued.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def _config_with_creds(**overrides: Any) -> VectorVueConfig:
    base = {
        "base_url": "https://127.0.0.1",
        "username": "acme_viewer",
        "password": "AcmeView3r!",
        "tenant_id": "10000000-0000-0000-0000-000000000001",
        "timeout_seconds": 0.01,
        "backoff_seconds": 0,
    }
    base.update(overrides)
    return VectorVueConfig(**base)


def test_config_requires_https_by_default() -> None:
    with pytest.raises(VectorVueConfigError):
        _config_with_creds(base_url="http://127.0.0.1")


def test_config_accepts_token_without_credentials() -> None:
    cfg = VectorVueConfig(base_url="https://127.0.0.1", token="jwt")
    assert cfg.token == "jwt"


def test_login_fetches_and_caches_token() -> None:
    session = FakeSession(
        [
            FakeResponse(
                200,
                {
                    "request_id": "req-login",
                    "status": "accepted",
                    "data": {"access_token": "token-1"},
                    "errors": [],
                },
            )
        ]
    )
    client = VectorVueClient(_config_with_creds(), session=session)

    token_a = client.login()
    token_b = client.login()

    assert token_a == "token-1"
    assert token_b == "token-1"
    assert len(session.calls) == 1


def test_login_accepts_top_level_access_token() -> None:
    session = FakeSession(
        [
            FakeResponse(
                200,
                {
                    "access_token": "token-top-level",
                    "token_type": "bearer",
                },
            )
        ]
    )
    client = VectorVueClient(_config_with_creds(), session=session)

    token = client.login()

    assert token == "token-top-level"


def test_send_event_sets_idempotency_key() -> None:
    session = FakeSession(
        [
            FakeResponse(200, {"request_id": "r", "status": "accepted", "data": {}, "errors": []})
        ]
    )
    client = VectorVueClient(_config_with_creds(token="jwt"), session=session)

    client.send_event({"event_type": "PROCESS_ANOMALY"}, idempotency_key="idem-1")

    headers = session.calls[0]["headers"]
    assert headers["Idempotency-Key"] == "idem-1"
    assert headers["Authorization"] == "Bearer jwt"


def test_signing_headers_are_added_when_secret_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("pkg.integration.vectorvue.client.time.time", lambda: 1700000000)
    session = FakeSession(
        [
            FakeResponse(200, {"request_id": "r", "status": "accepted", "data": {}, "errors": []})
        ]
    )
    client = VectorVueClient(
        _config_with_creds(token="jwt", signature_secret="signing-secret"),
        session=session,
    )

    client.send_event({"event_type": "PROCESS_ANOMALY"})

    headers = session.calls[0]["headers"]
    assert headers["X-Timestamp"] == "1700000000"
    assert "X-Signature" in headers


def test_retries_on_retryable_status(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("pkg.integration.vectorvue.client.time.sleep", lambda _: None)
    session = FakeSession(
        [
            FakeResponse(503, {"request_id": "r1", "status": "failed", "errors": []}),
            FakeResponse(200, {"request_id": "r2", "status": "accepted", "data": {}, "errors": []}),
        ]
    )
    client = VectorVueClient(_config_with_creds(token="jwt", max_retries=2), session=session)

    envelope = client.send_event({"event_type": "PROCESS_ANOMALY"})

    assert envelope.request_id == "r2"
    assert len(session.calls) == 2


def test_retries_on_timeout_then_raises_when_exhausted(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("pkg.integration.vectorvue.client.time.sleep", lambda _: None)
    session = FakeSession([Timeout("t1"), Timeout("t2")])
    client = VectorVueClient(_config_with_creds(token="jwt", max_retries=1), session=session)

    with pytest.raises(VectorVueTransportError):
        client.send_event({"event_type": "PROCESS_ANOMALY"})

    assert len(session.calls) == 2


def test_batch_size_guard() -> None:
    session = FakeSession([])
    client = VectorVueClient(_config_with_creds(token="jwt", max_batch_size=1), session=session)

    with pytest.raises(VectorVueSerializationError):
        client.send_events_batch([
            {"event_type": "A"},
            {"event_type": "B"},
        ])


def test_idempotency_conflict_maps_to_typed_api_error() -> None:
    session = FakeSession(
        [
            FakeResponse(
                409,
                {
                    "request_id": "r-409",
                    "status": "failed",
                    "errors": [
                        {
                            "error_code": "idempotency_conflict",
                            "error_message": "Key used with different payload",
                        }
                    ],
                },
            )
        ]
    )
    client = VectorVueClient(_config_with_creds(token="jwt"), session=session)

    with pytest.raises(VectorVueAPIError) as err:
        client.send_event({"event_type": "A"}, idempotency_key="dup")

    assert err.value.status_code == 409
    assert err.value.error_code == "idempotency_conflict"


def test_validation_error_uses_code_and_message_fields() -> None:
    session = FakeSession(
        [
            FakeResponse(
                422,
                {
                    "request_id": "r-422",
                    "status": "failed",
                    "errors": [
                        {
                            "code": "validation_failed",
                            "message": "Payload validation failed",
                        }
                    ],
                },
            )
        ]
    )
    client = VectorVueClient(_config_with_creds(token="jwt"), session=session)

    with pytest.raises(VectorVueAPIError) as err:
        client.send_event({"event_type": "A"})

    assert err.value.status_code == 422
    assert err.value.error_code == "validation_failed"
    assert str(err.value) == "Payload validation failed"
