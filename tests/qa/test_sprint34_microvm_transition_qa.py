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

"""Sprint 34 QA checks for firecracker microVM transition artifacts."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_roadmap_marks_sprint34_complete() -> None:
    content = (REPO_ROOT / "docs/ROADMAP.md").read_text(encoding="utf-8")
    section_title = "## Sprint 34 (Week 65-66): MicroVM Transition"
    section_start = content.index(section_title)
    next_section = content.find("\n\n## Sprint 35", section_start)
    section = content[section_start:next_section]

    required_checked = [
        "- [x] Transition Runner to Firecracker MicroVM",
        "- [x] Implement ephemeral boot optimization",
        "- [x] Implement runtime attestation reporting",
        "- [x] Enforce hardware isolation boundary",
        "- [x] Simulate breakout attempt",
        "- [x] Commit Sprint 34 MicroVM Transition",
    ]
    for line in required_checked:
        assert line in section


def test_sprint34_contracts_exist() -> None:
    files = [
        "src/pkg/runner/firecracker.py",
        "src/pkg/runner/universal.py",
        "docs/manuals/FIRECRACKER_MICROVM_TRANSITION.md",
        "docs/dev-logs/sprint-34.md",
    ]
    for relative in files:
        assert (REPO_ROOT / relative).exists(), f"missing sprint34 artifact: {relative}"


def test_firecracker_symbols_exposed() -> None:
    content = (REPO_ROOT / "src/pkg/runner/firecracker.py").read_text(encoding="utf-8")
    required = [
        "class FirecrackerMicroVMProfile",
        "class RuntimeAttestationReport",
        "class FirecrackerMicroVMRunner",
        "def verify_hardware_isolation_boundary",
        "def build_runtime_attestation_report",
        "def simulate_breakout_attempt",
    ]
    for symbol in required:
        assert symbol in content
