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

"""Control plane integrity enforcement for signed startup configuration."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from pkg.logging.framework import emit_integrity_audit_event
from pkg.runner.jws_verify import JWSVerificationError, RunnerJWSVerifier


def _canonical_json(value: dict[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256_hex(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


class ControlPlaneIntegrityError(RuntimeError):
    """Base exception for control plane startup integrity failures."""


class UnsignedConfigurationError(ControlPlaneIntegrityError):
    """Raised when startup configuration does not include a signature."""


class ConfigurationSignatureMismatchError(ControlPlaneIntegrityError):
    """Raised when config payload hash does not match signed claims."""


class PolicyHashMismatchError(ControlPlaneIntegrityError):
    """Raised when policy hash differs from pinned/enforced values."""


class RuntimeBinaryHashMismatchError(ControlPlaneIntegrityError):
    """Raised when runtime binary hash differs from expected baseline."""


class ImmutableConfigurationHistoryError(ControlPlaneIntegrityError):
    """Raised when immutable config history constraints are violated."""


@dataclass(slots=True, frozen=True)
class SignedConfigurationEnvelope:
    """Signed startup configuration container."""

    version: str
    config: dict[str, Any]
    signature: str
    policy_sha256: str
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    runtime_binary_sha256: str | None = None

    def __post_init__(self) -> None:
        if not self.version.strip():
            raise ValueError("version is required")
        if not isinstance(self.config, dict) or not self.config:
            raise ValueError("config must be a non-empty dictionary")
        if not self.signature.strip():
            raise ValueError("signature is required")
        if not _is_sha256(self.policy_sha256):
            raise ValueError("policy_sha256 must be 64 lowercase hex chars")
        if self.runtime_binary_sha256 is not None and not _is_sha256(
            self.runtime_binary_sha256
        ):
            raise ValueError("runtime_binary_sha256 must be 64 lowercase hex chars")
        try:
            datetime.fromisoformat(self.created_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("created_at must be ISO-8601 compatible") from exc

    @property
    def config_sha256(self) -> str:
        """Return deterministic SHA-256 hash of canonicalized config payload."""
        return _sha256_hex(_canonical_json(self.config))

    def to_record(self) -> dict[str, str]:
        """Return immutable history record projection."""
        return {
            "version": self.version,
            "created_at": self.created_at,
            "config_sha256": self.config_sha256,
            "policy_sha256": self.policy_sha256,
            "runtime_binary_sha256": self.runtime_binary_sha256 or "",
        }


@dataclass(slots=True, frozen=True)
class StartupIntegrityConfig:
    """Runtime enforcement configuration for control plane startup."""

    pinned_policy_sha256: str
    enforce_binary_hash: bool = True
    runtime_binary_path: str | None = None

    @classmethod
    def from_env(cls) -> StartupIntegrityConfig:
        pinned = os.getenv("OPA_POLICY_PINNED_SHA256", "").strip().lower()
        if not _is_sha256(pinned):
            raise ValueError("OPA_POLICY_PINNED_SHA256 must be set to sha256 hex")
        enforce_binary_hash = (
            os.getenv("SPECTRASTRIKE_ENFORCE_BINARY_HASH", "true").strip().lower()
            in {"1", "true", "yes", "on"}
        )
        runtime_binary_path = os.getenv("SPECTRASTRIKE_RUNTIME_BINARY_PATH")
        return cls(
            pinned_policy_sha256=pinned,
            enforce_binary_hash=enforce_binary_hash,
            runtime_binary_path=runtime_binary_path,
        )


@dataclass(slots=True)
class ImmutableConfigurationHistory:
    """Append-only immutable history for signed config versions."""

    _records: list[dict[str, str]] = field(default_factory=list)

    def append(self, envelope: SignedConfigurationEnvelope) -> dict[str, str]:
        """Append a config version record enforcing immutable constraints."""
        if any(item["version"] == envelope.version for item in self._records):
            raise ImmutableConfigurationHistoryError(
                "configuration version already exists in immutable history"
            )
        record = envelope.to_record()
        previous_hash = self._records[-1]["record_hash"] if self._records else "GENESIS"
        canonical = _canonical_json(record)
        record_hash = _sha256_hex(f"{previous_hash}:".encode("utf-8") + canonical)
        stored = dict(record)
        stored["prev_hash"] = previous_hash
        stored["record_hash"] = record_hash
        self._records.append(stored)
        return dict(stored)

    @property
    def records(self) -> list[dict[str, str]]:
        """Return immutable config history snapshot."""
        return [dict(item) for item in self._records]


@dataclass(slots=True, frozen=True)
class StartupIntegrityResult:
    """Startup integrity report for orchestration bootstrap."""

    config_version: str
    config_sha256: str
    policy_sha256: str
    runtime_binary_sha256: str | None
    history_record_hash: str


class ControlPlaneIntegrityEnforcer:
    """Validates signed startup config, policy pinning, and binary baseline."""

    def __init__(
        self,
        integrity_config: StartupIntegrityConfig,
        *,
        verifier: RunnerJWSVerifier | None = None,
        history: ImmutableConfigurationHistory | None = None,
    ) -> None:
        self._integrity_config = integrity_config
        self._verifier = verifier or RunnerJWSVerifier()
        self._history = history or ImmutableConfigurationHistory()

    def enforce_startup(
        self,
        envelope: SignedConfigurationEnvelope,
        *,
        hmac_secret: str | None = None,
        public_key_pem: str | None = None,
    ) -> StartupIntegrityResult:
        """Enforce startup integrity checks and return immutable result metadata."""
        if not envelope.signature:
            raise UnsignedConfigurationError("startup configuration must be signed")

        claims = self._verify_signed_claims(
            signature=envelope.signature,
            hmac_secret=hmac_secret,
            public_key_pem=public_key_pem,
        )
        claimed_config_sha = str(claims.get("config_sha256", "")).lower()
        actual_config_sha = envelope.config_sha256
        if claimed_config_sha != actual_config_sha:
            emit_integrity_audit_event(
                action="startup_integrity",
                actor="orchestrator",
                target="control-plane",
                status="denied",
                reason="config_signature_mismatch",
                expected_config_sha256=claimed_config_sha,
                actual_config_sha256=actual_config_sha,
            )
            raise ConfigurationSignatureMismatchError(
                "signed config_sha256 does not match startup configuration payload"
            )

        if envelope.policy_sha256 != self._integrity_config.pinned_policy_sha256:
            emit_integrity_audit_event(
                action="startup_integrity",
                actor="orchestrator",
                target="control-plane",
                status="denied",
                reason="policy_hash_pin_mismatch",
                pinned_policy_sha256=self._integrity_config.pinned_policy_sha256,
                supplied_policy_sha256=envelope.policy_sha256,
            )
            raise PolicyHashMismatchError("OPA policy hash does not match pinned hash")

        runtime_hash: str | None = None
        if self._integrity_config.enforce_binary_hash:
            runtime_hash = self._runtime_binary_sha256(
                self._integrity_config.runtime_binary_path
            )
            expected_runtime_hash = envelope.runtime_binary_sha256 or ""
            if expected_runtime_hash and runtime_hash != expected_runtime_hash:
                emit_integrity_audit_event(
                    action="startup_integrity",
                    actor="orchestrator",
                    target="control-plane",
                    status="denied",
                    reason="runtime_binary_hash_mismatch",
                    expected_runtime_binary_sha256=expected_runtime_hash,
                    actual_runtime_binary_sha256=runtime_hash,
                )
                raise RuntimeBinaryHashMismatchError(
                    "runtime binary hash does not match signed baseline"
                )

        history_record = self._history.append(envelope)
        emit_integrity_audit_event(
            action="startup_integrity",
            actor="orchestrator",
            target="control-plane",
            status="success",
            config_version=envelope.version,
            config_sha256=actual_config_sha,
            policy_sha256=envelope.policy_sha256,
            runtime_binary_sha256=runtime_hash or "",
            history_record_hash=history_record["record_hash"],
        )
        return StartupIntegrityResult(
            config_version=envelope.version,
            config_sha256=actual_config_sha,
            policy_sha256=envelope.policy_sha256,
            runtime_binary_sha256=runtime_hash,
            history_record_hash=history_record["record_hash"],
        )

    def _verify_signed_claims(
        self,
        *,
        signature: str,
        hmac_secret: str | None,
        public_key_pem: str | None,
    ) -> dict[str, Any]:
        try:
            return self._verifier.verify(
                compact_jws=signature,
                hmac_secret=hmac_secret,
                public_key_pem=public_key_pem,
            )
        except JWSVerificationError as exc:
            raise UnsignedConfigurationError(
                "startup configuration signature verification failed"
            ) from exc

    @staticmethod
    def _runtime_binary_sha256(binary_path: str | None) -> str:
        if not binary_path:
            binary_path = __file__
        with open(binary_path, "rb") as handle:
            return _sha256_hex(handle.read())


def _is_sha256(value: str) -> bool:
    return bool(value) and len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )
