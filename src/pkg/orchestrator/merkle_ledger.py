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

"""Phase 6 Sprint 26 append-only Merkle ledger core implementation."""

from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock
from typing import Protocol

from pkg.logging.framework import emit_integrity_audit_event
from .ledger_model import (
    AppendOnlyInsertionOrder,
    DeterministicTreeGrowthRules,
    LedgerModelError,
    MerkleLeafSchema,
    RootGenerationCadence,
    RootSigningProcedure,
)


class MerkleLedgerError(ValueError):
    """Raised when append-only Merkle ledger operations fail."""


class RootSigningAuthority(Protocol):
    """Control-plane signing authority contract for Merkle roots."""

    def sign_payload(self, payload: bytes) -> str:
        """Sign root payload bytes."""

    def verify_payload(self, payload: bytes, signature: str) -> bool:
        """Verify root signature for payload bytes."""


@dataclass(slots=True, frozen=True)
class ImmutableExecutionLeafRecord:
    """Persisted immutable execution leaf entry."""

    leaf: MerkleLeafSchema
    leaf_hash: str
    prev_record_hash: str
    record_hash: str


@dataclass(slots=True, frozen=True)
class SignedMerkleRoot:
    """Signed root snapshot for a ledger checkpoint."""

    root_hash: str
    leaf_count: int
    generated_at: str
    signature: str
    authority: str
    signature_format: str


class HMACRootSigningAuthority:
    """Deterministic local signing authority used for root signing workflows."""

    def __init__(self, *, secret: bytes) -> None:
        if not secret:
            raise MerkleLedgerError("secret is required")
        self._secret = secret

    def sign_payload(self, payload: bytes) -> str:
        digest = hmac.new(self._secret, payload, hashlib.sha256).hexdigest()
        return f"hmac-sha256:{digest}"

    def verify_payload(self, payload: bytes, signature: str) -> bool:
        if not signature.startswith("hmac-sha256:"):
            return False
        expected = self.sign_payload(payload)
        return hmac.compare_digest(expected, signature)


class ImmutableExecutionLeafStore:
    """Immutable append-only persistence for execution leaves."""

    def __init__(self, *, storage_path: Path | None = None) -> None:
        self._storage_path = storage_path
        self._records: list[ImmutableExecutionLeafRecord] = []
        self._lock = RLock()
        if storage_path is not None and storage_path.exists():
            self._load_from_disk()

    def _load_from_disk(self) -> None:
        assert self._storage_path is not None
        loaded: list[ImmutableExecutionLeafRecord] = []
        for line in self._storage_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            payload = json.loads(line)
            leaf = MerkleLeafSchema(**payload["leaf"])
            record = ImmutableExecutionLeafRecord(
                leaf=leaf,
                leaf_hash=str(payload["leaf_hash"]),
                prev_record_hash=str(payload["prev_record_hash"]),
                record_hash=str(payload["record_hash"]),
            )
            loaded.append(record)
        self._records = loaded
        self.verify_immutable_chain()

    def append(self, leaf: MerkleLeafSchema) -> ImmutableExecutionLeafRecord:
        """Persist immutable leaf record in append-only order."""
        with self._lock:
            prev_record_hash = self._records[-1].record_hash if self._records else "GENESIS"
            leaf_hash = leaf.leaf_hash()
            canonical = json.dumps(
                {
                    "leaf": json.loads(leaf.canonical_json()),
                    "leaf_hash": leaf_hash,
                    "prev_record_hash": prev_record_hash,
                },
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            )
            record_hash = hashlib.sha256(
                f"{prev_record_hash}:{canonical}".encode("utf-8")
            ).hexdigest()
            record = ImmutableExecutionLeafRecord(
                leaf=leaf,
                leaf_hash=leaf_hash,
                prev_record_hash=prev_record_hash,
                record_hash=record_hash,
            )
            self._records.append(record)
            if self._storage_path is not None:
                self._storage_path.parent.mkdir(parents=True, exist_ok=True)
                row = {
                    "leaf": asdict(leaf),
                    "leaf_hash": leaf_hash,
                    "prev_record_hash": prev_record_hash,
                    "record_hash": record_hash,
                }
                with self._storage_path.open("a", encoding="utf-8") as handle:
                    handle.write(
                        json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
                        + "\n"
                    )
            return record

    def verify_immutable_chain(self) -> None:
        """Fail when immutable record chain or leaf hash integrity is broken."""
        prev_hash = "GENESIS"
        for record in self._records:
            if record.prev_record_hash != prev_hash:
                raise MerkleLedgerError("immutable leaf chain mismatch detected")
            if record.leaf.leaf_hash() != record.leaf_hash:
                raise MerkleLedgerError("immutable leaf hash mismatch detected")
            canonical = json.dumps(
                {
                    "leaf": json.loads(record.leaf.canonical_json()),
                    "leaf_hash": record.leaf_hash,
                    "prev_record_hash": record.prev_record_hash,
                },
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            )
            computed = hashlib.sha256(
                f"{record.prev_record_hash}:{canonical}".encode("utf-8")
            ).hexdigest()
            if computed != record.record_hash:
                raise MerkleLedgerError("immutable record hash mismatch detected")
            prev_hash = record.record_hash

    @property
    def records(self) -> list[ImmutableExecutionLeafRecord]:
        """Return immutable copy of persisted records."""
        with self._lock:
            return list(self._records)


