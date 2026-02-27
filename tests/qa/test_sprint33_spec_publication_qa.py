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

"""Sprint 33 QA checks for specification publication and validation SDK."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_roadmap_marks_sprint33_complete() -> None:
    content = (REPO_ROOT / "docs/ROADMAP.md").read_text(encoding="utf-8")
    section_title = "## Sprint 33 (Week 63-64): Specification Publication"
    section_start = content.index(section_title)
    next_section = content.find("\n\n# Phase 10", section_start)
    section = content[section_start:next_section]

    required_checked = [
        "- [x] Publish Execution Manifest Specification v1",
        "- [x] Publish Telemetry Extension Specification",
        "- [x] Publish Capability Policy Specification",
        "- [x] Define backward compatibility guarantees",
        "- [x] Publish validation SDK",
        "- [x] Commit Sprint 33 Specification Publication",
    ]
    for line in required_checked:
        assert line in section


def test_sprint33_spec_artifacts_exist() -> None:
    required_paths = [
        "docs/specs/EXECUTION_MANIFEST_SPEC_V1.md",
        "docs/specs/TELEMETRY_EXTENSION_SPEC_V1.md",
        "docs/specs/CAPABILITY_POLICY_SPEC_V1.md",
        "docs/specs/BACKWARD_COMPATIBILITY_GUARANTEES.md",
        "docs/specs/VALIDATION_SDK.md",
        "src/pkg/specs/validation_sdk.py",
        "tests/unit/test_spec_validation_sdk.py",
    ]
    for relative_path in required_paths:
        absolute = REPO_ROOT / relative_path
        assert absolute.exists(), f"missing sprint 33 artifact: {relative_path}"


def test_validation_sdk_exports_published_contracts() -> None:
    content = (REPO_ROOT / "src/pkg/specs/validation_sdk.py").read_text(encoding="utf-8")
    required_symbols = [
        "class ValidationResult",
        "def validate_execution_manifest_v1",
        "def validate_telemetry_extension_v1",
        "def validate_capability_policy_input_v1",
        "def validate_spec_bundle_v1",
    ]
    for symbol in required_symbols:
        assert symbol in content
