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

"""Sprint 23 QA checks for federation channel enforcement."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_roadmap_marks_sprint23_complete_except_commit() -> None:
    content = (REPO_ROOT / "docs/ROADMAP.md").read_text(encoding="utf-8")
    section_title = "## Sprint 23 (Week 43-44): Federation Channel Enforcement"
    section_start = content.index(section_title)
    next_section = content.find("\n## Sprint 24", section_start)
    section = content[section_start:next_section]

    required_checked = [
        "- [x] Enforce single outbound telemetry gateway",
        "- [x] Remove any legacy direct API emission paths",
        "- [x] Enforce mTLS-only outbound federation",
        "- [x] Enforce signed telemetry requirement (no unsigned fallback)",
        "- [x] Add replay detection validation at producer side",
        "- [x] Implement bounded retry with idempotent fingerprint key",
        "- [x] Add federation smoke test suite",
    ]
    for line in required_checked:
        assert line in section
    assert "- [ ] Commit Sprint 23 Federation Channel Enforcement" in section


def test_bridge_and_cli_remove_legacy_direct_path() -> None:
    bridge = (
        REPO_ROOT / "src/pkg/integration/vectorvue/rabbitmq_bridge.py"
    ).read_text(encoding="utf-8")
    cli = (
        REPO_ROOT / "src/pkg/integration/vectorvue/sync_from_rabbitmq.py"
    ).read_text(encoding="utf-8")

    assert "send_federated_telemetry" in bridge
    assert "allow_legacy_direct_api" not in bridge
    assert "allow-legacy-direct-api" not in cli


def test_sprint23_template_folder_complete() -> None:
    template_dir = REPO_ROOT / "docs/dev-logs/sprint-23/pr-templates"
    assert template_dir.exists(), "missing sprint-23 template directory"
    expected = [
        "task-01-single-outbound-gateway.md",
        "task-02-remove-legacy-direct-api-paths.md",
        "task-03-mtls-only-federation.md",
        "task-04-signed-telemetry-required.md",
        "task-05-producer-replay-detection.md",
        "task-06-bounded-retry-idempotent-fingerprint.md",
        "task-07-federation-smoke-suite.md",
        "task-08-commit-sprint23.md",
    ]
    for file_name in expected:
        assert (template_dir / file_name).exists(), f"missing template: {file_name}"
