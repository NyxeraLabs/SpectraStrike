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

"""Sprint 19 QA checks for control-plane integrity hardening artifacts."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_roadmap_marks_sprint19_complete() -> None:
    content = (REPO_ROOT / "docs/ROADMAP.md").read_text(encoding="utf-8")
    section_title = "## Sprint 19 – Control Plane Integrity Hardening"
    section_start = content.index(section_title)
    next_section = content.find("\n## Sprint 20", section_start)
    section = content[section_start:next_section]

    assert "- [ ]" not in section, "Sprint 19 contains incomplete roadmap tasks"
    assert "- [x] Implement signed configuration enforcement (JWS-based)" in section
    assert "- [x] Implement immutable configuration version history" in section


def test_sprint19_dev_log_and_templates_exist() -> None:
    sprint_log = REPO_ROOT / "docs/dev-logs/sprint-19.md"
    assert sprint_log.exists(), "missing sprint 19 engineering log"

    template_dir = REPO_ROOT / "docs/dev-logs/sprint-19/pr-templates"
    assert template_dir.exists(), "missing sprint 19 pr templates directory"

    expected = [
        "task-01-signed-config-enforcement.md",
        "task-02-reject-unsigned-config.md",
        "task-03-opa-policy-hash-pinning.md",
        "task-04-policy-hash-mismatch-detection.md",
        "task-05-vault-key-rotation-workflow.md",
        "task-06-vault-unseal-hardening.md",
        "task-07-runtime-binary-baseline.md",
        "task-08-integrity-audit-channel.md",
        "task-09-immutable-config-history.md",
    ]
    for file_name in expected:
        assert (template_dir / file_name).exists(), f"missing template: {file_name}"


def test_orchestrator_architecture_includes_sprint19_controls() -> None:
    content = (REPO_ROOT / "docs/manuals/ORCHESTRATOR_ARCHITECTURE.md").read_text(
        encoding="utf-8"
    )
    assert "## Control Plane Integrity Hardening (Sprint 19)" in content
    assert "OPA_POLICY_PINNED_SHA256" in content
    assert "spectrastrike.audit.integrity" in content
