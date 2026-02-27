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

"""Sprint 29 QA checks for advanced C2 implementation artifacts."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_roadmap_marks_sprint29_complete_except_commit() -> None:
    content = (REPO_ROOT / "docs/ROADMAP.md").read_text(encoding="utf-8")
    section_title = "## Sprint 29 (Week 55-56): Advanced C2 Implementations"
    section_start = content.index(section_title)
    next_section = content.find("\n\n# Phase 8", section_start)
    section = content[section_start:next_section]

    required_checked = [
        "- [x] Implement Sliver adapter hardened version",
        "- [x] Implement Mythic adapter scaffold",
        "- [x] Integrate C2 execution metadata into ledger leaf",
        "- [x] Validate zero-trust enforcement during live session",
    ]
    for line in required_checked:
        assert line in section
    assert "Commit Sprint 29 Advanced C2 Implementations" in section


def test_sprint29_contracts_exist() -> None:
    content = (REPO_ROOT / "src/pkg/integration/c2_advanced.py").read_text(
        encoding="utf-8"
    )
    required = [
        "class HardenedSliverAdapter",
        "class MythicAdapterScaffold",
        "def execute_zero_trust_live_session",
        "class C2LiveSessionResult",
    ]
    for symbol in required:
        assert symbol in content
