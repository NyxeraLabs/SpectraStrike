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

"""Unit tests for Sprint 33 specification validation SDK."""

from __future__ import annotations

from pkg.specs.validation_sdk import (
    validate_capability_policy_input_v1,
    validate_execution_manifest_v1,
    validate_spec_bundle_v1,
    validate_telemetry_extension_v1,
)


def _manifest_payload() -> dict[str, object]:
    return {
        "manifest_version": "1.0.0",
        "issued_at": "2026-02-27T00:00:05+00:00",
        "task_context": {
            "task_id": "task-001",
            "tenant_id": "tenant-a",
            "operator_id": "op-001",
            "source": "api",
            "action": "run",
            "requested_at": "2026-02-27T00:00:00+00:00",
            "correlation_id": "bc8d85ff-31f2-4b57-9adf-3ce24227de97",
        },
        "target_urn": "urn:target:ip:10.0.0.5",
        "tool_sha256": "sha256:" + ("a" * 64),
        "nonce": "nonce-0001",
        "parameters": {"ports": [443]},
    }


def _telemetry_payload() -> dict[str, object]:
    return {
        "event_type": "nmap_scan_completed",
        "actor": "op-001",
        "target": "urn:target:ip:10.0.0.5",
        "status": "success",
        "tenant_id": "tenant-a",
        "attributes": {"severity": "medium"},
    }


def _capability_payload() -> dict[str, object]:
    return {
        "operator_id": "op-001",
        "tenant_id": "tenant-a",
        "tool_sha256": "sha256:" + ("b" * 64),
        "target_urn": "urn:target:ip:10.0.0.5",
        "action": "execute",
    }


def test_validate_execution_manifest_v1_accepts_valid_payload() -> None:
    result = validate_execution_manifest_v1(_manifest_payload())

    assert result.ok is True
    assert result.errors == []
    assert result.normalized is not None
    assert result.normalized["manifest_version"] == "1.0.0"
    assert len(str(result.normalized["deterministic_hash"])) == 64


def test_validate_execution_manifest_v1_rejects_invalid_payload() -> None:
    payload = _manifest_payload()
    payload["target_urn"] = "10.0.0.5"

    result = validate_execution_manifest_v1(payload)

    assert result.ok is False
    assert result.errors


def test_validate_telemetry_extension_v1_accepts_internal_contract() -> None:
    result = validate_telemetry_extension_v1(_telemetry_payload())

    assert result.ok is True
    assert result.normalized is not None
    assert result.normalized["tenant_id"] == "tenant-a"


def test_validate_capability_policy_input_v1_rejects_bad_tool_hash() -> None:
    payload = _capability_payload()
    payload["tool_sha256"] = "sha256:ABC"

    result = validate_capability_policy_input_v1(payload)

    assert result.ok is False
    assert result.errors == ["tool_sha256 must match sha256:<64 lowercase hex>"]


def test_validate_spec_bundle_v1_returns_three_result_groups() -> None:
    result = validate_spec_bundle_v1(
        manifest_payload=_manifest_payload(),
        telemetry_payload=_telemetry_payload(),
        capability_payload=_capability_payload(),
    )

    assert set(result.keys()) == {"manifest", "telemetry", "capability"}
    assert result["manifest"].ok is True
    assert result["telemetry"].ok is True
    assert result["capability"].ok is True
