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

"""Sprint 26 QA checks for ledger core implementation artifacts."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_roadmap_marks_sprint26_complete_except_commit() -> None:
    content = (REPO_ROOT / "docs/ROADMAP.md").read_text(encoding="utf-8")
    section_title = "## Sprint 26 (Week 49-50): Ledger Core Implementation"
    section_start = content.index(section_title)
    next_section = content.find("\n\n## Sprint 27", section_start)
    section = content[section_start:next_section]

    required_checked = [
        "- [x] Implement append-only Merkle tree",
        "- [x] Persist immutable execution leaves",
        "- [x] Implement periodic root generation",
        "- [x] Sign root with Control Plane signing authority",
        "- [x] Implement root verification routine",
        "- [x] Add tamper simulation test",
    ]
    for line in required_checked:
        assert line in section
    assert "Commit Sprint 26 Ledger Core Implementation" in section


def test_sprint26_core_module_exists_with_required_contracts() -> None:
    content = (
        REPO_ROOT / "src/pkg/orchestrator/merkle_ledger.py"
    ).read_text(encoding="utf-8")

    required_symbols = [
        "class ImmutableExecutionLeafStore",
        "class AppendOnlyMerkleLedger",
        "def generate_and_sign_root",
        "def verify_signed_root",
    ]
    for symbol in required_symbols:
        assert symbol in content
