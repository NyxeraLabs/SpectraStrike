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

"""Sprint 24 QA checks for anti-repudiation closure artifacts."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_roadmap_marks_sprint24_complete_except_commit() -> None:
    content = (REPO_ROOT / "docs/ROADMAP.md").read_text(encoding="utf-8")
    section_title = "## Sprint 24 (Week 45-46): Anti-Repudiation Closure"
    section_start = content.index(section_title)
    next_section = content.find("\n\n# Phase 6", section_start)
    section = content[section_start:next_section]

    required_checked = [
        "- [x] Bind operator identity irreversibly into execution fingerprint",
        "- [x] Enforce pre-dispatch intent record (write-ahead hash entry)",
        "- [x] Implement execution intent verification API",
        "- [x] Add operator-to-execution audit reconciliation test",
        "- [x] Simulate repudiation attempt and validate detection",
    ]
    for line in required_checked:
        assert line in section
    assert "- [ ] Commit Sprint 24 Anti-Repudiation Closure" in section


def test_anti_repudiation_files_and_templates_exist() -> None:
    assert (
        REPO_ROOT / "src/pkg/orchestrator/anti_repudiation.py"
    ).exists(), "missing anti_repudiation module"
    template_dir = REPO_ROOT / "docs/dev-logs/sprint-24/pr-templates"
    assert template_dir.exists(), "missing sprint-24 template directory"
    expected = [
        "task-01-operator-identity-fingerprint-binding.md",
        "task-02-write-ahead-intent-record.md",
        "task-03-execution-intent-verification-api.md",
        "task-04-operator-execution-reconciliation-test.md",
        "task-05-repudiation-simulation-detection.md",
        "task-06-commit-sprint24.md",
    ]
    for file_name in expected:
        assert (template_dir / file_name).exists(), f"missing template: {file_name}"


def test_bridge_contains_write_ahead_intent_metadata() -> None:
    content = (
        REPO_ROOT / "src/pkg/integration/vectorvue/rabbitmq_bridge.py"
    ).read_text(encoding="utf-8")
    assert "record_pre_dispatch_intent" in content
    assert "intent_hash" in content
    assert '"write_ahead" = True' not in content  # guard accidental bad syntax
