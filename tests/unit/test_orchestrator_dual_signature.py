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

"""Unit tests for high-risk manifest dual-signature enforcement."""

from __future__ import annotations

from typing import Any

import pytest

from pkg.orchestrator.dual_signature import (
    DualSignatureError,
    HighRiskManifestDualSigner,
)


class _FakeGenerator:
    def __init__(self, value: str) -> None:
        self.value = value
        self.calls: list[dict[str, Any]] = []

    def generate(self, payload: dict[str, Any]) -> str:
        self.calls.append(payload)
        return self.value


def test_non_high_risk_manifest_uses_single_signature() -> None:
    signer = HighRiskManifestDualSigner(
        primary=_FakeGenerator("jws-primary"),  # type: ignore[arg-type]
        secondary=None,
        primary_signer_id="sig-a",
        secondary_signer_id=None,
    )

    bundle = signer.sign({"task_id": "t1"}, risk_level="medium")

    assert bundle.primary_jws == "jws-primary"
    assert bundle.secondary_jws is None
    assert bundle.dual_signature_required is False


def test_high_risk_manifest_requires_dual_signature() -> None:
    signer = HighRiskManifestDualSigner(
        primary=_FakeGenerator("jws-primary"),  # type: ignore[arg-type]
        secondary=_FakeGenerator("jws-secondary"),  # type: ignore[arg-type]
        primary_signer_id="sig-a",
        secondary_signer_id="sig-b",
    )

    bundle = signer.sign({"task_id": "t2"}, risk_level="critical")

    assert bundle.primary_jws == "jws-primary"
    assert bundle.secondary_jws == "jws-secondary"
    assert bundle.dual_signature_required is True


def test_high_risk_manifest_rejects_same_signer_identity() -> None:
    signer = HighRiskManifestDualSigner(
        primary=_FakeGenerator("jws-primary"),  # type: ignore[arg-type]
        secondary=_FakeGenerator("jws-secondary"),  # type: ignore[arg-type]
        primary_signer_id="sig-a",
        secondary_signer_id="sig-a",
    )

    with pytest.raises(DualSignatureError, match="must differ"):
        signer.sign({"task_id": "t3"}, risk_level="high")
