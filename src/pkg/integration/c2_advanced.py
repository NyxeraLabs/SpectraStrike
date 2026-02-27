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

"""Phase 7 Sprint 29 advanced C2 adapter implementations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pkg.integration.c2_adapter_hardening import (
    C2DispatchBundle,
    HardenedC2AdapterBoundary,
)
from pkg.orchestrator.merkle_ledger import AppendOnlyMerkleLedger, ImmutableExecutionLeafRecord


class C2AdvancedAdapterError(ValueError):
    """Raised when advanced C2 adapter execution fails."""


@dataclass(slots=True, frozen=True)
class C2LiveSessionResult:
    """Normalized live C2 session outcome bound to ledger metadata."""

    adapter_name: str
    session_id: str
    operation_id: str
    status: str
    target: str
    ledger_record_hash: str
    execution_fingerprint: str


class HardenedSliverAdapter:
    """Hardened Sliver adapter implementation over zero-trust boundary."""

    adapter_name = "sliver"

    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        command = str(payload.get("command", "")).strip()
        target = str(payload.get("target", "")).strip()
        if not command:
            raise C2AdvancedAdapterError("sliver command is required")
        if not target:
            raise C2AdvancedAdapterError("sliver target is required")
        return {
            "status": "accepted",
            "adapter": self.adapter_name,
            "session_id": f"sliver-session-{uuid4().hex[:12]}",
            "operation_id": f"sliver-op-{uuid4().hex[:12]}",
            "target": target,
            "command": command,
        }


class MythicAdapterScaffold:
    """Mythic adapter scaffold contract for future command-transport wiring."""

    adapter_name = "mythic"

    def execute(self, payload: dict[str, Any]) -> dict[str, Any]:
        target = str(payload.get("target", "")).strip()
        operation = str(payload.get("operation", "task")).strip() or "task"
        if not target:
            raise C2AdvancedAdapterError("mythic target is required")
        return {
            "status": "scaffold",
            "adapter": self.adapter_name,
            "session_id": f"mythic-session-{uuid4().hex[:12]}",
            "operation_id": f"mythic-op-{uuid4().hex[:12]}",
            "target": target,
            "operation": operation,
        }


def execute_zero_trust_live_session(
    *,
    boundary: HardenedC2AdapterBoundary,
    ledger: AppendOnlyMerkleLedger,
    bundle: C2DispatchBundle,
    hmac_secret: str | None = None,
    public_key_pem: str | None = None,
) -> C2LiveSessionResult:
    """Run live C2 dispatch through hardened boundary and persist ledger metadata."""
    response = boundary.dispatch(
        bundle=bundle,
        hmac_secret=hmac_secret,
        public_key_pem=public_key_pem,
    )
    session_id = str(response.get("session_id", "")).strip()
    operation_id = str(response.get("operation_id", "")).strip()
    adapter = str(response.get("adapter", bundle.adapter_name)).strip()
    status = str(response.get("status", "unknown")).strip() or "unknown"
    if not session_id or not operation_id:
        raise C2AdvancedAdapterError("adapter response missing session metadata")

    record: ImmutableExecutionLeafRecord = ledger.append_execution_leaf(
        execution_fingerprint=bundle.execution_fingerprint,
        operator_id=bundle.operator_id,
        tenant_id=bundle.tenant_id,
        intent_hash=f"intent-{operation_id}",
        manifest_hash=bundle.manifest_hash,
        tool_hash=bundle.tool_hash,
        policy_decision_hash=bundle.policy_decision_hash,
        timestamp=datetime.now(UTC).isoformat(),
        c2_adapter=adapter,
        c2_session_id=session_id,
        c2_operation_id=operation_id,
        c2_target=bundle.target,
    )
    return C2LiveSessionResult(
        adapter_name=adapter,
        session_id=session_id,
        operation_id=operation_id,
        status=status,
        target=bundle.target,
        ledger_record_hash=record.record_hash,
        execution_fingerprint=bundle.execution_fingerprint,
    )
