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

"""Sprint 20 QA checks for high-assurance AAA control artifacts."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_roadmap_marks_sprint20_complete() -> None:
    content = (REPO_ROOT / "docs/ROADMAP.md").read_text(encoding="utf-8")
    section_title = "## Sprint 20 – High-Assurance AAA Controls"
    section_start = content.index(section_title)
    next_section = content.find("\n## Sprint 21", section_start)
    section = content[section_start:next_section]

    assert "- [ ]" not in section, "Sprint 20 contains incomplete roadmap tasks"
    assert "- [x] Enforce hardware-backed MFA for privileged actions" in section
    assert "- [x] Add privileged session recording support" in section


def test_sprint20_pr_templates_exist() -> None:
    template_dir = REPO_ROOT / "docs/dev-logs/sprint-20/pr-templates"
    assert template_dir.exists(), "missing sprint 20 template directory"

    expected = [
        "task-01-hardware-mfa-privileged-actions.md",
        "task-02-dual-control-tool-ingestion.md",
        "task-03-dual-signature-high-risk.md",
        "task-04-break-glass-irreversible-audit.md",
        "task-05-time-bound-elevation-tokens.md",
        "task-06-privileged-session-recording.md",
    ]
    for file_name in expected:
        assert (template_dir / file_name).exists(), f"missing template: {file_name}"


def test_manuals_reference_sprint20_controls() -> None:
    content = (REPO_ROOT / "docs/manuals/ORCHESTRATOR_ARCHITECTURE.md").read_text(
        encoding="utf-8"
    )
    assert "## High-Assurance AAA Controls (Sprint 20)" in content
    assert "Hardware-backed MFA" in content
    assert "dual-signature" in content.lower()
