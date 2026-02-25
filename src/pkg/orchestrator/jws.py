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

"""Compact JWS payload generation for orchestrator manifests."""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from typing import Any

from pkg.orchestrator.signing import ManifestSigner


class JWSPayloadError(ValueError):
    """Raised when JWS generation cannot complete safely."""


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _json_compact(data: dict[str, Any]) -> bytes:
    return json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


def _decode_signer_signature(signature: str) -> bytes:
    if not signature:
        raise JWSPayloadError("signer returned an empty signature")

    encoded = signature
    if signature.startswith("vault:v"):
        parts = signature.split(":", maxsplit=2)
        if len(parts) != 3:
            raise JWSPayloadError("Vault signature format is invalid")
        encoded = parts[2]

    padding = "=" * (-len(encoded) % 4)
    decoders = (
        lambda value: base64.b64decode(value, validate=True),
        lambda value: base64.b64decode(value, altchars=b"-_", validate=True),
    )
    for decoder in decoders:
        try:
            decoded = decoder(encoded + padding)
        except (ValueError, TypeError):
            continue
        if decoded:
            return decoded

    raise JWSPayloadError("unable to decode signer signature")


@dataclass(slots=True, frozen=True)
class JWSConfig:
    """Config for compact JWS generation."""

    algorithm: str = "ES256"
    key_id: str | None = None
    include_typ: bool = True
    typ: str = "JWT"


class CompactJWSGenerator:
    """Generate compact JWS strings for orchestrator execution payloads."""

    def __init__(self, signer: ManifestSigner, config: JWSConfig | None = None) -> None:
        self._signer = signer
        self._config = config or JWSConfig()

    def generate(self, payload: dict[str, Any]) -> str:
        """Build, sign, and return compact JWS: header.payload.signature."""
        if not payload:
            raise JWSPayloadError("payload must not be empty")

        header: dict[str, Any] = {"alg": self._config.algorithm}
        if self._config.include_typ:
            header["typ"] = self._config.typ
        if self._config.key_id:
            header["kid"] = self._config.key_id

        header_segment = _b64url_encode(_json_compact(header))
        payload_segment = _b64url_encode(_json_compact(payload))
        signing_input = f"{header_segment}.{payload_segment}"

        signer_value = self._signer.sign_payload(signing_input.encode("ascii"))
        signature_segment = _b64url_encode(_decode_signer_signature(signer_value))
        return f"{signing_input}.{signature_segment}"
