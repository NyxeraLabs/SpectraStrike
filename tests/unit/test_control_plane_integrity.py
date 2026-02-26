# Copyright (c) 2026 NyxeraLabs
# Author: Jose Maria Micoli
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

"""Unit tests for Sprint 19 control-plane integrity enforcement."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from pathlib import Path

import pytest

from pkg.orchestrator.control_plane_integrity import (
    ConfigurationSignatureMismatchError,
    ControlPlaneIntegrityEnforcer,
    ImmutableConfigurationHistory,
    ImmutableConfigurationHistoryError,
    PolicyHashMismatchError,
    RuntimeBinaryHashMismatchError,
    SignedConfigurationEnvelope,
    StartupIntegrityConfig,
    UnsignedConfigurationError,
)


def _sha256_hex(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _hs256_jws(payload: dict[str, object], secret: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    header_segment = _b64(
        json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )
    payload_segment = _b64(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )
    signing_input = f"{header_segment}.{payload_segment}".encode("ascii")
    signature = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    return f"{header_segment}.{payload_segment}.{_b64(signature)}"


def _envelope(
    *,
    version: str,
    config: dict[str, object],
    policy_sha256: str,
    runtime_binary_sha256: str,
    secret: str,
    claimed_config_sha256: str | None = None,
) -> SignedConfigurationEnvelope:
    config_sha = claimed_config_sha256 or _sha256_hex(
        json.dumps(config, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )
    signature = _hs256_jws(
        {
            "config_sha256": config_sha,
            "version": version,
        },
        secret,
    )
    return SignedConfigurationEnvelope(
        version=version,
        config=config,
        signature=signature,
        policy_sha256=policy_sha256,
        runtime_binary_sha256=runtime_binary_sha256,
    )


def test_enforce_startup_accepts_signed_config_and_writes_history(tmp_path: Path) -> None:
    binary = tmp_path / "runtime.bin"
    binary.write_bytes(b"spectrastrike-runtime")
    runtime_hash = _sha256_hex(binary.read_bytes())

    policy_hash = _sha256_hex(b"package spectrastrike")
    secret = "startup-secret"
    config = {"mode": "strict", "tenant_guard": True}
    envelope = _envelope(
        version="19.0.1",
        config=config,
        policy_sha256=policy_hash,
        runtime_binary_sha256=runtime_hash,
        secret=secret,
    )
    history = ImmutableConfigurationHistory()
    enforcer = ControlPlaneIntegrityEnforcer(
        StartupIntegrityConfig(
            pinned_policy_sha256=policy_hash,
            runtime_binary_path=str(binary),
            enforce_binary_hash=True,
        ),
        history=history,
    )

    result = enforcer.enforce_startup(envelope, hmac_secret=secret)

    assert result.config_version == "19.0.1"
    assert result.runtime_binary_sha256 == runtime_hash
    assert len(history.records) == 1
    assert history.records[0]["version"] == "19.0.1"


def test_enforce_startup_rejects_invalid_signature() -> None:
    policy_hash = _sha256_hex(b"opa")
    envelope = SignedConfigurationEnvelope(
        version="19.0.2",
        config={"strict": True},
        signature="broken.signature.token",
        policy_sha256=policy_hash,
    )
    enforcer = ControlPlaneIntegrityEnforcer(
        StartupIntegrityConfig(
            pinned_policy_sha256=policy_hash,
            enforce_binary_hash=False,
        )
    )

    with pytest.raises(UnsignedConfigurationError):
        enforcer.enforce_startup(envelope, hmac_secret="secret")


def test_enforce_startup_detects_config_hash_mismatch() -> None:
    policy_hash = _sha256_hex(b"opa-policy")
    secret = "secret"
    envelope = _envelope(
        version="19.0.3",
        config={"strict": True},
        policy_sha256=policy_hash,
        runtime_binary_sha256=_sha256_hex(b"runtime"),
        secret=secret,
        claimed_config_sha256=_sha256_hex(b"different"),
    )
    enforcer = ControlPlaneIntegrityEnforcer(
        StartupIntegrityConfig(
            pinned_policy_sha256=policy_hash,
            enforce_binary_hash=False,
        )
    )

    with pytest.raises(ConfigurationSignatureMismatchError):
        enforcer.enforce_startup(envelope, hmac_secret=secret)


def test_enforce_startup_detects_policy_pin_mismatch() -> None:
    secret = "secret"
    envelope = _envelope(
        version="19.0.4",
        config={"strict": True},
        policy_sha256=_sha256_hex(b"policy-a"),
        runtime_binary_sha256=_sha256_hex(b"runtime"),
        secret=secret,
    )
    enforcer = ControlPlaneIntegrityEnforcer(
        StartupIntegrityConfig(
            pinned_policy_sha256=_sha256_hex(b"policy-b"),
            enforce_binary_hash=False,
        )
    )

    with pytest.raises(PolicyHashMismatchError):
        enforcer.enforce_startup(envelope, hmac_secret=secret)


def test_enforce_startup_detects_runtime_binary_hash_mismatch(tmp_path: Path) -> None:
    binary = tmp_path / "runtime.bin"
    binary.write_bytes(b"real-runtime")
    secret = "secret"
    policy_hash = _sha256_hex(b"policy")
    envelope = _envelope(
        version="19.0.5",
        config={"strict": True},
        policy_sha256=policy_hash,
        runtime_binary_sha256=_sha256_hex(b"unexpected-runtime"),
        secret=secret,
    )
    enforcer = ControlPlaneIntegrityEnforcer(
        StartupIntegrityConfig(
            pinned_policy_sha256=policy_hash,
            runtime_binary_path=str(binary),
            enforce_binary_hash=True,
        )
    )

    with pytest.raises(RuntimeBinaryHashMismatchError):
        enforcer.enforce_startup(envelope, hmac_secret=secret)


def test_immutable_history_rejects_duplicate_versions() -> None:
    policy_hash = _sha256_hex(b"policy")
    secret = "secret"
    envelope = _envelope(
        version="19.1.0",
        config={"strict": True},
        policy_sha256=policy_hash,
        runtime_binary_sha256=_sha256_hex(b"runtime"),
        secret=secret,
    )
    history = ImmutableConfigurationHistory()
    history.append(envelope)

    with pytest.raises(ImmutableConfigurationHistoryError):
        history.append(envelope)
