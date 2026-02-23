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

import json
from pathlib import Path

import pytest

from pkg.governance.legal_enforcement import (
    assert_cli_legal_acceptance,
    evaluate_cli_legal_acceptance,
)


def test_self_hosted_blocks_when_acceptance_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SPECTRASTRIKE_ENV", "self-hosted")
    missing_path = Path("/tmp/spectrastrike_missing_acceptance.json")
    if missing_path.exists():
        missing_path.unlink()
    monkeypatch.setenv("SPECTRASTRIKE_LEGAL_ACCEPTANCE_PATH", str(missing_path))

    decision = evaluate_cli_legal_acceptance()
    assert decision.is_compliant is False
    assert decision.reason is not None
    assert "LEGAL_ACCEPTANCE_REQUIRED" in decision.reason


def test_self_hosted_allows_when_versions_match(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("SPECTRASTRIKE_ENV", "self-hosted")
    acceptance_path = tmp_path / "acceptance.json"
    acceptance_path.write_text(
        json.dumps(
            {
                "environment": "self-hosted",
                "installation_id": "installation-1",
                "accepted_documents": {
                    "eula": "2026.1",
                    "aup": "2026.1",
                },
                "accepted_at": "2026-02-23T00:00:00Z",
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("SPECTRASTRIKE_LEGAL_ACCEPTANCE_PATH", str(acceptance_path))

    assert_cli_legal_acceptance()


def test_non_self_hosted_does_not_block_cli(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("SPECTRASTRIKE_ENV", "saas")
    acceptance_path = tmp_path / "acceptance.json"
    acceptance_path.write_text(
        json.dumps(
            {
                "environment": "saas",
                "accepted_documents": {
                    "eula": "2026.1",
                    "aup": "2026.1",
                },
                "accepted_at": "2026-02-23T00:00:00Z",
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("SPECTRASTRIKE_LEGAL_ACCEPTANCE_PATH", str(acceptance_path))

    decision = evaluate_cli_legal_acceptance()
    assert decision.is_compliant is True
