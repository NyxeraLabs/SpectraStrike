# Copyright (c) 2026 NyxeraLabs
# Author: José María Micoli
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

import pytest

from pkg.runner.jws_verify import JWSVerificationError, RunnerJWSVerifier


def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _hs256_jws(payload: dict[str, object], secret: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    header_segment = _b64(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_segment = _b64(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_segment}.{payload_segment}".encode("ascii")
    signature = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    return f"{header_segment}.{payload_segment}.{_b64(signature)}"


def test_verify_hs256_success() -> None:
    verifier = RunnerJWSVerifier()
    token = _hs256_jws({"task_id": "task-1", "tenant_id": "tenant-a"}, "secret")

    payload = verifier.verify(compact_jws=token, hmac_secret="secret")

    assert payload["task_id"] == "task-1"


def test_verify_hs256_fails_on_forged_signature() -> None:
    verifier = RunnerJWSVerifier()
    token = _hs256_jws({"task_id": "task-1"}, "secret")
    forged = token[:-1] + ("A" if token[-1] != "A" else "B")

    with pytest.raises(JWSVerificationError):
        verifier.verify(compact_jws=forged, hmac_secret="secret")
