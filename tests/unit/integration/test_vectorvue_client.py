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

"""Unit tests for VectorVue integration client."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
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


class _FakeSock:
    def __init__(self, cert: bytes) -> None:
        self._cert = cert

    def getpeercert(self, binary_form: bool = False) -> bytes | dict[str, Any]:
        if binary_form:
            return self._cert
        return {}


class _FakeConn:
    def __init__(self, cert: bytes) -> None:
        self.sock = _FakeSock(cert)


class _FakeRaw:
    def __init__(self, cert: bytes) -> None:
        self.connection = _FakeConn(cert)


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
            FakeResponse(
                200, {"request_id": "r", "status": "accepted", "data": {}, "errors": []}
            )
        ]
    )
    client = VectorVueClient(_config_with_creds(token="jwt"), session=session)

    client.send_event({"event_type": "PROCESS_ANOMALY"}, idempotency_key="idem-1")

    headers = session.calls[0]["headers"]
    assert headers["Idempotency-Key"] == "idem-1"
    assert headers["Authorization"] == "Bearer jwt"


def test_send_execution_graph_metadata_uses_cognitive_endpoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = FakeSession(
        [
            FakeResponse(
                202,
                {"request_id": "graph-1", "status": "accepted", "data": {}, "errors": []},
            )
        ]
    )
    client = VectorVueClient(_config_with_creds(token="jwt"), session=session)
    monkeypatch.setattr(
        client,
        "_build_federation_headers",
        lambda **_: {
            "X-Service-Identity": "spectrastrike-producer",
            "X-Client-Cert-Sha256": "a" * 64,
            "X-Telemetry-Timestamp": "1760000000",
            "X-Telemetry-Nonce": "nonce-graph",
            "X-Telemetry-Signature": "sig",
        },
    )

    envelope = client.send_execution_graph_metadata(
        {
            "graph_id": "g-001",
            "tenant_id": "10000000-0000-0000-0000-000000000001",
            "execution_fingerprint": "f" * 64,
            "operator_id": "op-001",
            "nodes": [{"id": "n1", "type": "task"}],
            "edges": [],
        }
    )

    assert envelope.ok
    assert session.calls[0]["url"].endswith("/internal/v1/cognitive/execution-graph")
    assert "Authorization" not in session.calls[0]["headers"]


def test_fetch_feedback_adjustments_uses_expected_query(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = FakeSession(
        [
            FakeResponse(
                200,
                {
                    "request_id": "fb-1",
                    "status": "accepted",
                    "data": [
                        {
                            "tenant_id": "10000000-0000-0000-0000-000000000001",
                            "execution_fingerprint": "e" * 64,
                            "target_urn": "urn:target:ip:10.0.0.5",
                            "action": "tighten",
                            "confidence": 0.91,
                            "rationale": "risk cluster",
                            "timestamp": 1760000000,
                            "schema_version": "feedback.adjustment.v1",
                        }
                    ],
                    "errors": [],
                    "signed_at": 1760000001,
                    "nonce": "feedback-nonce-1",
                    "signature": "placeholder",
                },
            )
        ]
    )
    client = VectorVueClient(
        _config_with_creds(token="jwt", signature_secret="feedback-secret"),
        session=session,
    )
    monkeypatch.setattr(
        client,
        "_build_federation_headers",
        lambda **_: {
            "X-Service-Identity": "spectrastrike-producer",
            "X-Client-Cert-Sha256": "a" * 64,
            "X-Telemetry-Timestamp": "1760000000",
            "X-Telemetry-Nonce": "nonce-feedback",
            "X-Telemetry-Signature": "sig",
        },
    )
    monkeypatch.setattr(client, "_enforce_feedback_replay", lambda **_: None)
    monkeypatch.setattr(client, "_verify_feedback_signature", lambda **_: None)

    envelope = client.fetch_feedback_adjustments(
        "10000000-0000-0000-0000-000000000001",
        limit=25,
    )

    assert envelope.ok
    assert session.calls[0]["url"].endswith(
        "/internal/v1/cognitive/feedback/adjustments/query"
    )
    assert "Authorization" not in session.calls[0]["headers"]


def test_fetch_feedback_adjustments_rejects_invalid_input() -> None:
    session = FakeSession([])
    client = VectorVueClient(_config_with_creds(token="jwt"), session=session)

    with pytest.raises(VectorVueSerializationError, match="tenant_id is required"):
        client.fetch_feedback_adjustments("", limit=10)
    with pytest.raises(VectorVueSerializationError, match="limit must be greater than zero"):
        client.fetch_feedback_adjustments("tenant-a", limit=0)


def test_fetch_feedback_adjustments_rejects_unsigned_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = FakeSession(
        [
            FakeResponse(
                200,
                {
                    "request_id": "fb-unsigned",
                    "status": "accepted",
                    "data": [],
                    "errors": [],
                },
            )
        ]
    )
    client = VectorVueClient(
        _config_with_creds(token="jwt", signature_secret="feedback-secret"),
        session=session,
    )
    monkeypatch.setattr(
        client,
        "_build_federation_headers",
        lambda **_: {
            "X-Service-Identity": "spectrastrike-producer",
            "X-Client-Cert-Sha256": "a" * 64,
            "X-Telemetry-Timestamp": "1760000000",
            "X-Telemetry-Nonce": "nonce-feedback",
            "X-Telemetry-Signature": "sig",
        },
    )
    with pytest.raises(VectorVueSerializationError, match="signed feedback response"):
        client.fetch_feedback_adjustments(
            "10000000-0000-0000-0000-000000000001",
            limit=10,
        )


def test_send_federated_telemetry_uses_internal_gateway_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("VECTORVUE_FEDERATION_SIGNING_KEY_PATH", "/tmp/fed-sign.key")
    monkeypatch.setenv("VECTORVUE_FEDERATION_CLIENT_CERT_SHA256", "a" * 64)
    session = FakeSession(
        [
            FakeResponse(
                202, {"request_id": "fed-1", "status": "accepted", "data": {}, "errors": []}
            )
        ]
    )
    client = VectorVueClient(
        _config_with_creds(
            token="jwt",
            signature_secret="sig-secret",
            mtls_client_cert_file="/tmp/client.crt",
            mtls_client_key_file="/tmp/client.key",
        ),
        session=session,
    )
    monkeypatch.setattr(
        client,
        "_sign_federation_payload",
        lambda **_: "dGVzdC1zaWduYXR1cmU=",
    )

    client.send_federated_telemetry(
        {
            "operator_id": "op-001",
            "campaign_id": "cmp-001",
            "tenant_id": "10000000-0000-0000-0000-000000000001",
            "execution_hash": "a" * 64,
            "timestamp": 1700000000,
            "nonce": "nonce-fed-001",
            "signed_metadata": {
                "tenant_id": "10000000-0000-0000-0000-000000000001",
                "operator_id": "op-001",
                "campaign_id": "cmp-001",
            },
            "payload": {
                "event_id": "evt-fed-001",
                "event_type": "PROCESS_ANOMALY",
                "source_system": "spectrastrike",
                "severity": "high",
                "observed_at": "2026-02-26T12:00:00Z",
                "mitre_techniques": ["T1059.001"],
                "mitre_tactics": ["TA0002"],
                "description": "federated test",
                "attributes": {"asset_ref": "host-a", "schema_version": "1.0"},
            },
        },
        idempotency_key="fp-1",
    )

    call = session.calls[0]
    assert call["url"].endswith("/internal/v1/telemetry")
    assert call["headers"]["Idempotency-Key"] == "fp-1"
    assert call["headers"]["X-Service-Identity"] == "spectrastrike-producer"


def test_send_federated_telemetry_requires_signature_and_mtls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("VECTORVUE_FEDERATION_SIGNING_KEY_PATH", raising=False)
    session = FakeSession([])
    client = VectorVueClient(
        _config_with_creds(
            token="jwt",
            mtls_client_cert_file="/tmp/client.crt",
            mtls_client_key_file="/tmp/client.key",
        ),
        session=session,
    )

    with pytest.raises(VectorVueSerializationError, match="requires signed telemetry"):
        client.send_federated_telemetry({"timestamp": 1, "nonce": "n"})


def test_send_federated_telemetry_requires_mtls(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    key_path = tmp_path / "fed.key"
    key_path.write_bytes(b"\x02" * 32)
    monkeypatch.setenv("VECTORVUE_FEDERATION_SIGNING_KEY_PATH", str(key_path))
    session = FakeSession([])
    client = VectorVueClient(
        _config_with_creds(token="jwt", signature_secret="sig-secret"),
        session=session,
    )

    with pytest.raises(VectorVueTransportError, match="requires mTLS client cert/key"):
        client.send_federated_telemetry({"timestamp": 1, "nonce": "n"})


def test_signing_headers_are_added_when_secret_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "pkg.integration.vectorvue.client.time.time", lambda: 1700000000
    )
    session = FakeSession(
        [
            FakeResponse(
                200, {"request_id": "r", "status": "accepted", "data": {}, "errors": []}
            )
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
            FakeResponse(
                200,
                {"request_id": "r2", "status": "accepted", "data": {}, "errors": []},
            ),
        ]
    )
    client = VectorVueClient(
        _config_with_creds(token="jwt", max_retries=2), session=session
    )

    envelope = client.send_event({"event_type": "PROCESS_ANOMALY"})

    assert envelope.request_id == "r2"
    assert len(session.calls) == 2


def test_retries_on_timeout_then_raises_when_exhausted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("pkg.integration.vectorvue.client.time.sleep", lambda _: None)
    session = FakeSession([Timeout("t1"), Timeout("t2")])
    client = VectorVueClient(
        _config_with_creds(token="jwt", max_retries=1), session=session
    )

    with pytest.raises(VectorVueTransportError):
        client.send_event({"event_type": "PROCESS_ANOMALY"})

    assert len(session.calls) == 2


def test_batch_size_guard() -> None:
    session = FakeSession([])
    client = VectorVueClient(
        _config_with_creds(token="jwt", max_batch_size=1), session=session
    )

    with pytest.raises(VectorVueSerializationError):
        client.send_events_batch(
            [
                {"event_type": "A"},
                {"event_type": "B"},
            ]
        )


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


def test_tls_pinning_accepts_matching_peer_cert() -> None:
    cert = b"vectorvue-cert"
    digest = hashlib.sha256(cert).hexdigest()
    response = FakeResponse(
        200, {"request_id": "r", "status": "accepted", "data": {}, "errors": []}
    )
    response.raw = _FakeRaw(cert)  # type: ignore[attr-defined]
    session = FakeSession([response])
    client = VectorVueClient(
        _config_with_creds(token="jwt", tls_pinned_cert_sha256=digest),
        session=session,
    )

    envelope = client.send_event({"event_type": "A"})
    assert envelope.status == "accepted"


def test_tls_pinning_rejects_mismatched_peer_cert() -> None:
    cert = b"vectorvue-cert"
    response = FakeResponse(
        200, {"request_id": "r", "status": "accepted", "data": {}, "errors": []}
    )
    response.raw = _FakeRaw(cert)  # type: ignore[attr-defined]
    session = FakeSession([response])
    client = VectorVueClient(
        _config_with_creds(token="jwt", tls_pinned_cert_sha256="deadbeef"),
        session=session,
    )

    with pytest.raises(VectorVueTransportError, match="tls pinning validation failed"):
        client.send_event({"event_type": "A"})
