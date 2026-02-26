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

"""Sprint 22 QA checks for federation fingerprint binding artifacts."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_roadmap_marks_sprint22_complete_except_commit() -> None:
    content = (REPO_ROOT / "docs/ROADMAP.md").read_text(encoding="utf-8")
    section_title = "## Sprint 22 (Week 41-42): Unified Execution Fingerprint Binding"
    section_start = content.index(section_title)
    next_section = content.find("\n## Sprint 23", section_start)
    section = content[section_start:next_section]

    required_checked = [
        "- [x] Define unified execution fingerprint schema:",
        "- [x] Generate fingerprint before dispatch",
        "- [x] Persist fingerprint in tamper-evident audit stream",
        "- [x] Include fingerprint in telemetry payload to VectorVue",
        "- [x] Enforce fingerprint validation before C2 dispatch",
        "- [x] Reject execution if fingerprint mismatch detected",
        "- [x] Add integration tests for fingerprint integrity",
    ]
    for line in required_checked:
        assert line in section
    assert "- [ ] Commit Sprint 22 Unified Execution Fingerprint Binding" in section


def test_sprint22_template_folder_is_complete() -> None:
    template_dir = REPO_ROOT / "docs/dev-logs/sprint-22/pr-templates"
    assert template_dir.exists(), "missing sprint-22 template directory"
    expected = [
        "task-01-fingerprint-schema.md",
        "task-02-generate-before-dispatch.md",
        "task-03-tamper-evident-fingerprint-audit.md",
        "task-04-vectorvue-payload-fingerprint.md",
        "task-05-validate-before-c2-dispatch.md",
        "task-06-reject-fingerprint-mismatch.md",
        "task-07-fingerprint-integration-tests.md",
        "task-08-commit-sprint22.md",
    ]
    for file_name in expected:
        assert (template_dir / file_name).exists(), f"missing template: {file_name}"


def test_bridge_defaults_to_federated_path_with_legacy_compatibility_switch() -> None:
    content = (
        REPO_ROOT / "src/pkg/integration/vectorvue/rabbitmq_bridge.py"
    ).read_text(encoding="utf-8")
    assert "send_federated_telemetry" in content
    assert "allow_legacy_direct_api" in content
