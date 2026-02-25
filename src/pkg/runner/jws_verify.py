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

"""Runner-side JWS verification for signed execution manifests."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from dataclasses import dataclass
from typing import Any, Protocol


class JWSVerificationError(ValueError):
    """Raised when JWS payload fails cryptographic or structural verification."""


class PublicKeyVerifier(Protocol):
    """Protocol for pluggable asymmetric verification backends."""

    def verify(
        self, *, signing_input: bytes, signature: bytes, public_key_pem: str
    ) -> bool:
        """Verify detached signature over signing input."""


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + padding).encode("ascii"))


@dataclass(slots=True)
class RunnerJWSVerifier:
    """Compact JWS verifier supporting HS256 and pluggable ES256 verifier."""

    es256_verifier: PublicKeyVerifier | None = None

    def verify(
        self,
        *,
        compact_jws: str,
        hmac_secret: str | None = None,
        public_key_pem: str | None = None,
    ) -> dict[str, Any]:
        """Verify compact JWS and return decoded payload mapping."""
        parts = compact_jws.split(".")
        if len(parts) != 3:
            raise JWSVerificationError("compact JWS must have three segments")
        header_segment, payload_segment, signature_segment = parts

        try:
            header = json.loads(_b64url_decode(header_segment).decode("utf-8"))
            payload = json.loads(_b64url_decode(payload_segment).decode("utf-8"))
            signature = _b64url_decode(signature_segment)
        except (ValueError, json.JSONDecodeError) as exc:
            raise JWSVerificationError("invalid JWS encoding") from exc

        alg = header.get("alg")
        if alg not in {"HS256", "ES256"}:
            raise JWSVerificationError("unsupported JWS algorithm")

        signing_input = f"{header_segment}.{payload_segment}".encode("ascii")
        if alg == "HS256":
            if not hmac_secret:
                raise JWSVerificationError("hmac_secret is required for HS256")
            expected = hmac.new(
                hmac_secret.encode("utf-8"),
                signing_input,
                hashlib.sha256,
            ).digest()
            if not hmac.compare_digest(expected, signature):
                raise JWSVerificationError("HS256 signature verification failed")
        else:
            if not public_key_pem:
                raise JWSVerificationError("public_key_pem is required for ES256")
            if self.es256_verifier is None:
                raise JWSVerificationError("ES256 verifier backend is not configured")
            ok = self.es256_verifier.verify(
                signing_input=signing_input,
                signature=signature,
                public_key_pem=public_key_pem,
            )
            if not ok:
                raise JWSVerificationError("ES256 signature verification failed")

        if not isinstance(payload, dict):
            raise JWSVerificationError("JWS payload must be a JSON object")
        return payload
