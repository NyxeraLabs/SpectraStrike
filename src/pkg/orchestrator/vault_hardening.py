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

"""Vault key rotation automation and unseal hardening helpers."""

from __future__ import annotations

from dataclasses import dataclass

from pkg.logging.framework import emit_integrity_audit_event
from pkg.orchestrator.signing import VaultTransitSigner


class VaultHardeningError(RuntimeError):
    """Base error for Vault hardening workflow failures."""


class VaultUnsealPolicyError(VaultHardeningError):
    """Raised when unseal policy validation fails."""


@dataclass(slots=True, frozen=True)
class VaultUnsealPolicy:
    """Unseal security policy for threshold quorum and share quality."""

    total_shares: int = 5
    threshold: int = 3
    minimum_share_length: int = 16
    require_unique_shares: bool = True

    def __post_init__(self) -> None:
        if self.total_shares < 3:
            raise ValueError("total_shares must be at least 3")
        if self.threshold < 3:
            raise ValueError("threshold must be at least 3")
        if self.threshold > self.total_shares:
            raise ValueError("threshold cannot exceed total_shares")
        if self.minimum_share_length < 8:
            raise ValueError("minimum_share_length must be at least 8")


@dataclass(slots=True, frozen=True)
class VaultRotationResult:
    """Result metadata for automated Vault key rotation workflow."""

    key_name: str
    previous_version: int
    rotated_version: int


class VaultHardeningWorkflow:
    """Automate key rotation and enforce hardened unseal procedures."""

    def __init__(
        self,
        signer: VaultTransitSigner,
        *,
        unseal_policy: VaultUnsealPolicy | None = None,
    ) -> None:
        self._signer = signer
        self._unseal_policy = unseal_policy or VaultUnsealPolicy()

    def rotate_transit_key(self) -> VaultRotationResult:
        """Rotate signing key and verify key version increments."""
        before = self._signer.read_signing_key_metadata()
        previous_version = int(before.get("latest_version", 0))

        self._signer.rotate_signing_key()
        after = self._signer.read_signing_key_metadata()
        rotated_version = int(after.get("latest_version", 0))

        if rotated_version <= previous_version:
            emit_integrity_audit_event(
                action="vault_key_rotation",
                actor="orchestrator",
                target="vault-transit",
                status="failed",
                reason="non_incrementing_key_version",
                previous_version=previous_version,
                rotated_version=rotated_version,
            )
            raise VaultHardeningError("Vault key rotation did not increment key version")

        key_name = str(after.get("name") or before.get("name") or "unknown")
        emit_integrity_audit_event(
            action="vault_key_rotation",
            actor="orchestrator",
            target="vault-transit",
            status="success",
            key_name=key_name,
            previous_version=previous_version,
            rotated_version=rotated_version,
        )
        return VaultRotationResult(
            key_name=key_name,
            previous_version=previous_version,
            rotated_version=rotated_version,
        )

    def validate_unseal_shares(self, shares: list[str]) -> None:
        """Enforce hardened unseal quorum and share validation constraints."""
        if len(shares) < self._unseal_policy.threshold:
            raise VaultUnsealPolicyError("insufficient unseal shares for threshold")
        if self._unseal_policy.require_unique_shares and len(set(shares)) != len(shares):
            raise VaultUnsealPolicyError("unseal shares must be unique")

        for share in shares:
            if len(share.strip()) < self._unseal_policy.minimum_share_length:
                raise VaultUnsealPolicyError("unseal share length below policy minimum")

        emit_integrity_audit_event(
            action="vault_unseal_validation",
            actor="orchestrator",
            target="vault-unseal",
            status="success",
            threshold=self._unseal_policy.threshold,
            validated_shares=len(shares),
        )
