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

"""Unit tests for orchestrator compact JWS generation."""

from __future__ import annotations

import base64
import json

import pytest

from pkg.orchestrator.jws import CompactJWSGenerator, JWSConfig, JWSPayloadError


def _b64url_decode(segment: str) -> bytes:
    return base64.urlsafe_b64decode(segment + "=" * (-len(segment) % 4))


class FakeSigner:
    def __init__(self, signer_value: str) -> None:
        self.signer_value = signer_value
        self.last_input: bytes | None = None

    def sign_payload(self, payload: bytes) -> str:
        self.last_input = payload
        return self.signer_value

    def read_public_key(self, key_version: int | None = None) -> str:
        del key_version
        return "pem"


class FakeAuthorizer:
    def __init__(self, should_raise: bool = False) -> None:
        self.should_raise = should_raise
        self.last_payload: dict[str, object] | None = None

    def authorize(self, payload: dict[str, object]) -> None:
        self.last_payload = payload
        if self.should_raise:
            raise PermissionError("denied")


def test_generate_compact_jws_with_vault_signature_prefix() -> None:
    signer = FakeSigner("vault:v1:AQI")
    generator = CompactJWSGenerator(
        signer=signer,
        config=JWSConfig(algorithm="ES256", key_id="transit:signing:v1"),
    )

    token = generator.generate({"target_urn": "urn:target:ip:10.0.0.5", "tool": "nmap"})

    segments = token.split(".")
    assert len(segments) == 3
    header = json.loads(_b64url_decode(segments[0]).decode("utf-8"))
    payload = json.loads(_b64url_decode(segments[1]).decode("utf-8"))
    assert header == {"alg": "ES256", "kid": "transit:signing:v1", "typ": "JWT"}
    assert payload == {"target_urn": "urn:target:ip:10.0.0.5", "tool": "nmap"}
    assert segments[2] == "AQI"
    assert signer.last_input == f"{segments[0]}.{segments[1]}".encode("ascii")


def test_generate_compact_jws_accepts_plain_base64_signature() -> None:
    signature = base64.b64encode(b"\x01\x02\x03").decode("ascii")
    signer = FakeSigner(signature)
    generator = CompactJWSGenerator(signer=signer)

    token = generator.generate({"a": 1})

    assert token.split(".")[2] == "AQID"


def test_generate_rejects_empty_payload() -> None:
    signer = FakeSigner("vault:v1:AQI")
    generator = CompactJWSGenerator(signer=signer)

    with pytest.raises(JWSPayloadError, match="must not be empty"):
        generator.generate({})


def test_generate_rejects_invalid_signer_signature() -> None:
    signer = FakeSigner("vault:v1:@@bad@@")
    generator = CompactJWSGenerator(signer=signer)

    with pytest.raises(JWSPayloadError, match="unable to decode"):
        generator.generate({"target_urn": "urn:target:ip:10.0.0.5"})


def test_generate_calls_pre_execution_authorizer() -> None:
    signer = FakeSigner("vault:v1:AQI")
    authorizer = FakeAuthorizer()
    generator = CompactJWSGenerator(signer=signer, pre_execution_authorizer=authorizer)

    payload = {"target_urn": "urn:target:ip:10.0.0.5", "tool": "nmap"}
    token = generator.generate(payload)

    assert token
    assert authorizer.last_payload == payload


def test_generate_raises_when_pre_execution_authorizer_denies() -> None:
    signer = FakeSigner("vault:v1:AQI")
    authorizer = FakeAuthorizer(should_raise=True)
    generator = CompactJWSGenerator(signer=signer, pre_execution_authorizer=authorizer)

    with pytest.raises(PermissionError, match="denied"):
        generator.generate({"target_urn": "urn:target:ip:10.0.0.5", "tool": "nmap"})
