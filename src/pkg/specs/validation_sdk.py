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

"""Sprint 33 validation SDK for published specification contracts."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from pkg.orchestrator.manifest import (
    ExecutionManifest,
    canonical_manifest_json,
    parse_and_validate_manifest_submission,
)
from pkg.orchestrator.telemetry_schema import TelemetrySchemaParser

_SHA256_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
_URN_PATTERN = re.compile(r"^urn:[a-z0-9][a-z0-9-]{0,31}:[^\s]+$")


@dataclass(slots=True, frozen=True)
class ValidationResult:
    """Validation response model for spec SDK checks."""

    ok: bool
    errors: list[str]
    normalized: dict[str, Any] | None = None


class SpecValidationError(ValueError):
    """Raised for invalid SDK arguments."""


def _ok(normalized: dict[str, Any]) -> ValidationResult:
    return ValidationResult(ok=True, errors=[], normalized=normalized)


def _fail(message: str) -> ValidationResult:
    return ValidationResult(ok=False, errors=[message], normalized=None)


def validate_execution_manifest_v1(payload: dict[str, Any]) -> ValidationResult:
    """Validate v1 execution manifest payload contract."""
    if not isinstance(payload, dict):
        raise SpecValidationError("manifest payload must be a dictionary")
    try:
        canonical = canonical_manifest_json(payload)
        parsed: ExecutionManifest = parse_and_validate_manifest_submission(canonical)
    except ValueError as exc:
        return _fail(str(exc))

    return _ok(
        {
            "manifest_version": parsed.manifest_version,
            "target_urn": parsed.target_urn,
            "tool_sha256": parsed.tool_sha256,
            "deterministic_hash": parsed.deterministic_hash(),
        }
    )


def validate_telemetry_extension_v1(payload: dict[str, Any]) -> ValidationResult:
    """Validate telemetry extension payload using unified parser contract."""
    if not isinstance(payload, dict):
        raise SpecValidationError("telemetry payload must be a dictionary")
    parser = TelemetrySchemaParser()
    try:
        parsed = parser.parse(payload)
    except ValueError as exc:
        return _fail(str(exc))

    return _ok(
        {
            "event_type": parsed.event_type,
            "actor": parsed.actor,
            "target": parsed.target,
            "status": parsed.status,
            "tenant_id": parsed.tenant_id,
            "attributes": parsed.attributes,
        }
    )


def validate_capability_policy_input_v1(payload: dict[str, Any]) -> ValidationResult:
    """Validate OPA capability input contract used by execution authorization."""
    if not isinstance(payload, dict):
        raise SpecValidationError("capability payload must be a dictionary")

    operator_id = str(payload.get("operator_id", "")).strip()
    tenant_id = str(payload.get("tenant_id", "")).strip()
    tool_sha256 = str(payload.get("tool_sha256", "")).strip()
    target_urn = str(payload.get("target_urn", "")).strip()
    action = str(payload.get("action", "")).strip()

    if not operator_id:
        return _fail("operator_id is required")
    if not tenant_id:
        return _fail("tenant_id is required")
    if not _SHA256_PATTERN.match(tool_sha256):
        return _fail("tool_sha256 must match sha256:<64 lowercase hex>")
    if not _URN_PATTERN.match(target_urn):
        return _fail("target_urn must follow URN format")
    if not action:
        return _fail("action is required")

    return _ok(
        {
            "operator_id": operator_id,
            "tenant_id": tenant_id,
            "tool_sha256": tool_sha256,
            "target_urn": target_urn,
            "action": action,
        }
    )


def validate_spec_bundle_v1(
    *,
    manifest_payload: dict[str, Any],
    telemetry_payload: dict[str, Any],
    capability_payload: dict[str, Any],
) -> dict[str, ValidationResult]:
    """Validate all Sprint 33 published v1 contracts as one bundle."""
    return {
        "manifest": validate_execution_manifest_v1(manifest_payload),
        "telemetry": validate_telemetry_extension_v1(telemetry_payload),
        "capability": validate_capability_policy_input_v1(capability_payload),
    }
