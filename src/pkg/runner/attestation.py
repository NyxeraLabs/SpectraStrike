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

"""TPM identity, key derivation, and mutual attestation contracts (Sprint 35)."""

from __future__ import annotations

import hashlib
import hmac
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any


class AttestationError(RuntimeError):
    """Raised when attestation or derivation contracts fail."""


@dataclass(slots=True, frozen=True)
class TPMIdentityEvidence:
    """Minimal TPM identity evidence payload for runner identity."""

    mode: str
    quote_nonce: str
    pcr_digest: str
    aik_fingerprint: str
    tenant_id: str
    operator_id: str
    generated_at: str

    def to_dict(self) -> dict[str, str]:
        return {
            "mode": self.mode,
            "quote_nonce": self.quote_nonce,
            "pcr_digest": self.pcr_digest,
            "aik_fingerprint": self.aik_fingerprint,
            "tenant_id": self.tenant_id,
            "operator_id": self.operator_id,
            "generated_at": self.generated_at,
        }


@dataclass(slots=True, frozen=True)
class ExecutionEphemeralKey:
    """Per-execution derived key metadata."""

    key_id: str
    key_hash: str
    algorithm: str
    derived_at: str

    def to_dict(self) -> dict[str, str]:
        return {
            "key_id": self.key_id,
            "key_hash": self.key_hash,
            "algorithm": self.algorithm,
            "derived_at": self.derived_at,
        }


@dataclass(slots=True, frozen=True)
class MutualAttestationResult:
    """Runner-control-plane mutual attestation decision contract."""

    approved: bool
    reason: str
    session_binding_hash: str

    def to_dict(self) -> dict[str, str | bool]:
        return {
            "approved": self.approved,
            "reason": self.reason,
            "session_binding_hash": self.session_binding_hash,
        }


@dataclass(slots=True, frozen=True)
class IsolationStressResult:
    """Multi-tenant isolation stress check summary."""

    total_records: int
    violation_count: int
    passed: bool


class TPMIdentityProvider:
    """TPM identity evidence provider with deterministic simulation mode."""

    def __init__(self, *, mode: str = "simulate") -> None:
        if mode not in {"simulate", "native"}:
            raise AttestationError("TPM mode must be simulate or native")
        self._mode = mode

    def issue_identity_evidence(
        self,
        *,
        quote_nonce: str,
        tenant_id: str,
        operator_id: str,
    ) -> TPMIdentityEvidence:
        if not quote_nonce.strip():
            raise AttestationError("quote_nonce is required")
        if not tenant_id.strip() or not operator_id.strip():
            raise AttestationError("tenant_id and operator_id are required")

        seed = f"{self._mode}|{quote_nonce}|{tenant_id}|{operator_id}"
        pcr_digest = hashlib.sha256(f"pcr|{seed}".encode("utf-8")).hexdigest()
        aik_fingerprint = hashlib.sha256(f"aik|{seed}".encode("utf-8")).hexdigest()
        return TPMIdentityEvidence(
            mode=self._mode,
            quote_nonce=quote_nonce,
            pcr_digest=pcr_digest,
            aik_fingerprint=aik_fingerprint,
            tenant_id=tenant_id,
            operator_id=operator_id,
            generated_at=datetime.now(UTC).isoformat(),
        )


class EphemeralKeyDeriver:
    """Per-execution ephemeral key derivation using HMAC-SHA256."""

    def __init__(self, *, root_secret: bytes | None = None) -> None:
        self._root_secret = root_secret or os.urandom(32)
        if len(self._root_secret) < 16:
            raise AttestationError("root_secret must be at least 16 bytes")

    def derive_execution_key(
        self,
        *,
        execution_fingerprint: str,
        tenant_id: str,
        operator_id: str,
    ) -> ExecutionEphemeralKey:
        if not execution_fingerprint.strip():
            raise AttestationError("execution_fingerprint is required")
        context = f"{execution_fingerprint}|{tenant_id}|{operator_id}".encode("utf-8")
        key_hash = hmac.new(self._root_secret, context, hashlib.sha256).hexdigest()
        key_id = hashlib.sha256(f"key-id|{key_hash}".encode("utf-8")).hexdigest()[:24]
        return ExecutionEphemeralKey(
            key_id=key_id,
            key_hash=key_hash,
            algorithm="HMAC-SHA256",
            derived_at=datetime.now(UTC).isoformat(),
        )


class MutualAttestationService:
    """Runner-control-plane mutual attestation decision service."""

    def __init__(self, *, control_plane_identity: str = "spectrastrike-control-plane") -> None:
        if not control_plane_identity.strip():
            raise AttestationError("control_plane_identity is required")
        self._control_plane_identity = control_plane_identity

    def attest(
        self,
        *,
        quote_nonce: str,
        tenant_id: str,
        operator_id: str,
        tpm_evidence: TPMIdentityEvidence,
        ephemeral_key: ExecutionEphemeralKey,
    ) -> MutualAttestationResult:
        if tpm_evidence.quote_nonce != quote_nonce:
            return MutualAttestationResult(
                approved=False,
                reason="nonce_mismatch",
                session_binding_hash="",
            )
        if tpm_evidence.tenant_id != tenant_id or tpm_evidence.operator_id != operator_id:
            return MutualAttestationResult(
                approved=False,
                reason="identity_scope_mismatch",
                session_binding_hash="",
            )

        binding_input = (
            f"{self._control_plane_identity}|{quote_nonce}|{tenant_id}|"
            f"{operator_id}|{tpm_evidence.pcr_digest}|{ephemeral_key.key_id}"
        )
        session_binding_hash = hashlib.sha256(binding_input.encode("utf-8")).hexdigest()
        return MutualAttestationResult(
            approved=True,
            reason="approved",
            session_binding_hash=session_binding_hash,
        )


class MultiTenantIsolationStressValidator:
    """Validate tenant isolation invariants across mutual-attestation records."""

    def validate(self, records: list[dict[str, Any]]) -> IsolationStressResult:
        binding_to_tenant: dict[str, str] = {}
        violations = 0
        for record in records:
            tenant_id = str(record.get("tenant_id", "")).strip()
            binding = str(record.get("session_binding_hash", "")).strip()
            if not tenant_id or not binding:
                violations += 1
                continue
            existing = binding_to_tenant.get(binding)
            if existing and existing != tenant_id:
                violations += 1
            else:
                binding_to_tenant[binding] = tenant_id
        total = len(records)
        return IsolationStressResult(
            total_records=total,
            violation_count=violations,
            passed=violations == 0,
        )
