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

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

_URN_PATTERN = re.compile(r"^urn:[a-z0-9][a-z0-9-]{0,31}:[^\s]+$")
_SHA256_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
_TASK_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{2,127}$")
_NONCE_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{8,128}$")


class ExecutionManifestValidationError(ValueError):
    """Raised when an execution manifest or context is invalid."""


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
