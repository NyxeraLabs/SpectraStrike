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

"""Execution manifest schema for cryptographic task endorsement."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

_URN_PATTERN = re.compile(r"^urn:[a-z0-9][a-z0-9-]{0,31}:[^\s]+$")
_SHA256_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
_TASK_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{2,127}$")
_NONCE_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{8,128}$")
_SEMVER_PATTERN = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


class ExecutionManifestValidationError(ValueError):
    """Raised when an execution manifest or context is invalid."""


class NonCanonicalManifestError(ExecutionManifestValidationError):
    """Raised when submitted manifest payload is not canonical JSON."""


class ManifestSchemaVersionError(ExecutionManifestValidationError):
    """Raised when manifest schema version is invalid or unsupported."""


@dataclass(slots=True, frozen=True)
class ExecutionTaskContext:
    """Task identity and tenant/operator context required for signing."""

    task_id: str
    tenant_id: str
    operator_id: str
    source: str
    action: str
    requested_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    correlation_id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if not _TASK_ID_PATTERN.match(self.task_id):
            raise ExecutionManifestValidationError("task_id format is invalid")
        if not self.tenant_id.strip():
            raise ExecutionManifestValidationError("tenant_id is required")
        if not self.operator_id.strip():
            raise ExecutionManifestValidationError("operator_id is required")
        if not self.source.strip():
            raise ExecutionManifestValidationError("source is required")
        if not self.action.strip():
            raise ExecutionManifestValidationError("action is required")
        try:
            datetime.fromisoformat(self.requested_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ExecutionManifestValidationError(
                "requested_at must be ISO-8601 compatible"
            ) from exc

    def to_dict(self) -> dict[str, str]:
        """Return task context as a plain mapping."""
        return {
            "task_id": self.task_id,
            "tenant_id": self.tenant_id,
            "operator_id": self.operator_id,
            "source": self.source,
            "action": self.action,
            "requested_at": self.requested_at,
            "correlation_id": self.correlation_id,
        }


@dataclass(slots=True, frozen=True)
class ExecutionManifest:
    """Canonical execution manifest schema for signed payload dispatch."""

    task_context: ExecutionTaskContext
    target_urn: str
    tool_sha256: str
    nonce: str = field(default_factory=lambda: uuid4().hex)
    parameters: dict[str, Any] = field(default_factory=dict)
    issued_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    manifest_version: str = "1.0.0"

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if not _URN_PATTERN.match(self.target_urn):
            raise ExecutionManifestValidationError(
                "target_urn must follow URN format (urn:<nid>:<nss>)"
            )
        if not _SHA256_PATTERN.match(self.tool_sha256):
            raise ExecutionManifestValidationError(
                "tool_sha256 must match sha256:<64 lowercase hex>"
            )
        if not _NONCE_PATTERN.match(self.nonce):
            raise ExecutionManifestValidationError(
                "nonce must be 8-128 chars (A-Za-z0-9._:-)"
            )
        if not isinstance(self.parameters, dict):
            raise ExecutionManifestValidationError("parameters must be a dictionary")
        if not self.manifest_version.strip():
            raise ExecutionManifestValidationError("manifest_version is required")
        ManifestSchemaVersionPolicy.assert_supported(self.manifest_version)
        try:
            datetime.fromisoformat(self.issued_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ExecutionManifestValidationError(
                "issued_at must be ISO-8601 compatible"
            ) from exc

    def to_payload(self) -> dict[str, Any]:
        """Return manifest payload for canonical JWS signing."""
        return {
            "manifest_version": self.manifest_version,
            "issued_at": self.issued_at,
            "task_context": self.task_context.to_dict(),
            "target_urn": self.target_urn,
            "tool_sha256": self.tool_sha256,
            "nonce": self.nonce,
            "parameters": dict(self.parameters),
        }

    def canonical_json(self) -> str:
        """Return deterministic canonical JSON representation of manifest payload."""
        return canonical_manifest_json(self.to_payload())

    def deterministic_hash(self) -> str:
        """Return deterministic SHA-256 hash over canonical manifest JSON."""
        return deterministic_manifest_hash(self.to_payload())


class ManifestSchemaVersionPolicy:
    """Semantic-versioning policy for manifest schema compatibility."""

    SUPPORTED_MAJOR = 1
    MIN_SUPPORTED_VERSION = "1.0.0"
    MAX_SUPPORTED_VERSION = "1.99.99"

    @classmethod
    def assert_supported(cls, version: str) -> None:
        parts = cls.parse(version)
        if parts[0] != cls.SUPPORTED_MAJOR:
            raise ManifestSchemaVersionError(
                f"unsupported manifest_version major: {parts[0]}"
            )
        if cls.compare(version, cls.MIN_SUPPORTED_VERSION) < 0:
            raise ManifestSchemaVersionError(
                f"manifest_version {version} is below minimum supported "
                f"{cls.MIN_SUPPORTED_VERSION}"
            )
        if cls.compare(version, cls.MAX_SUPPORTED_VERSION) > 0:
            raise ManifestSchemaVersionError(
                f"manifest_version {version} exceeds maximum supported "
                f"{cls.MAX_SUPPORTED_VERSION}"
            )

    @staticmethod
    def parse(version: str) -> tuple[int, int, int]:
        match = _SEMVER_PATTERN.match(version.strip())
        if not match:
            raise ManifestSchemaVersionError(
                "manifest_version must follow semantic versioning (MAJOR.MINOR.PATCH)"
            )
        return tuple(int(part) for part in match.groups())

    @classmethod
    def compare(cls, left: str, right: str) -> int:
        left_parts = cls.parse(left)
        right_parts = cls.parse(right)
        if left_parts < right_parts:
            return -1
        if left_parts > right_parts:
            return 1
        return 0


def canonical_manifest_json(payload: dict[str, Any]) -> str:
    """Produce canonical JSON string for deterministic signing and hashing."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def deterministic_manifest_hash(payload: dict[str, Any]) -> str:
    """Compute deterministic SHA-256 over canonical manifest JSON."""
    canonical = canonical_manifest_json(payload).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def parse_and_validate_manifest_submission(raw_manifest: str) -> ExecutionManifest:
    """Parse submitted JSON, enforce canonical form, and construct manifest model."""
    if not raw_manifest.strip():
        raise NonCanonicalManifestError("manifest submission must not be empty")

    try:
        payload = json.loads(raw_manifest)
    except json.JSONDecodeError as exc:
        raise NonCanonicalManifestError("manifest submission is not valid JSON") from exc

    if not isinstance(payload, dict):
        raise NonCanonicalManifestError("manifest submission must be a JSON object")

    canonical = canonical_manifest_json(payload)
    if raw_manifest.strip() != canonical:
        raise NonCanonicalManifestError(
            "manifest submission is non-canonical; must be compact sorted JSON"
        )

    task_context_raw = payload.get("task_context")
    if not isinstance(task_context_raw, dict):
        raise ExecutionManifestValidationError("task_context must be a dictionary")

    task_context = ExecutionTaskContext(
        task_id=str(task_context_raw.get("task_id", "")),
        tenant_id=str(task_context_raw.get("tenant_id", "")),
        operator_id=str(task_context_raw.get("operator_id", "")),
        source=str(task_context_raw.get("source", "")),
        action=str(task_context_raw.get("action", "")),
        requested_at=str(task_context_raw.get("requested_at", "")),
        correlation_id=str(task_context_raw.get("correlation_id", "")),
    )

    return ExecutionManifest(
        task_context=task_context,
        target_urn=str(payload.get("target_urn", "")),
        tool_sha256=str(payload.get("tool_sha256", "")),
        nonce=str(payload.get("nonce", "")),
        parameters=payload.get("parameters", {}),
        issued_at=str(payload.get("issued_at", "")),
        manifest_version=str(payload.get("manifest_version", "")),
    )
