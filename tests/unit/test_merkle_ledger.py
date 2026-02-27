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

"""Unit tests for Sprint 26 Merkle ledger core implementation."""

from __future__ import annotations

import json
from datetime import UTC, datetime

from pkg.orchestrator.ledger_model import RootGenerationCadence
from pkg.orchestrator.merkle_ledger import (
    AppendOnlyMerkleLedger,
    HMACRootSigningAuthority,
    ImmutableExecutionLeafStore,
    MerkleLedgerError,
    ReadOnlyMerkleVerifierNode,
)


def _append_sample(ledger: AppendOnlyMerkleLedger, *, idx: int) -> None:
    ledger.append_execution_leaf(
        execution_fingerprint=f"fp-{idx:04d}",
        operator_id="op-001",
        tenant_id="tenant-a",
        intent_hash=f"intent-{idx:04d}",
        manifest_hash=f"manifest-{idx:04d}",
        tool_hash="sha256:" + ("a" * 64),
        policy_decision_hash=f"policy-{idx:04d}",
        timestamp=datetime.now(UTC).isoformat(),
    )


def test_append_only_merkle_tree_generates_deterministic_root() -> None:
    store = ImmutableExecutionLeafStore()
    signer = HMACRootSigningAuthority(secret=b"test-secret")
    ledger = AppendOnlyMerkleLedger(store=store, signer=signer)

    _append_sample(ledger, idx=1)
    _append_sample(ledger, idx=2)

    root_one = ledger.merkle_root()
    root_two = ledger.merkle_root()
    assert root_one == root_two
    assert len(root_one) == 64


def test_immutable_execution_leaves_are_persisted(tmp_path) -> None:
    path = tmp_path / "ledger" / "execution_leaves.jsonl"
    signer = HMACRootSigningAuthority(secret=b"persist-secret")
    store = ImmutableExecutionLeafStore(storage_path=path)
    ledger = AppendOnlyMerkleLedger(store=store, signer=signer)
    _append_sample(ledger, idx=1)
    _append_sample(ledger, idx=2)

    reloaded_store = ImmutableExecutionLeafStore(storage_path=path)
    assert len(reloaded_store.records) == 2
    assert reloaded_store.records[0].leaf.leaf_index == 1
    assert reloaded_store.records[1].leaf.leaf_index == 2


def test_periodic_root_generation_and_signing() -> None:
    signer = HMACRootSigningAuthority(secret=b"sign-secret")
    store = ImmutableExecutionLeafStore()
    ledger = AppendOnlyMerkleLedger(
        store=store,
        signer=signer,
        root_cadence=RootGenerationCadence(every_n_leaves=2),
    )

    _append_sample(ledger, idx=1)
    assert len(ledger.signed_roots) == 0
    _append_sample(ledger, idx=2)
    assert len(ledger.signed_roots) == 1

    signed_root = ledger.signed_roots[0]
    assert signed_root.signature.startswith("hmac-sha256:")
    assert ledger.verify_signed_root(signed_root) is True


def test_root_verification_detects_tampered_signature() -> None:
    signer = HMACRootSigningAuthority(secret=b"verify-secret")
    store = ImmutableExecutionLeafStore()
    ledger = AppendOnlyMerkleLedger(store=store, signer=signer)
    _append_sample(ledger, idx=1)
    signed = ledger.generate_and_sign_root(generated_at=datetime.now(UTC).isoformat())
    tampered = signed.__class__(
        root_hash=signed.root_hash,
        leaf_count=signed.leaf_count,
        generated_at=signed.generated_at,
        signature="hmac-sha256:deadbeef",
        authority=signed.authority,
        signature_format=signed.signature_format,
    )
    assert ledger.verify_signed_root(tampered) is False


def test_tamper_simulation_detects_immutable_leaf_mutation(tmp_path) -> None:
    path = tmp_path / "ledger" / "execution_leaves.jsonl"
    signer = HMACRootSigningAuthority(secret=b"tamper-secret")
    store = ImmutableExecutionLeafStore(storage_path=path)
    ledger = AppendOnlyMerkleLedger(store=store, signer=signer)
    _append_sample(ledger, idx=1)

    lines = path.read_text(encoding="utf-8").splitlines()
    payload = json.loads(lines[0])
    payload["leaf"]["tenant_id"] = "tenant-tampered"
    lines[0] = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    try:
        ImmutableExecutionLeafStore(storage_path=path)
    except MerkleLedgerError as exc:
        assert "mismatch" in str(exc)
    else:
        raise AssertionError("expected immutable tamper detection to fail")


def test_inclusion_proof_api_and_snapshot_export(tmp_path) -> None:
    signer = HMACRootSigningAuthority(secret=b"proof-secret")
    store = ImmutableExecutionLeafStore(storage_path=tmp_path / "execution_leaves.jsonl")
    ledger = AppendOnlyMerkleLedger(
        store=store,
        signer=signer,
        root_cadence=RootGenerationCadence(every_n_leaves=2),
    )
    _append_sample(ledger, idx=1)
    _append_sample(ledger, idx=2)

    proof = ledger.build_inclusion_proof(leaf_index=1)
    assert proof.leaf_index == 1
    assert proof.merkle_root == ledger.signed_roots[-1].root_hash
    assert len(proof.audit_path) >= 1

    snapshot = tmp_path / "snapshot.json"
    ledger.export_snapshot(output_path=snapshot)
    assert snapshot.exists()


def test_read_only_verifier_detects_root_mismatch_tampering(tmp_path) -> None:
    signer = HMACRootSigningAuthority(secret=b"verify-node-secret")
    store = ImmutableExecutionLeafStore(storage_path=tmp_path / "execution_leaves.jsonl")
    ledger = AppendOnlyMerkleLedger(
        store=store,
        signer=signer,
        root_cadence=RootGenerationCadence(every_n_leaves=2),
    )
    _append_sample(ledger, idx=1)
    _append_sample(ledger, idx=2)
    snapshot = tmp_path / "snapshot.json"
    ledger.export_snapshot(output_path=snapshot)

    verifier = ReadOnlyMerkleVerifierNode.from_snapshot_file(
        snapshot_path=snapshot,
        signer=signer,
    )
    assert verifier.validate_db_tampering_detection() is False

    tampered_payload = json.loads(snapshot.read_text(encoding="utf-8"))
    tampered_payload["records"][0]["leaf"]["tenant_id"] = "tampered-tenant"
    snapshot.write_text(
        json.dumps(tampered_payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True),
        encoding="utf-8",
    )

    tampered_verifier = ReadOnlyMerkleVerifierNode.from_snapshot_file(
        snapshot_path=snapshot,
        signer=signer,
    )
    assert tampered_verifier.validate_db_tampering_detection() is True
