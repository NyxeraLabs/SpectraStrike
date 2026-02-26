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
    ManifestSchemaVersionError,
    ManifestSchemaVersionPolicy,
    NonCanonicalManifestError,
    ExecutionManifestValidationError,
    ExecutionTaskContext,
    canonical_manifest_json,
    deterministic_manifest_hash,
    parse_and_validate_manifest_submission,
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


def test_manifest_canonical_json_and_hash_are_deterministic() -> None:
    manifest = _manifest(parameters={"b": 2, "a": 1})
    payload = manifest.to_payload()

    canonical_1 = canonical_manifest_json(payload)
    canonical_2 = manifest.canonical_json()
    assert canonical_1 == canonical_2
    assert '"a":1' in canonical_1
    assert '"b":2' in canonical_1

    hash_1 = deterministic_manifest_hash(payload)
    hash_2 = manifest.deterministic_hash()
    assert hash_1 == hash_2
    assert len(hash_1) == 64


def test_manifest_schema_version_requires_semver_and_supported_major() -> None:
    with pytest.raises(ManifestSchemaVersionError, match="semantic versioning"):
        _manifest(manifest_version="v1")
    with pytest.raises(ManifestSchemaVersionError, match="unsupported manifest_version major"):
        _manifest(manifest_version="2.0.0")
    ManifestSchemaVersionPolicy.assert_supported("1.2.3")


def test_parse_and_validate_manifest_submission_rejects_non_canonical_json() -> None:
    payload = _manifest().to_payload()
    non_canonical = '{"tool_sha256":"' + payload["tool_sha256"] + '","manifest_version":"1.0.0"}'
    with pytest.raises(NonCanonicalManifestError, match="non-canonical"):
        parse_and_validate_manifest_submission(non_canonical)


def test_parse_and_validate_manifest_submission_accepts_canonical_json() -> None:
    payload = _manifest().to_payload()
    raw = canonical_manifest_json(payload)

    parsed = parse_and_validate_manifest_submission(raw)

    assert parsed.target_urn == payload["target_urn"]
    assert parsed.tool_sha256 == payload["tool_sha256"]
