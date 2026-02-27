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

"""Unit tests for Sprint 25 Merkle ledger model definitions."""

from __future__ import annotations

import pytest

from pkg.orchestrator.ledger_model import (
    AppendOnlyInsertionOrder,
    DeterministicTreeGrowthRules,
    InclusionProofNode,
    InclusionProofStructure,
    LedgerModelError,
    MerkleLeafSchema,
    RootGenerationCadence,
    RootSigningProcedure,
)


def _sample_leaf(*, index: int = 1) -> MerkleLeafSchema:
    return MerkleLeafSchema(
        leaf_index=index,
        execution_fingerprint="fp-" + ("a" * 60),
        operator_id="op-001",
        tenant_id="tenant-a",
        intent_hash="ih-" + ("b" * 60),
        manifest_hash="mh-" + ("c" * 60),
        tool_hash="sha256:" + ("d" * 64),
        policy_decision_hash="ph-" + ("e" * 60),
        timestamp="2026-02-27T14:00:00+00:00",
    )


def test_merkle_leaf_hash_is_deterministic() -> None:
    first = _sample_leaf()
    second = _sample_leaf()

    assert first.canonical_json() == second.canonical_json()
    assert first.leaf_hash() == second.leaf_hash()
    assert len(first.leaf_hash()) == 64


def test_append_only_order_rejects_gap() -> None:
    policy = AppendOnlyInsertionOrder()
    with pytest.raises(LedgerModelError, match="invalid append order"):
        policy.validate_next_index(existing_leaf_count=2, next_leaf_index=4)


def test_tree_growth_rules_are_strict() -> None:
    DeterministicTreeGrowthRules()
    with pytest.raises(LedgerModelError, match="odd_leaf_strategy"):
        DeterministicTreeGrowthRules(odd_leaf_strategy="carry")


def test_root_generation_cadence_is_interval_based() -> None:
    cadence = RootGenerationCadence(every_n_leaves=3)

    assert cadence.should_generate_root(leaf_count=1) is False
    assert cadence.should_generate_root(leaf_count=2) is False
    assert cadence.should_generate_root(leaf_count=3) is True
    assert cadence.should_generate_root(leaf_count=6) is True


def test_root_signing_payload_is_canonical_and_validated() -> None:
    procedure = RootSigningProcedure()
    payload = procedure.payload(
        merkle_root="root-" + ("f" * 59),
        leaf_count=64,
        generated_at="2026-02-27T15:00:00+00:00",
    )

    assert '"authority":"control-plane-signing-authority"' in payload
    assert '"signature_format":"jws"' in payload
    with pytest.raises(LedgerModelError, match="leaf_count"):
        procedure.payload(
            merkle_root="root-x",
            leaf_count=0,
            generated_at="2026-02-27T15:00:00+00:00",
        )


def test_inclusion_proof_structure_requires_audit_path() -> None:
    node = InclusionProofNode(direction="left", sibling_hash="sib-" + ("a" * 60))
    proof = InclusionProofStructure(
        leaf_index=8,
        leaf_hash=_sample_leaf(index=8).leaf_hash(),
        merkle_root="root-" + ("f" * 59),
        audit_path=(node,),
        root_signature="jws-signature",
    )
    assert proof.signature_format == "jws"

    with pytest.raises(LedgerModelError, match="audit_path"):
        InclusionProofStructure(
            leaf_index=8,
            leaf_hash=_sample_leaf(index=8).leaf_hash(),
            merkle_root="root-" + ("f" * 59),
            audit_path=(),
            root_signature="jws-signature",
        )
