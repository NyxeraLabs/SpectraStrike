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

"""Unit tests for execution manifest schema validation."""

from __future__ import annotations

import pytest

from pkg.orchestrator.manifest import (
    ExecutionManifest,
    ExecutionManifestValidationError,
    ExecutionTaskContext,
)


def _task_context(**overrides: str) -> ExecutionTaskContext:
    base = {
        "task_id": "task-001",
        "tenant_id": "tenant-a",
        "operator_id": "alice",
        "source": "api",
        "action": "run",
        "requested_at": "2026-02-25T00:00:00+00:00",
        "correlation_id": "bc8d85ff-31f2-4b57-9adf-3ce24227de97",
    }
    base.update(overrides)
    return ExecutionTaskContext(**base)


def _manifest(**overrides: object) -> ExecutionManifest:
    base: dict[str, object] = {
        "task_context": _task_context(),
        "target_urn": "urn:target:ip:10.0.0.5",
        "tool_sha256": "sha256:" + ("a" * 64),
        "nonce": "nonce-0001",
        "parameters": {"ports": [443], "aggressive": True},
        "issued_at": "2026-02-25T00:00:05+00:00",
        "manifest_version": "1.0.0",
    }
    base.update(overrides)
    return ExecutionManifest(**base)


def test_manifest_to_payload_contains_required_sections() -> None:
    manifest = _manifest()

    payload = manifest.to_payload()

    assert payload["target_urn"] == "urn:target:ip:10.0.0.5"
    assert payload["tool_sha256"] == "sha256:" + ("a" * 64)
    assert payload["nonce"] == "nonce-0001"
    assert payload["task_context"]["tenant_id"] == "tenant-a"
    assert payload["parameters"]["ports"] == [443]


def test_manifest_requires_valid_target_urn() -> None:
    with pytest.raises(ExecutionManifestValidationError, match="target_urn"):
        _manifest(target_urn="10.0.0.5")


def test_manifest_requires_sha256_hex_format() -> None:
    with pytest.raises(ExecutionManifestValidationError, match="tool_sha256"):
        _manifest(tool_sha256="sha256:ABCDEF")


def test_manifest_requires_parameters_dict() -> None:
    with pytest.raises(ExecutionManifestValidationError, match="parameters"):
        _manifest(parameters=["--flag"])  # type: ignore[arg-type]


def test_manifest_requires_nonce_format() -> None:
    with pytest.raises(ExecutionManifestValidationError, match="nonce"):
        _manifest(nonce="x")


def test_task_context_requires_operator_and_tenant() -> None:
    with pytest.raises(ExecutionManifestValidationError, match="tenant_id"):
        _task_context(tenant_id=" ")
    with pytest.raises(ExecutionManifestValidationError, match="operator_id"):
        _task_context(operator_id=" ")


def test_task_context_requires_iso_requested_at() -> None:
    with pytest.raises(ExecutionManifestValidationError, match="requested_at"):
        _task_context(requested_at="not-a-time")


def test_task_context_requires_task_id_format() -> None:
    with pytest.raises(ExecutionManifestValidationError, match="task_id"):
        _task_context(task_id="x")
