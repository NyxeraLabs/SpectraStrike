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

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from datetime import UTC, datetime

import pytest

from pkg.integration.c2_adapter_hardening import C2DispatchBundle, HardenedC2AdapterBoundary
from pkg.integration.c2_adapter_hardening import C2AdapterHardeningError
from pkg.integration.c2_advanced import (
    C2AdvancedAdapterError,
    HardenedSliverAdapter,
    MythicAdapterScaffold,
    execute_zero_trust_live_session,
)
from pkg.orchestrator.execution_fingerprint import (
    ExecutionFingerprintInput,
    generate_execution_fingerprint,
)
from pkg.orchestrator.ledger_model import RootGenerationCadence
from pkg.orchestrator.merkle_ledger import (
    AppendOnlyMerkleLedger,
    HMACRootSigningAuthority,
    ImmutableExecutionLeafStore,
)


def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _hs256_jws(payload: dict[str, object], secret: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    header_segment = _b64(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_segment = _b64(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_segment}.{payload_segment}".encode("ascii")
    signature = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    return f"{header_segment}.{payload_segment}.{_b64(signature)}"


def _bundle(secret: str = "secret") -> C2DispatchBundle:
    timestamp = datetime.now(UTC).isoformat()
    fingerprint_input = ExecutionFingerprintInput(
        manifest_hash="manifest-hash-002",
        tool_hash="sha256:" + ("a" * 64),
        operator_id="op-001",
        tenant_id="tenant-a",
        policy_decision_hash="policy-allow-002",
        timestamp=timestamp,
    )
    fingerprint = generate_execution_fingerprint(fingerprint_input)
    token = _hs256_jws(
        {
            "execution_fingerprint": fingerprint,
            "policy_decision_hash": "policy-allow-002",
            "target": "urn:host:node-2",
        },
        secret,
    )
    return C2DispatchBundle(
        adapter_name="sliver",
        compact_jws=token,
        execution_fingerprint=fingerprint,
        manifest_hash=fingerprint_input.manifest_hash,
        tool_hash=fingerprint_input.tool_hash,
        operator_id=fingerprint_input.operator_id,
        tenant_id=fingerprint_input.tenant_id,
        policy_decision_hash=fingerprint_input.policy_decision_hash,
        timestamp=fingerprint_input.timestamp,
        target="urn:host:node-2",
        payload={"command": "ls", "target": "10.0.0.8"},
    )


def test_hardened_sliver_adapter_implementation() -> None:
    adapter = HardenedSliverAdapter()
    result = adapter.execute({"command": "whoami", "target": "10.0.0.5"})
    assert result["adapter"] == "sliver"
    assert result["status"] == "accepted"
    assert str(result["session_id"]).startswith("sliver-session-")


def test_mythic_adapter_scaffold_implementation() -> None:
    adapter = MythicAdapterScaffold()
    result = adapter.execute({"target": "10.0.0.11", "operation": "sleep"})
    assert result["adapter"] == "mythic"
    assert result["status"] == "scaffold"
    assert str(result["operation_id"]).startswith("mythic-op-")


def test_integrates_c2_execution_metadata_into_ledger_leaf() -> None:
    sliver = HardenedSliverAdapter()
    boundary = HardenedC2AdapterBoundary(adapters={"sliver": sliver.execute})
    ledger = AppendOnlyMerkleLedger(
        store=ImmutableExecutionLeafStore(),
        signer=HMACRootSigningAuthority(secret=b"s29-secret"),
        root_cadence=RootGenerationCadence(every_n_leaves=1),
    )
    result = execute_zero_trust_live_session(
        boundary=boundary,
        ledger=ledger,
        bundle=_bundle(),
        hmac_secret="secret",
    )
    leaf = ledger._store.records[-1].leaf  # noqa: SLF001 - test verifies persisted metadata
    assert leaf.c2_adapter == "sliver"
    assert leaf.c2_session_id == result.session_id
    assert leaf.c2_operation_id == result.operation_id
    assert leaf.c2_target == "urn:host:node-2"


def test_validates_zero_trust_enforcement_during_live_session() -> None:
    sliver = HardenedSliverAdapter()
    boundary = HardenedC2AdapterBoundary(adapters={"sliver": sliver.execute})
    ledger = AppendOnlyMerkleLedger(
        store=ImmutableExecutionLeafStore(),
        signer=HMACRootSigningAuthority(secret=b"s29-secret"),
    )
    bundle = _bundle()
    forged = C2DispatchBundle(
        adapter_name=bundle.adapter_name,
        compact_jws=bundle.compact_jws[:-1] + "A",
        execution_fingerprint=bundle.execution_fingerprint,
        manifest_hash=bundle.manifest_hash,
        tool_hash=bundle.tool_hash,
        operator_id=bundle.operator_id,
        tenant_id=bundle.tenant_id,
        policy_decision_hash=bundle.policy_decision_hash,
        timestamp=bundle.timestamp,
        target=bundle.target,
        payload=bundle.payload,
    )
    with pytest.raises(C2AdapterHardeningError):
        execute_zero_trust_live_session(
            boundary=boundary,
            ledger=ledger,
            bundle=forged,
            hmac_secret="secret",
        )

    with pytest.raises(C2AdvancedAdapterError):
        sliver.execute({"target": "10.0.0.5"})
