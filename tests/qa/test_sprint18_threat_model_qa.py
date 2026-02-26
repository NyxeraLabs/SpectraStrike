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

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_threat_model_v1_contains_stride_and_boundaries() -> None:
    path = REPO_ROOT / "docs/THREAT_MODEL.md"
    content = path.read_text(encoding="utf-8")

    required_snippets = [
        "SpectraStrike Threat Model v1.0 (Sprint 18)",
        "Methodology: STRIDE",
        "## 2. Trust Boundary Diagram",
        "Boundary A: Untrusted human input into Control Plane.",
        "### 3.1 Malicious Operator Scenarios",
        "### 3.2 Compromised Runner Scenarios",
        "### 3.3 Supply-Chain Compromise Scenarios",
        "### 3.4 Cross-Tenant Escalation Scenarios",
    ]
    for snippet in required_snippets:
        assert snippet in content, f"missing threat model content: {snippet}"


def test_sprint18_risk_backlog_has_expected_entries() -> None:
    path = REPO_ROOT / "docs/RISK_BACKLOG.md"
    content = path.read_text(encoding="utf-8")

    required_ids = [
        "RISK-S18-001",
        "RISK-S18-002",
        "RISK-S18-003",
        "RISK-S18-004",
        "RISK-S18-005",
        "RISK-S18-006",
    ]
    for risk_id in required_ids:
        assert risk_id in content, f"missing risk backlog entry: {risk_id}"


def test_sprint18_pr_templates_exist() -> None:
    directory = REPO_ROOT / "docs/dev-logs/sprint-18/pr-templates"
    assert directory.exists(), "missing sprint-18 pr templates directory"

    expected_files = [
        "task-01-stride-threat-model.md",
        "task-02-trust-boundary-diagram.md",
        "task-03-malicious-operator-scenarios.md",
        "task-04-compromised-runner-scenarios.md",
        "task-05-supply-chain-scenarios.md",
        "task-06-cross-tenant-scenarios.md",
        "task-07-threat-mitigation-mapping.md",
        "task-08-unresolved-risk-backlog.md",
        "task-09-commit-threat-model-v1.md",
    ]

    for file_name in expected_files:
        path = directory / file_name
        assert path.exists(), f"missing sprint-18 pr template: {file_name}"
