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
from dataclasses import replace
from datetime import UTC, datetime

import pytest

from pkg.integration.c2_adapter_hardening import (
    C2AdapterHardeningError,
    C2DispatchBundle,
    HardenedC2AdapterBoundary,
    simulate_malicious_adapter_payload,
)
from pkg.orchestrator.execution_fingerprint import (
    ExecutionFingerprintInput,
    generate_execution_fingerprint,
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
        manifest_hash="manifest-hash-001",
        tool_hash="sha256:" + ("a" * 64),
        operator_id="op-001",
        tenant_id="tenant-a",
        policy_decision_hash="policy-allow-001",
        timestamp=timestamp,
    )
    fingerprint = generate_execution_fingerprint(fingerprint_input)
    token = _hs256_jws(
        {
            "execution_fingerprint": fingerprint,
            "policy_decision_hash": "policy-allow-001",
            "target": "urn:host:node-1",
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
        target="urn:host:node-1",
        payload={"command": "whoami", "target": "10.0.0.5"},
    )


def test_dispatch_binds_to_unified_execution_fingerprint() -> None:
    boundary = HardenedC2AdapterBoundary(
        adapters={"sliver": lambda payload: {"ok": True, "payload": payload}}
    )
    result = boundary.dispatch(bundle=_bundle(), hmac_secret="secret")
    assert result["ok"] is True


def test_enforces_jws_verification_at_adapter_boundary() -> None:
    boundary = HardenedC2AdapterBoundary(adapters={"sliver": lambda payload: {"ok": True}})
    forged = _bundle()
    forged = replace(forged, compact_jws=forged.compact_jws[:-1] + "A")
    with pytest.raises(C2AdapterHardeningError, match="JWS verification failed"):
        boundary.dispatch(bundle=forged, hmac_secret="secret")


def test_enforces_policy_hash_validation_at_adapter_boundary() -> None:
    boundary = HardenedC2AdapterBoundary(adapters={"sliver": lambda payload: {"ok": True}})
    bundle = _bundle()
    tampered_token = _hs256_jws(
        {
            "execution_fingerprint": bundle.execution_fingerprint,
            "policy_decision_hash": "policy-deny-999",
            "target": bundle.target,
        },
        "secret",
    )
    bad = replace(bundle, compact_jws=tampered_token)
    with pytest.raises(C2AdapterHardeningError, match="policy hash mismatch"):
        boundary.dispatch(bundle=bad, hmac_secret="secret")


def test_isolates_adapters_within_hardened_execution_boundary() -> None:
    boundary = HardenedC2AdapterBoundary(adapters={"sliver": lambda payload: {"ok": True}})
    bundle = _bundle()
    out_of_boundary = replace(bundle, adapter_name="legacy-shell")
    with pytest.raises(C2AdapterHardeningError, match="outside hardened execution boundary"):
        boundary.dispatch(bundle=out_of_boundary, hmac_secret="secret")


def test_simulates_malicious_adapter_behavior_detection() -> None:
    boundary = HardenedC2AdapterBoundary(adapters={"sliver": lambda payload: {"ok": True}})
    malicious_payload = simulate_malicious_adapter_payload()
    bundle = _bundle()
    malicious = replace(bundle, payload=malicious_payload)
    with pytest.raises(C2AdapterHardeningError, match="malicious adapter behavior"):
        boundary.dispatch(bundle=malicious, hmac_secret="secret")
