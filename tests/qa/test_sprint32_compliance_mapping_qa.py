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

"""Sprint 32 QA checks for compliance mapping and Secure SDLC package."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_roadmap_marks_sprint32_complete() -> None:
    content = (REPO_ROOT / "docs/ROADMAP.md").read_text(encoding="utf-8")
    section_title = "## Sprint 32 (Week 61-62): Compliance Mapping"
    section_start = content.index(section_title)
    next_section = content.find("\n\n## Sprint 33", section_start)
    section = content[section_start:next_section]

    required_checked = [
        "- [x] Map controls to SOC 2",
        "- [x] Map controls to ISO 27001 Annex A",
        "- [x] Map controls to NIST 800-53",
        "- [x] Map telemetry to MITRE ATT&CK",
        "- [x] Produce Secure SDLC documentation package",
        "- [x] Commit Sprint 32 Compliance Mapping",
    ]
    for line in required_checked:
        assert line in section


def test_sprint32_compliance_artifacts_exist() -> None:
    required_paths = [
        "docs/compliance/INDEX.md",
        "docs/compliance/SOC2_CONTROL_MAPPING.md",
        "docs/compliance/ISO27001_ANNEXA_MAPPING.md",
        "docs/compliance/NIST_800_53_MAPPING.md",
        "docs/compliance/MITRE_ATTACK_TELEMETRY_MAPPING.md",
        "docs/compliance/SECURE_SDLC_PACKAGE.md",
    ]
    for relative_path in required_paths:
        absolute = REPO_ROOT / relative_path
        assert absolute.exists(), f"missing sprint 32 artifact: {relative_path}"


def test_compliance_docs_include_required_framework_terms() -> None:
    checks = {
        "docs/compliance/SOC2_CONTROL_MAPPING.md": ["SOC 2", "CC6.1", "CC7.3"],
        "docs/compliance/ISO27001_ANNEXA_MAPPING.md": [
            "ISO/IEC 27001",
            "Annex A",
            "A.8.24",
        ],
        "docs/compliance/NIST_800_53_MAPPING.md": [
            "NIST SP 800-53",
            "AC-3",
            "AU-10",
        ],
        "docs/compliance/MITRE_ATTACK_TELEMETRY_MAPPING.md": [
            "MITRE ATT&CK",
            "T1595",
            "TA0043",
            "execution_fingerprint",
        ],
        "docs/compliance/SECURE_SDLC_PACKAGE.md": [
            "Secure SDLC",
            "make policy-check",
            "scripts/check_license_headers.py",
        ],
    }
    for path, tokens in checks.items():
        content = (REPO_ROOT / path).read_text(encoding="utf-8")
        for token in tokens:
            assert token in content, f"missing token '{token}' in {path}"
