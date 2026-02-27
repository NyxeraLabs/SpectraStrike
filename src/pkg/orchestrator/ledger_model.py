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

"""Phase 6 Sprint 25 Merkle ledger model definitions."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Literal


class LedgerModelError(ValueError):
    """Raised when ledger model definitions are violated."""


@dataclass(slots=True, frozen=True)
class MerkleLeafSchema:
    """Immutable Merkle leaf schema bound to unified execution fingerprint."""

    leaf_index: int
    execution_fingerprint: str
    operator_id: str
    tenant_id: str
    intent_hash: str
    manifest_hash: str
    tool_hash: str
    policy_decision_hash: str
    timestamp: str
    c2_adapter: str = ""
    c2_session_id: str = ""
    c2_operation_id: str = ""
    c2_target: str = ""

    def __post_init__(self) -> None:
        if self.leaf_index < 1:
            raise LedgerModelError("leaf_index must start at 1")
        required = {
            "execution_fingerprint": self.execution_fingerprint,
            "operator_id": self.operator_id,
            "tenant_id": self.tenant_id,
            "intent_hash": self.intent_hash,
            "manifest_hash": self.manifest_hash,
            "tool_hash": self.tool_hash,
            "policy_decision_hash": self.policy_decision_hash,
            "timestamp": self.timestamp,
        }
        for name, value in required.items():
            if not str(value).strip():
                raise LedgerModelError(f"{name} is required")

    def canonical_json(self) -> str:
        """Return canonical payload used for deterministic leaf hashing."""
        return json.dumps(
            {
                "execution_fingerprint": self.execution_fingerprint,
                "intent_hash": self.intent_hash,
                "leaf_index": self.leaf_index,
                "manifest_hash": self.manifest_hash,
                "operator_id": self.operator_id,
                "policy_decision_hash": self.policy_decision_hash,
                "tenant_id": self.tenant_id,
                "timestamp": self.timestamp,
                "tool_hash": self.tool_hash,
                "c2_adapter": self.c2_adapter,
                "c2_session_id": self.c2_session_id,
                "c2_operation_id": self.c2_operation_id,
                "c2_target": self.c2_target,
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )

    def leaf_hash(self) -> str:
        """Compute deterministic leaf hash for Merkle tree ingestion."""
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


@dataclass(slots=True, frozen=True)
class AppendOnlyInsertionOrder:
    """Strict append-only insertion order policy for ledger leaves."""

    sequence_start: int = 1
    contiguous: bool = True

    def validate_next_index(self, *, existing_leaf_count: int, next_leaf_index: int) -> None:
        """Enforce monotonic insertion sequence with no gaps or backfill."""
        expected = existing_leaf_count + self.sequence_start
        if self.contiguous and next_leaf_index != expected:
            raise LedgerModelError(
                f"invalid append order: expected leaf_index {expected}, got {next_leaf_index}"
            )
        if next_leaf_index < expected:
            raise LedgerModelError("invalid append order: backfill insertion is not allowed")


@dataclass(slots=True, frozen=True)
class DeterministicTreeGrowthRules:
    """Deterministic Merkle tree growth behavior definition."""

    hash_algorithm: Literal["sha256"] = "sha256"
    pairing_order: Literal["left-right"] = "left-right"
    odd_leaf_strategy: Literal["duplicate-last"] = "duplicate-last"

    def __post_init__(self) -> None:
        if self.hash_algorithm != "sha256":
            raise LedgerModelError("only sha256 is supported for deterministic growth")
        if self.pairing_order != "left-right":
            raise LedgerModelError("pairing_order must be left-right")
        if self.odd_leaf_strategy != "duplicate-last":
            raise LedgerModelError("odd_leaf_strategy must be duplicate-last")


@dataclass(slots=True, frozen=True)
class RootGenerationCadence:
    """Ledger root generation cadence based on fixed append intervals."""

    every_n_leaves: int = 64

    def __post_init__(self) -> None:
        if self.every_n_leaves < 1:
            raise LedgerModelError("every_n_leaves must be >= 1")

    def should_generate_root(self, *, leaf_count: int) -> bool:
        """Return True when cadence threshold is reached."""
        if leaf_count < 1:
            return False
        return leaf_count % self.every_n_leaves == 0


@dataclass(slots=True, frozen=True)
class RootSigningProcedure:
    """Root signing procedure using control-plane signing authority."""

    authority: str = "control-plane-signing-authority"
    signature_format: Literal["jws"] = "jws"

    def __post_init__(self) -> None:
        if not self.authority.strip():
            raise LedgerModelError("authority is required")
        if self.signature_format != "jws":
            raise LedgerModelError("signature_format must be jws")

    def payload(self, *, merkle_root: str, leaf_count: int, generated_at: str) -> str:
        """Build canonical payload to be signed by control-plane authority."""
        required = {
            "merkle_root": merkle_root,
            "generated_at": generated_at,
        }
        for name, value in required.items():
            if not str(value).strip():
                raise LedgerModelError(f"{name} is required")
        if leaf_count < 1:
            raise LedgerModelError("leaf_count must be >= 1")
        return json.dumps(
            {
                "authority": self.authority,
                "generated_at": generated_at,
                "leaf_count": leaf_count,
                "merkle_root": merkle_root,
                "signature_format": self.signature_format,
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )


ProofDirection = Literal["left", "right"]


@dataclass(slots=True, frozen=True)
class InclusionProofNode:
    """A sibling node in an inclusion proof audit path."""

    direction: ProofDirection
    sibling_hash: str

    def __post_init__(self) -> None:
        if self.direction not in {"left", "right"}:
            raise LedgerModelError("direction must be left or right")
        if not self.sibling_hash.strip():
            raise LedgerModelError("sibling_hash is required")


@dataclass(slots=True, frozen=True)
class InclusionProofStructure:
    """Formal inclusion proof structure contract."""

    leaf_index: int
    leaf_hash: str
    merkle_root: str
    audit_path: tuple[InclusionProofNode, ...]
    root_signature: str
    signature_format: Literal["jws"] = "jws"

    def __post_init__(self) -> None:
        if self.leaf_index < 1:
            raise LedgerModelError("leaf_index must be >= 1")
        required = {
            "leaf_hash": self.leaf_hash,
            "merkle_root": self.merkle_root,
            "root_signature": self.root_signature,
        }
        for name, value in required.items():
            if not str(value).strip():
                raise LedgerModelError(f"{name} is required")
        if self.signature_format != "jws":
            raise LedgerModelError("signature_format must be jws")
        if not self.audit_path:
            raise LedgerModelError("audit_path must contain at least one sibling node")
