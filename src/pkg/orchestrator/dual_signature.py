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

"""Dual-signature enforcement for high-risk execution manifests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pkg.orchestrator.jws import CompactJWSGenerator


class DualSignatureError(PermissionError):
    """Raised when dual-signature policy cannot be satisfied."""


@dataclass(slots=True, frozen=True)
class ManifestSignatureBundle:
    """Signature output bundle for manifest endorsement."""

    risk_level: str
    primary_jws: str
    secondary_jws: str | None = None
    dual_signature_required: bool = False


class HighRiskManifestDualSigner:
    """Require two independent signatures for high-risk manifests."""

    def __init__(
        self,
        *,
        primary: CompactJWSGenerator,
        secondary: CompactJWSGenerator | None,
        primary_signer_id: str,
        secondary_signer_id: str | None,
        high_risk_levels: set[str] | None = None,
    ) -> None:
        self._primary = primary
        self._secondary = secondary
        self._primary_signer_id = primary_signer_id.strip()
        self._secondary_signer_id = (secondary_signer_id or "").strip()
        self._high_risk_levels = high_risk_levels or {"high", "critical"}
        if not self._primary_signer_id:
            raise ValueError("primary_signer_id is required")

    def sign(self, payload: dict[str, Any], *, risk_level: str) -> ManifestSignatureBundle:
        """Sign manifest payload with single or dual signature based on risk level."""
        required = risk_level.strip().lower() in self._high_risk_levels
        primary_jws = self._primary.generate(payload)
        if not required:
            return ManifestSignatureBundle(
                risk_level=risk_level,
                primary_jws=primary_jws,
                dual_signature_required=False,
            )

        if self._secondary is None:
            raise DualSignatureError("secondary signer is required for high-risk manifest")
        if not self._secondary_signer_id:
            raise DualSignatureError("secondary_signer_id is required for high-risk")
        if self._primary_signer_id == self._secondary_signer_id:
            raise DualSignatureError("primary and secondary signer identities must differ")

        secondary_jws = self._secondary.generate(payload)
        return ManifestSignatureBundle(
            risk_level=risk_level,
            primary_jws=primary_jws,
            secondary_jws=secondary_jws,
            dual_signature_required=True,
        )
