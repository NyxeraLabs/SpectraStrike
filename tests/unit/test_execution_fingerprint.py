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

"""Unit tests for unified execution fingerprint generation and validation."""

from __future__ import annotations

import pytest

from pkg.orchestrator.execution_fingerprint import (
    ExecutionFingerprintError,
    ExecutionFingerprintInput,
    fingerprint_input_from_envelope,
    generate_operator_bound_execution_fingerprint,
    generate_execution_fingerprint,
    validate_fingerprint_before_c2_dispatch,
)


def _fingerprint_input() -> ExecutionFingerprintInput:
    return ExecutionFingerprintInput(
        manifest_hash="mh-123",
        tool_hash="sha256:" + ("a" * 64),
        operator_id="op-001",
        tenant_id="tenant-a",
        policy_decision_hash="policy-allow-001",
        timestamp="2026-02-26T12:00:00+00:00",
    )


def test_fingerprint_generation_is_deterministic() -> None:
    one = generate_execution_fingerprint(_fingerprint_input())
    two = generate_execution_fingerprint(_fingerprint_input())

    assert one == two
    assert len(one) == 64


def test_validate_before_c2_dispatch_rejects_mismatch() -> None:
    data = _fingerprint_input()
    with pytest.raises(ExecutionFingerprintError, match="mismatch"):
        validate_fingerprint_before_c2_dispatch(
            data=data,
            provided_fingerprint="deadbeef",
            actor="op-001",
            dispatch_target="c2/sliver",
        )


def test_operator_bound_fingerprint_rejects_operator_mismatch() -> None:
    data = _fingerprint_input()
    with pytest.raises(ExecutionFingerprintError, match="operator_id mismatch"):
        generate_operator_bound_execution_fingerprint(data=data, operator_id="op-999")


def test_fingerprint_input_from_envelope_requires_required_fields() -> None:
    with pytest.raises(ExecutionFingerprintError, match="manifest_hash"):
        fingerprint_input_from_envelope(
            actor="op-001",
            timestamp="2026-02-26T12:00:00+00:00",
            attributes={
                "tenant_id": "tenant-a",
                "tool_sha256": "sha256:" + ("a" * 64),
                "policy_decision_hash": "policy-allow-001",
            },
        )
