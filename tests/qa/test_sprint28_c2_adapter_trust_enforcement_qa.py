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

"""Sprint 28 QA checks for C2 adapter trust enforcement artifacts."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_roadmap_marks_sprint28_complete_except_commit() -> None:
    content = (REPO_ROOT / "docs/ROADMAP.md").read_text(encoding="utf-8")
    section_title = "## Sprint 28 (Week 53-54): C2 Adapter Trust Enforcement"
    section_start = content.index(section_title)
    next_section = content.find("\n\n## Sprint 29", section_start)
    section = content[section_start:next_section]

    required_checked = [
        "- [x] Bind C2 dispatch to unified execution fingerprint",
        "- [x] Enforce JWS verification at adapter boundary",
        "- [x] Enforce policy hash validation at adapter boundary",
        "- [x] Isolate adapters within hardened execution boundary",
        "- [x] Simulate malicious adapter behavior",
    ]
    for line in required_checked:
        assert line in section
    assert "Commit Sprint 28 C2 Adapter Trust Enforcement" in section


def test_sprint28_contracts_exist() -> None:
    content = (
        REPO_ROOT / "src/pkg/integration/c2_adapter_hardening.py"
    ).read_text(encoding="utf-8")
    required = [
        "class HardenedC2AdapterBoundary",
        "def dispatch(",
        "def _bind_dispatch_to_execution_fingerprint",
        "def _verify_jws",
        "def _enforce_policy_hash_validation",
        "def _enforce_hardened_boundary",
        "def simulate_malicious_adapter_payload",
    ]
    for symbol in required:
        assert symbol in content
