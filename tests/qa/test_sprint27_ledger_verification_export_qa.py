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

"""Sprint 27 QA checks for ledger verification and export artifacts."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_roadmap_marks_sprint27_complete_except_commit() -> None:
    content = (REPO_ROOT / "docs/ROADMAP.md").read_text(encoding="utf-8")
    section_title = "## Sprint 27 (Week 51-52): Ledger Verification & Export"
    section_start = content.index(section_title)
    next_section = content.find("\n\n# Phase 7", section_start)
    section = content[section_start:next_section]

    required_checked = [
        "- [x] Implement inclusion proof API",
        "- [x] Implement deterministic rebuild mode",
        "- [x] Implement ledger snapshot export",
        "- [x] Implement read-only verifier node",
        "- [x] Validate DB tampering detection via root mismatch",
    ]
    for line in required_checked:
        assert line in section
    assert "Commit Sprint 27 Ledger Verification & Export" in section


def test_sprint27_contracts_exist() -> None:
    content = (
        REPO_ROOT / "src/pkg/orchestrator/merkle_ledger.py"
    ).read_text(encoding="utf-8")
    required = [
        "def build_inclusion_proof",
        "def deterministic_rebuild_root",
        "def export_snapshot",
        "class ReadOnlyMerkleVerifierNode",
        "def validate_db_tampering_detection",
    ]
    for symbol in required:
        assert symbol in content
