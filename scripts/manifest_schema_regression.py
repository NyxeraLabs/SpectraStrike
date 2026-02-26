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

"""Deterministic regression guard for manifest canonical schema behavior."""

from __future__ import annotations

from pkg.orchestrator.manifest import (
    ExecutionManifest,
    ExecutionTaskContext,
    ManifestSchemaVersionPolicy,
)

EXPECTED_MANIFEST_HASH = (
    "f583b422a7d3ad0d694cfb4f2829b2f3ed64d9db3216eb13e9570c55d167ebf5"
)


def _fixture_manifest() -> ExecutionManifest:
    context = ExecutionTaskContext(
        task_id="task-001",
        tenant_id="tenant-a",
        operator_id="alice",
        source="api",
        action="run",
        requested_at="2026-02-26T00:00:00+00:00",
        correlation_id="bc8d85ff-31f2-4b57-9adf-3ce24227de97",
    )
    return ExecutionManifest(
        task_context=context,
        target_urn="urn:target:ip:10.0.0.5",
        tool_sha256="sha256:" + ("a" * 64),
        nonce="nonce-0001",
        parameters={"aggressive": True, "ports": [443]},
        issued_at="2026-02-26T00:00:05+00:00",
        manifest_version="1.0.0",
    )


def main() -> int:
    manifest = _fixture_manifest()
    ManifestSchemaVersionPolicy.assert_supported(manifest.manifest_version)
    actual_hash = manifest.deterministic_hash()
    if actual_hash != EXPECTED_MANIFEST_HASH:
        print("Manifest schema regression detected")
        print(f"Expected: {EXPECTED_MANIFEST_HASH}")
        print(f"Actual:   {actual_hash}")
        return 1
    print("Manifest schema regression check: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
