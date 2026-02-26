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

"""Unified execution fingerprint model for federation trust closure."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from pkg.logging.framework import emit_integrity_audit_event


class ExecutionFingerprintError(ValueError):
    """Raised when fingerprint generation or validation fails."""


@dataclass(slots=True, frozen=True)
class ExecutionFingerprintInput:
    """Canonical input schema for unified execution fingerprint generation."""

    manifest_hash: str
    tool_hash: str
    operator_id: str
    tenant_id: str
    policy_decision_hash: str
    timestamp: str

    def __post_init__(self) -> None:
        values = {
            "manifest_hash": self.manifest_hash,
            "tool_hash": self.tool_hash,
            "operator_id": self.operator_id,
            "tenant_id": self.tenant_id,
            "policy_decision_hash": self.policy_decision_hash,
            "timestamp": self.timestamp,
        }
        for name, value in values.items():
            if not str(value).strip():
                raise ExecutionFingerprintError(f"{name} is required")

    def canonical_json(self) -> str:
        """Return deterministic canonical JSON representation."""
        payload = {
            "manifest_hash": self.manifest_hash,
            "tool_hash": self.tool_hash,
            "operator_id": self.operator_id,
            "tenant_id": self.tenant_id,
            "policy_decision_hash": self.policy_decision_hash,
            "timestamp": self.timestamp,
        }
        return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def generate_execution_fingerprint(data: ExecutionFingerprintInput) -> str:
    """Generate unified execution fingerprint SHA-256 over canonical input."""
    return hashlib.sha256(data.canonical_json().encode("utf-8")).hexdigest()


def generate_operator_bound_execution_fingerprint(
    *,
    data: ExecutionFingerprintInput,
    operator_id: str,
) -> str:
    """Generate fingerprint only when explicit operator identity matches input."""
    if data.operator_id != operator_id:
        raise ExecutionFingerprintError(
            "operator_id mismatch: fingerprint input is not bound to claimed operator"
        )
    return generate_execution_fingerprint(data)


def validate_execution_fingerprint(
    *,
    data: ExecutionFingerprintInput,
    expected_fingerprint: str,
    actor: str,
    target: str,
) -> str:
    """Validate fingerprint equality and emit tamper-evident audit record."""
    computed = generate_execution_fingerprint(data)
    if expected_fingerprint.strip().lower() != computed:
        emit_integrity_audit_event(
            action="execution_fingerprint_validate",
            actor=actor,
            target=target,
            status="denied",
            expected_execution_fingerprint=expected_fingerprint,
            computed_execution_fingerprint=computed,
        )
        raise ExecutionFingerprintError("execution fingerprint mismatch detected")

    emit_integrity_audit_event(
        action="execution_fingerprint_validate",
        actor=actor,
        target=target,
        status="success",
        execution_fingerprint=computed,
    )
    return computed


def validate_fingerprint_before_c2_dispatch(
    *,
    data: ExecutionFingerprintInput,
    provided_fingerprint: str,
    actor: str,
    dispatch_target: str,
) -> str:
    """Enforce fingerprint validation gate before C2 dispatch path."""
    return validate_execution_fingerprint(
        data=data,
        expected_fingerprint=provided_fingerprint,
        actor=actor,
        target=dispatch_target,
    )


def fingerprint_input_from_envelope(
    *,
    actor: str,
    timestamp: str,
    attributes: dict[str, Any],
) -> ExecutionFingerprintInput:
    """Build fingerprint input from normalized telemetry envelope fields."""
    return ExecutionFingerprintInput(
        manifest_hash=str(attributes.get("manifest_hash", "")).strip(),
        tool_hash=str(attributes.get("tool_sha256", "")).strip(),
        operator_id=actor,
        tenant_id=str(attributes.get("tenant_id", "")).strip(),
        policy_decision_hash=str(attributes.get("policy_decision_hash", "")).strip(),
        timestamp=timestamp.strip(),
    )
