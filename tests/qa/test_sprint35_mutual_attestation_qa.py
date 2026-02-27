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

"""Sprint 35 QA checks for mutual attestation and key derivation artifacts."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_roadmap_marks_sprint35_complete() -> None:
    content = (REPO_ROOT / "docs/ROADMAP.md").read_text(encoding="utf-8")
    section_title = "## Sprint 35 (Week 67-68): Mutual Attestation & Key Derivation"
    section_start = content.index(section_title)
    section = content[section_start:]

    required_checked = [
        "- [x] Implement TPM-backed identity (on-prem)",
        "- [x] Implement per-execution ephemeral key derivation",
        "- [x] Implement Runner ↔ Control Plane mutual attestation",
        "- [x] Validate multi-tenant stress isolation",
        "- [x] Commit Sprint 35 Mutual Attestation & Isolation Validation",
    ]
    for line in required_checked:
        assert line in section


def test_sprint35_contracts_exist() -> None:
    files = [
        "src/pkg/runner/attestation.py",
        "docs/dev-logs/sprint-35.md",
        "docs/manuals/MUTUAL_ATTESTATION_KEY_DERIVATION.md",
        "tests/unit/test_runner_attestation.py",
    ]
    for relative in files:
        assert (REPO_ROOT / relative).exists(), f"missing sprint35 artifact: {relative}"


def test_attestation_symbols_exist() -> None:
    content = (REPO_ROOT / "src/pkg/runner/attestation.py").read_text(encoding="utf-8")
    required = [
        "class TPMIdentityProvider",
        "class EphemeralKeyDeriver",
        "class MutualAttestationService",
        "class MultiTenantIsolationStressValidator",
    ]
    for symbol in required:
        assert symbol in content
