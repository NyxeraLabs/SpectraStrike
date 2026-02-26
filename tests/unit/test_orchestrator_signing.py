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

"""Unit tests for Vault transit signing integration."""

from __future__ import annotations

import base64
from dataclasses import dataclass, field
from typing import Any

import pytest

from pkg.orchestrator.signing import (
    VaultTransitConfig,
    VaultTransitError,
    VaultTransitSigner,
)


@dataclass
class FakeResponse:
    status_code: int
    payload: dict[str, Any] = field(default_factory=dict)

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


def _config(**overrides: Any) -> VaultTransitConfig:
    base = {
        "address": "https://vault.internal:8200",
        "token": "vault-token",
        "mount_path": "transit",
        "key_name": "orchestrator-signing",
        "timeout_seconds": 1.0,
    }
    base.update(overrides)
    return VaultTransitConfig(**base)


def test_vault_config_rejects_http_by_default() -> None:
    with pytest.raises(ValueError, match="https"):
        _config(address="http://vault.internal:8200")


def test_vault_config_from_env_parses_fields(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("VAULT_ADDR", "https://vault.service:8200")
    monkeypatch.setenv("VAULT_TOKEN", "tkn")
    monkeypatch.setenv("VAULT_NAMESPACE", "ops")
    monkeypatch.setenv("VAULT_TRANSIT_KEY_NAME", "jws-signing")
    monkeypatch.setenv("VAULT_VERIFY_TLS", "false")
    monkeypatch.setenv("VAULT_TIMEOUT_SECONDS", "9.5")
    monkeypatch.setenv("VAULT_TRANSIT_AUTO_CREATE_KEY", "true")

    cfg = VaultTransitConfig.from_env()

    assert cfg.address == "https://vault.service:8200"
    assert cfg.token == "tkn"
    assert cfg.namespace == "ops"
    assert cfg.key_name == "jws-signing"
    assert cfg.verify_tls is False
    assert cfg.timeout_seconds == 9.5
    assert cfg.auto_create_key is True


def test_ensure_signing_key_posts_expected_payload() -> None:
    session = FakeSession([FakeResponse(204, {"data": {}})])
    signer = VaultTransitSigner(_config(), session=session)  # type: ignore[arg-type]

    signer.ensure_signing_key()

    assert len(session.calls) == 1
    call = session.calls[0]
    assert call["method"] == "POST"
    assert call["url"].endswith("/v1/transit/keys/orchestrator-signing")
    assert call["json"]["type"] == "ecdsa-p256"
    assert call["headers"]["X-Vault-Token"] == "vault-token"


def test_sign_payload_returns_vault_signature() -> None:
    session = FakeSession(
        [FakeResponse(200, {"data": {"signature": "vault:v1:signature-bytes"}})]
    )
    signer = VaultTransitSigner(
        _config(namespace="core-sec"),
        session=session,  # type: ignore[arg-type]
    )

    signature = signer.sign_payload(b'{"tool":"nmap","target":"10.0.0.5"}')

    assert signature == "vault:v1:signature-bytes"
    call = session.calls[0]
    assert call["url"].endswith("/v1/transit/sign/orchestrator-signing")
    assert call["json"]["input"] == base64.b64encode(
        b'{"tool":"nmap","target":"10.0.0.5"}'
    ).decode("ascii")
    assert call["json"]["marshaling_algorithm"] == "jws"
    assert call["headers"]["X-Vault-Namespace"] == "core-sec"


def test_sign_payload_raises_on_vault_http_error() -> None:
    session = FakeSession([FakeResponse(403, {"errors": ["permission denied"]})])
    signer = VaultTransitSigner(_config(), session=session)  # type: ignore[arg-type]

    with pytest.raises(VaultTransitError, match="permission denied"):
        signer.sign_payload(b"abc")


def test_read_public_key_uses_latest_version() -> None:
    session = FakeSession(
        [
            FakeResponse(
                200,
                {
                    "data": {
                        "latest_version": 2,
                        "keys": {
                            "1": {"public_key": "pem-v1"},
                            "2": {"public_key": "pem-v2"},
                        },
                    }
                },
            )
        ]
    )
    signer = VaultTransitSigner(_config(), session=session)  # type: ignore[arg-type]

    public_key = signer.read_public_key()

    assert public_key == "pem-v2"


def test_auto_create_key_runs_on_init() -> None:
    session = FakeSession([FakeResponse(204, {"data": {}})])
    VaultTransitSigner(
        _config(auto_create_key=True),
        session=session,  # type: ignore[arg-type]
    )

    assert len(session.calls) == 1
    assert session.calls[0]["url"].endswith("/v1/transit/keys/orchestrator-signing")


def test_rotate_signing_key_calls_rotate_endpoint() -> None:
    session = FakeSession([FakeResponse(200, {"data": {"latest_version": 3}})])
    signer = VaultTransitSigner(_config(), session=session)  # type: ignore[arg-type]

    data = signer.rotate_signing_key()

    assert data["latest_version"] == 3
    assert len(session.calls) == 1
    assert session.calls[0]["url"].endswith(
        "/v1/transit/keys/orchestrator-signing/rotate"
    )
