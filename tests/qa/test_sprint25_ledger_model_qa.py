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

"""Sprint 25 QA checks for ledger model definition artifacts."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_roadmap_marks_sprint25_definition_complete_except_commit() -> None:
    content = (REPO_ROOT / "docs/ROADMAP.md").read_text(encoding="utf-8")
    section_title = "## Sprint 25 (Week 47-48): Ledger Model Definition"
    section_start = content.index(section_title)
    next_section = content.find("\n\n## Sprint 26", section_start)
    section = content[section_start:next_section]

    required_checked = [
        "- [x] Define Merkle leaf schema using unified execution fingerprint",
        "- [x] Define strict append-only insertion order",
        "- [x] Define deterministic tree growth rules",
        "- [x] Define root generation cadence",
        "- [x] Define root signing procedure",
        "- [x] Define inclusion proof structure",
    ]
    for line in required_checked:
        assert line in section
    assert "Commit Sprint 25 Ledger Model Definition" in section


def test_sprint25_model_module_exists_with_required_contracts() -> None:
    content = (
        REPO_ROOT / "src/pkg/orchestrator/ledger_model.py"
    ).read_text(encoding="utf-8")

    required_symbols = [
        "class MerkleLeafSchema",
        "class AppendOnlyInsertionOrder",
        "class DeterministicTreeGrowthRules",
        "class RootGenerationCadence",
        "class RootSigningProcedure",
        "class InclusionProofStructure",
    ]
    for symbol in required_symbols:
        assert symbol in content
