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

"""Sprint 21 QA checks for deterministic manifest guarantees."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_roadmap_marks_sprint21_complete() -> None:
    content = (REPO_ROOT / "docs/ROADMAP.md").read_text(encoding="utf-8")
    section_title = "## Sprint 21 – Deterministic Execution Guarantees"
    section_start = content.index(section_title)
    next_section = content.find("\n---", section_start)
    section = content[section_start:next_section]

    assert "- [ ]" not in section, "Sprint 21 contains incomplete roadmap tasks"
    assert "- [x] Enforce canonical JSON serialization for manifests" in section
    assert "- [x] Reject non-canonical manifest submissions" in section


def test_sprint21_pr_templates_exist() -> None:
    template_dir = REPO_ROOT / "docs/dev-logs/sprint-21/pr-templates"
    assert template_dir.exists(), "missing sprint 21 template directory"
    expected = [
        "task-01-canonical-json-serialization.md",
        "task-02-deterministic-manifest-hash.md",
        "task-03-manifest-schema-semver.md",
        "task-04-schema-regression-ci.md",
        "task-05-reject-non-canonical-submissions.md",
    ]
    for file_name in expected:
        assert (template_dir / file_name).exists(), f"missing template: {file_name}"


def test_ci_pipeline_contains_manifest_regression_step() -> None:
    content = (REPO_ROOT / ".github/workflows/lint-test.yml").read_text(
        encoding="utf-8"
    )
    assert "Run manifest schema regression guard" in content
    assert "scripts/manifest_schema_regression.py" in content