class AppendOnlyMerkleLedger:
    """Append-only Merkle tree runtime with periodic signed root generation."""

    def __init__(
        self,
        *,
        store: ImmutableExecutionLeafStore,
        signer: RootSigningAuthority,
        insertion_order: AppendOnlyInsertionOrder | None = None,
        growth_rules: DeterministicTreeGrowthRules | None = None,
        root_cadence: RootGenerationCadence | None = None,
        signing_procedure: RootSigningProcedure | None = None,
    ) -> None:
        self._store = store
        self._signer = signer
        self._insertion_order = insertion_order or AppendOnlyInsertionOrder()
        self._growth_rules = growth_rules or DeterministicTreeGrowthRules()
        self._root_cadence = root_cadence or RootGenerationCadence()
        self._signing_procedure = signing_procedure or RootSigningProcedure()
        self._signed_roots: list[SignedMerkleRoot] = []
        self._lock = RLock()

    def append_execution_leaf(
        self,
        *,
        execution_fingerprint: str,
        operator_id: str,
        tenant_id: str,
        intent_hash: str,
        manifest_hash: str,
        tool_hash: str,
        policy_decision_hash: str,
        timestamp: str,
    ) -> ImmutableExecutionLeafRecord:
        """Append immutable leaf and trigger periodic root generation."""
        with self._lock:
            next_index = len(self._store.records) + 1
            self._insertion_order.validate_next_index(
                existing_leaf_count=len(self._store.records),
                next_leaf_index=next_index,
            )
            leaf = MerkleLeafSchema(
                leaf_index=next_index,
                execution_fingerprint=execution_fingerprint,
                operator_id=operator_id,
                tenant_id=tenant_id,
                intent_hash=intent_hash,
                manifest_hash=manifest_hash,
                tool_hash=tool_hash,
                policy_decision_hash=policy_decision_hash,
                timestamp=timestamp,
            )
            record = self._store.append(leaf)
            if self._root_cadence.should_generate_root(leaf_count=len(self._store.records)):
                self.generate_and_sign_root(
                    generated_at=datetime.now(UTC).isoformat(),
                )
            return record

    def merkle_root(self, *, leaf_count: int | None = None) -> str:
        """Compute deterministic Merkle root over persisted leaf hashes."""
        leaf_hashes = [record.leaf_hash for record in self._store.records]
        if leaf_count is not None:
            if leaf_count < 1 or leaf_count > len(leaf_hashes):
                raise MerkleLedgerError("leaf_count out of range for merkle_root")
            leaf_hashes = leaf_hashes[:leaf_count]
        if not leaf_hashes:
            raise MerkleLedgerError("cannot compute merkle_root without leaves")

        if self._growth_rules.hash_algorithm != "sha256":
            raise LedgerModelError("only sha256 tree growth is supported")

        level = list(leaf_hashes)
        while len(level) > 1:
            if len(level) % 2 == 1:
                level.append(level[-1])
            next_level: list[str] = []
            for i in range(0, len(level), 2):
                left = level[i]
                right = level[i + 1]
                combined = f"{left}:{right}".encode("utf-8")
                next_level.append(hashlib.sha256(combined).hexdigest())
            level = next_level
        return level[0]

    def generate_and_sign_root(self, *, generated_at: str) -> SignedMerkleRoot:
        """Generate root checkpoint and sign with control-plane authority."""
        with self._lock:
            leaf_count = len(self._store.records)
            root_hash = self.merkle_root()
            payload = self._signing_procedure.payload(
                merkle_root=root_hash,
                leaf_count=leaf_count,
                generated_at=generated_at,
            )
            signature = self._signer.sign_payload(payload.encode("utf-8"))
            signed = SignedMerkleRoot(
                root_hash=root_hash,
                leaf_count=leaf_count,
                generated_at=generated_at,
                signature=signature,
                authority=self._signing_procedure.authority,
                signature_format=self._signing_procedure.signature_format,
            )
            self._signed_roots.append(signed)
            emit_integrity_audit_event(
                action="merkle_root_sign",
                actor=self._signing_procedure.authority,
                target="merkle-ledger",
                status="success",
                root_hash=root_hash,
                leaf_count=leaf_count,
            )
            return signed

    def verify_signed_root(self, signed_root: SignedMerkleRoot) -> bool:
        """Verify root hash and control-plane signature integrity."""
        expected_root = self.merkle_root(leaf_count=signed_root.leaf_count)
        if expected_root != signed_root.root_hash:
            emit_integrity_audit_event(
                action="merkle_root_verify",
                actor=self._signing_procedure.authority,
                target="merkle-ledger",
                status="denied",
                reason="root-hash-mismatch",
                expected_root=expected_root,
                provided_root=signed_root.root_hash,
            )
            return False

        payload = self._signing_procedure.payload(
            merkle_root=signed_root.root_hash,
            leaf_count=signed_root.leaf_count,
            generated_at=signed_root.generated_at,
        )
        signature_valid = self._signer.verify_payload(
            payload.encode("utf-8"),
            signed_root.signature,
        )
        emit_integrity_audit_event(
            action="merkle_root_verify",
            actor=self._signing_procedure.authority,
            target="merkle-ledger",
            status="success" if signature_valid else "denied",
            leaf_count=signed_root.leaf_count,
            root_hash=signed_root.root_hash,
        )
        return signature_valid

    @property
    def signed_roots(self) -> list[SignedMerkleRoot]:
        """Return immutable copy of signed root checkpoints."""
        with self._lock:
            return list(self._signed_roots)
