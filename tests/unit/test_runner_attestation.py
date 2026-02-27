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

from pkg.runner.attestation import (
    EphemeralKeyDeriver,
    MultiTenantIsolationStressValidator,
    MutualAttestationService,
    TPMIdentityProvider,
)


def test_tpm_identity_provider_generates_evidence() -> None:
    provider = TPMIdentityProvider(mode="simulate")

    evidence = provider.issue_identity_evidence(
        quote_nonce="nonce-1",
        tenant_id="tenant-a",
        operator_id="op-001",
    )

    assert evidence.mode == "simulate"
    assert evidence.quote_nonce == "nonce-1"
    assert len(evidence.pcr_digest) == 64
    assert len(evidence.aik_fingerprint) == 64


def test_ephemeral_key_derivation_is_context_bound() -> None:
    deriver = EphemeralKeyDeriver(root_secret=b"x" * 32)

    key_a = deriver.derive_execution_key(
        execution_fingerprint="a" * 64,
        tenant_id="tenant-a",
        operator_id="op-001",
    )
    key_b = deriver.derive_execution_key(
        execution_fingerprint="a" * 64,
        tenant_id="tenant-b",
        operator_id="op-001",
    )

    assert key_a.key_hash != key_b.key_hash
    assert key_a.key_id != key_b.key_id


def test_mutual_attestation_approves_matching_scope() -> None:
    provider = TPMIdentityProvider(mode="simulate")
    deriver = EphemeralKeyDeriver(root_secret=b"x" * 32)
    service = MutualAttestationService()
    evidence = provider.issue_identity_evidence(
        quote_nonce="nonce-1",
        tenant_id="tenant-a",
        operator_id="op-001",
    )
    key = deriver.derive_execution_key(
        execution_fingerprint="a" * 64,
        tenant_id="tenant-a",
        operator_id="op-001",
    )

    result = service.attest(
        quote_nonce="nonce-1",
        tenant_id="tenant-a",
        operator_id="op-001",
        tpm_evidence=evidence,
        ephemeral_key=key,
    )

    assert result.approved is True
    assert result.reason == "approved"
    assert len(result.session_binding_hash) == 64


def test_multi_tenant_stress_validator_detects_cross_tenant_binding_reuse() -> None:
    validator = MultiTenantIsolationStressValidator()

    outcome = validator.validate(
        [
            {"tenant_id": "tenant-a", "session_binding_hash": "abc"},
            {"tenant_id": "tenant-b", "session_binding_hash": "abc"},
        ]
    )

    assert outcome.passed is False
    assert outcome.violation_count == 1
