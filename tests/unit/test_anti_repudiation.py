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

"""Unit tests for Sprint 24 anti-repudiation intent ledger."""

from __future__ import annotations

import pytest

from pkg.orchestrator.anti_repudiation import (
    AntiRepudiationError,
    ExecutionIntentLedger,
    verify_execution_intent_api,
)


def test_record_pre_dispatch_intent_creates_hash_chain() -> None:
    ledger = ExecutionIntentLedger()
    first = ledger.record_pre_dispatch_intent(
        execution_fingerprint="fp-1",
        operator_id="op-001",
        tenant_id="tenant-a",
        dispatch_target="host-a",
        manifest_hash="mh-1",
        tool_hash="sha256:" + ("a" * 64),
        policy_decision_hash="ph-1",
        timestamp="2026-02-26T12:00:00+00:00",
    )
    second = ledger.record_pre_dispatch_intent(
        execution_fingerprint="fp-2",
        operator_id="op-001",
        tenant_id="tenant-a",
        dispatch_target="host-b",
        manifest_hash="mh-2",
        tool_hash="sha256:" + ("b" * 64),
        policy_decision_hash="ph-2",
        timestamp="2026-02-26T12:00:01+00:00",
    )

    assert first.prev_hash == "GENESIS"
    assert second.prev_hash == first.intent_hash


def test_execution_intent_verification_api() -> None:
    ledger = ExecutionIntentLedger()
    record = ledger.record_pre_dispatch_intent(
        execution_fingerprint="fp-verify",
        operator_id="op-001",
        tenant_id="tenant-a",
        dispatch_target="host-a",
        manifest_hash="mh-1",
        tool_hash="sha256:" + ("a" * 64),
        policy_decision_hash="ph-1",
        timestamp="2026-02-26T12:00:00+00:00",
    )

    result = verify_execution_intent_api(
        ledger, execution_fingerprint="fp-verify", operator_id="op-001"
    )

    assert result["verified"] is True
    assert result["intent_id"] == record.intent_id


def test_operator_to_execution_reconciliation() -> None:
    ledger = ExecutionIntentLedger()
    ledger.record_pre_dispatch_intent(
        execution_fingerprint="fp-reconcile",
        operator_id="op-001",
        tenant_id="tenant-a",
        dispatch_target="host-a",
        manifest_hash="mh-1",
        tool_hash="sha256:" + ("a" * 64),
        policy_decision_hash="ph-1",
        timestamp="2026-02-26T12:00:00+00:00",
    )

    assert ledger.reconcile_operator_to_execution(
        operator_id="op-001",
        execution_fingerprint="fp-reconcile",
    )


def test_repudiation_attempt_is_detected() -> None:
    ledger = ExecutionIntentLedger()
    ledger.record_pre_dispatch_intent(
        execution_fingerprint="fp-rep",
        operator_id="op-001",
        tenant_id="tenant-a",
        dispatch_target="host-a",
        manifest_hash="mh-1",
        tool_hash="sha256:" + ("a" * 64),
        policy_decision_hash="ph-1",
        timestamp="2026-02-26T12:00:00+00:00",
    )

    assert ledger.detect_repudiation_attempt(
        claimed_operator_id="op-999",
        execution_fingerprint="fp-rep",
    )

    with pytest.raises(AntiRepudiationError):
        ledger.verify_execution_intent(
            execution_fingerprint="fp-rep",
            operator_id="op-999",
        )
