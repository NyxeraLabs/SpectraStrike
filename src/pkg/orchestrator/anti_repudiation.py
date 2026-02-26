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

"""Anti-repudiation write-ahead intent ledger and verification API contracts."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from threading import Lock

from pkg.logging.framework import emit_integrity_audit_event


class AntiRepudiationError(ValueError):
    """Raised when anti-repudiation checks fail."""


@dataclass(slots=True, frozen=True)
class ExecutionIntentRecord:
    """Immutable pre-dispatch execution intent write-ahead record."""

    intent_id: str
    execution_fingerprint: str
    operator_id: str
    tenant_id: str
    dispatch_target: str
    manifest_hash: str
    tool_hash: str
    policy_decision_hash: str
    timestamp: str
    prev_hash: str
    intent_hash: str


class ExecutionIntentLedger:
    """Append-only execution intent ledger for anti-repudiation closure."""

    def __init__(self) -> None:
        self._records: list[ExecutionIntentRecord] = []
        self._lock = Lock()

    def record_pre_dispatch_intent(
        self,
        *,
        execution_fingerprint: str,
        operator_id: str,
        tenant_id: str,
        dispatch_target: str,
        manifest_hash: str,
        tool_hash: str,
        policy_decision_hash: str,
        timestamp: str,
    ) -> ExecutionIntentRecord:
        """Write intent record before dispatch, chaining previous ledger hash."""
        required = {
            "execution_fingerprint": execution_fingerprint,
            "operator_id": operator_id,
            "tenant_id": tenant_id,
            "dispatch_target": dispatch_target,
            "manifest_hash": manifest_hash,
            "tool_hash": tool_hash,
            "policy_decision_hash": policy_decision_hash,
            "timestamp": timestamp,
        }
        for name, value in required.items():
            if not str(value).strip():
                raise AntiRepudiationError(f"{name} is required")

        with self._lock:
            prev_hash = self._records[-1].intent_hash if self._records else "GENESIS"
            intent_id = f"intent-{len(self._records) + 1:08d}"
            canonical = json.dumps(
                {
                    "dispatch_target": dispatch_target,
                    "execution_fingerprint": execution_fingerprint,
                    "intent_id": intent_id,
                    "manifest_hash": manifest_hash,
                    "operator_id": operator_id,
                    "policy_decision_hash": policy_decision_hash,
                    "tenant_id": tenant_id,
                    "timestamp": timestamp,
                    "tool_hash": tool_hash,
                },
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            )
            intent_hash = hashlib.sha256(
                f"{prev_hash}:{canonical}".encode("utf-8")
            ).hexdigest()
            record = ExecutionIntentRecord(
                intent_id=intent_id,
                execution_fingerprint=execution_fingerprint,
                operator_id=operator_id,
                tenant_id=tenant_id,
                dispatch_target=dispatch_target,
                manifest_hash=manifest_hash,
                tool_hash=tool_hash,
                policy_decision_hash=policy_decision_hash,
                timestamp=timestamp,
                prev_hash=prev_hash,
                intent_hash=intent_hash,
            )
            self._records.append(record)

        emit_integrity_audit_event(
            action="execution_intent_write_ahead",
            actor=operator_id,
            target=dispatch_target,
            status="success",
            intent_id=record.intent_id,
            execution_fingerprint=execution_fingerprint,
            intent_hash=record.intent_hash,
            prev_hash=record.prev_hash,
        )
        return record

    def verify_execution_intent(
        self,
        *,
        execution_fingerprint: str,
        operator_id: str | None = None,
    ) -> dict[str, str | bool]:
        """Verification API contract for execution intent lookup."""
        with self._lock:
            for record in self._records:
                if record.execution_fingerprint != execution_fingerprint:
                    continue
                if operator_id is not None and record.operator_id != operator_id:
                    raise AntiRepudiationError(
                        "execution fingerprint belongs to different operator"
                    )
                return {
                    "verified": True,
                    "intent_id": record.intent_id,
                    "intent_hash": record.intent_hash,
                    "operator_id": record.operator_id,
                    "tenant_id": record.tenant_id,
                    "dispatch_target": record.dispatch_target,
                    "timestamp": record.timestamp,
                }
        raise AntiRepudiationError("execution fingerprint intent not found")

    def reconcile_operator_to_execution(
        self,
        *,
        operator_id: str,
        execution_fingerprint: str,
    ) -> bool:
        """Verify operator-to-execution reconciliation relation."""
        result = self.verify_execution_intent(
            execution_fingerprint=execution_fingerprint,
            operator_id=operator_id,
        )
        return bool(result.get("verified", False))

    def detect_repudiation_attempt(
        self,
        *,
        claimed_operator_id: str,
        execution_fingerprint: str,
    ) -> bool:
        """Return True when claim does not match immutable execution intent record."""
        try:
            self.verify_execution_intent(
                execution_fingerprint=execution_fingerprint,
                operator_id=claimed_operator_id,
            )
            return False
        except AntiRepudiationError:
            emit_integrity_audit_event(
                action="execution_repudiation_detected",
                actor=claimed_operator_id,
                target="execution-intent",
                status="denied",
                execution_fingerprint=execution_fingerprint,
            )
            return True

    @property
    def records(self) -> list[ExecutionIntentRecord]:
        """Return immutable copy of intent ledger records."""
        with self._lock:
            return list(self._records)


def verify_execution_intent_api(
    ledger: ExecutionIntentLedger,
    *,
    execution_fingerprint: str,
    operator_id: str | None = None,
) -> dict[str, str | bool]:
    """Execution intent verification API handler contract."""
    return ledger.verify_execution_intent(
        execution_fingerprint=execution_fingerprint,
        operator_id=operator_id,
    )
