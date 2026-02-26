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

"""Unit tests for Sprint 19 Vault hardening workflows."""

from __future__ import annotations

import pytest

from pkg.orchestrator.vault_hardening import (
    VaultHardeningError,
    VaultHardeningWorkflow,
    VaultUnsealPolicyError,
)


class _FakeSigner:
    def __init__(self, versions: list[int]) -> None:
        self._versions = versions
        self._reads = 0
        self.rotated = False

    def read_signing_key_metadata(self) -> dict[str, object]:
        version = self._versions[self._reads]
        self._reads = min(self._reads + 1, len(self._versions) - 1)
        return {"latest_version": version, "name": "orchestrator-signing"}

    def rotate_signing_key(self) -> dict[str, object]:
        self.rotated = True
        return {}


def test_rotate_transit_key_increments_version() -> None:
    workflow = VaultHardeningWorkflow(_FakeSigner([2, 3]))  # type: ignore[arg-type]

    result = workflow.rotate_transit_key()

    assert result.previous_version == 2
    assert result.rotated_version == 3


def test_rotate_transit_key_fails_when_version_does_not_change() -> None:
    workflow = VaultHardeningWorkflow(_FakeSigner([4, 4]))  # type: ignore[arg-type]

    with pytest.raises(VaultHardeningError):
        workflow.rotate_transit_key()


def test_validate_unseal_shares_enforces_threshold_and_uniqueness() -> None:
    workflow = VaultHardeningWorkflow(_FakeSigner([1, 2]))  # type: ignore[arg-type]

    with pytest.raises(VaultUnsealPolicyError, match="insufficient"):
        workflow.validate_unseal_shares(["share-1", "share-2"])

    with pytest.raises(VaultUnsealPolicyError, match="unique"):
        workflow.validate_unseal_shares(
            [
                "share-1-abcdefghijklmnopqrstuvwxyz",
                "share-1-abcdefghijklmnopqrstuvwxyz",
                "share-3-abcdefghijklmnopqrstuvwxyz",
            ]
        )

    workflow.validate_unseal_shares(
        [
            "share-1-abcdefghijklmnopqrstuvwxyz",
            "share-2-abcdefghijklmnopqrstuvwxyz",
            "share-3-abcdefghijklmnopqrstuvwxyz",
        ]
    )
