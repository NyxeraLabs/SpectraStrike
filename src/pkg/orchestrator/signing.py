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

"""Vault transit signing integration for orchestrator cryptographic workflows."""

from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.parse import urlparse

import requests


def _as_bool(raw: str | None, default: bool) -> bool:
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


class VaultTransitError(RuntimeError):
    """Raised when Vault transit operations fail."""


@dataclass(slots=True, frozen=True)
class VaultTransitConfig:
    """Runtime configuration for Vault transit signing."""

    address: str = "https://vault:8200"
    token: str | None = None
    namespace: str | None = None
    mount_path: str = "transit"
    key_name: str = "spectrastrike-orchestrator-signing"
    key_type: str = "ecdsa-p256"
    timeout_seconds: float = 5.0
    verify_tls: bool = True
    ca_cert_file: str | None = None
    require_https: bool = True
    auto_create_key: bool = False

    def __post_init__(self) -> None:
        self._validate()

    @classmethod
    def from_env(cls, prefix: str = "VAULT_") -> VaultTransitConfig:
        """Build Vault transit config from environment variables."""
        return cls(
            address=os.getenv(f"{prefix}ADDR", "https://vault:8200"),
            token=os.getenv(f"{prefix}TOKEN"),
            namespace=os.getenv(f"{prefix}NAMESPACE"),
            mount_path=os.getenv(f"{prefix}TRANSIT_MOUNT", "transit"),
            key_name=os.getenv(
                f"{prefix}TRANSIT_KEY_NAME",
                "spectrastrike-orchestrator-signing",
            ),
            key_type=os.getenv(f"{prefix}TRANSIT_KEY_TYPE", "ecdsa-p256"),
            timeout_seconds=float(os.getenv(f"{prefix}TIMEOUT_SECONDS", "5.0")),
            verify_tls=_as_bool(os.getenv(f"{prefix}VERIFY_TLS"), True),
            ca_cert_file=os.getenv(f"{prefix}CA_CERT_FILE"),
            require_https=_as_bool(os.getenv(f"{prefix}REQUIRE_HTTPS"), True),
            auto_create_key=_as_bool(
                os.getenv(f"{prefix}TRANSIT_AUTO_CREATE_KEY"), False
            ),
        )

    def _validate(self) -> None:
        parsed = urlparse(self.address)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Vault address must be an absolute URL")
        if self.require_https and parsed.scheme.lower() != "https":
            raise ValueError("Vault address must use https when require_https is set")
        if not self.token:
            raise ValueError("Vault token is required")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero")
        if "/" in self.mount_path.strip("/"):
            raise ValueError("mount_path must be a single path segment")
        if "/" in self.key_name.strip("/"):
            raise ValueError("key_name must be a single path segment")


class ManifestSigner(Protocol):
    """Abstract signer contract for future JWS manifest issuance."""

    def sign_payload(self, payload: bytes) -> str:
        """Sign payload bytes and return signer-native signature value."""

    def read_public_key(self, key_version: int | None = None) -> str:
        """Return PEM-encoded public key for signature verification."""


class VaultTransitSigner:
    """HashiCorp Vault transit-backed signing service."""

    def __init__(
        self,
        config: VaultTransitConfig,
        session: requests.Session | None = None,
    ) -> None:
        self._config = config
        self._session = session or requests.Session()

        verify: bool | str = config.verify_tls
        if config.verify_tls and config.ca_cert_file:
            verify = config.ca_cert_file
        self._verify = verify

        self._headers = {
            "X-Vault-Token": config.token or "",
            "Content-Type": "application/json",
        }
        if config.namespace:
            self._headers["X-Vault-Namespace"] = config.namespace

        if config.auto_create_key:
            self.ensure_signing_key()

    def ensure_signing_key(self) -> None:
        """Create or update the transit key used for orchestrator signatures."""
        endpoint = self._vault_endpoint(
            f"/v1/{self._config.mount_path}/keys/{self._config.key_name}"
        )
        self._request(
            "POST",
            endpoint,
            {
                "type": self._config.key_type,
                "derived": False,
                "exportable": False,
                "allow_plaintext_backup": False,
            },
        )

    def sign_payload(
        self,
        payload: bytes,
        *,
        hash_algorithm: str = "sha2-256",
        prehashed: bool = False,
        key_version: int | None = None,
    ) -> str:
        """Sign payload bytes with the configured transit key."""
        if not payload:
            raise ValueError("payload must not be empty")

        endpoint = self._vault_endpoint(
            f"/v1/{self._config.mount_path}/sign/{self._config.key_name}"
        )
        body: dict[str, Any] = {
            "input": base64.b64encode(payload).decode("ascii"),
            "prehashed": prehashed,
            "hash_algorithm": hash_algorithm,
        }
        if key_version is not None:
            body["key_version"] = key_version

        data = self._request("POST", endpoint, body)
        signature = data.get("signature")
        if not isinstance(signature, str) or not signature:
            raise VaultTransitError("Vault transit response missing signature")
        return signature

    def read_public_key(self, key_version: int | None = None) -> str:
        """Load PEM public key metadata from Vault transit key details."""
        endpoint = self._vault_endpoint(
            f"/v1/{self._config.mount_path}/keys/{self._config.key_name}"
        )
        data = self._request("GET", endpoint)

        keys = data.get("keys")
        if not isinstance(keys, dict) or not keys:
            raise VaultTransitError("Vault transit response missing key versions")

        if key_version is None:
            latest = data.get("latest_version")
            if not isinstance(latest, int):
                raise VaultTransitError(
                    "Vault transit response missing latest key version"
                )
            key_version = latest

        key_meta = keys.get(str(key_version))
        if not isinstance(key_meta, dict):
            raise VaultTransitError("Requested key version not found in Vault transit")

        public_key = key_meta.get("public_key")
        if not isinstance(public_key, str) or not public_key:
            raise VaultTransitError(
                "Vault transit response missing public key for requested version"
            )
        return public_key

    def _request(
        self,
        method: str,
        url: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        try:
            response = self._session.request(
                method=method,
                url=url,
                headers=self._headers,
                json=payload,
                timeout=self._config.timeout_seconds,
                verify=self._verify,
            )
        except requests.RequestException as exc:
            raise VaultTransitError("Vault transit request failed") from exc

        if response.status_code >= 400:
            message = f"Vault transit request failed with status {response.status_code}"
            try:
                body = response.json()
                errors = body.get("errors")
                if isinstance(errors, list) and errors:
                    message = f"{message}: {errors[0]}"
            except ValueError:
                pass
            raise VaultTransitError(message)

        try:
            body = response.json()
        except ValueError as exc:
            raise VaultTransitError("Vault transit response is not valid JSON") from exc

        data = body.get("data")
        if not isinstance(data, dict):
            raise VaultTransitError("Vault transit response missing data payload")
        return data

    def _vault_endpoint(self, path: str) -> str:
        return f"{self._config.address.rstrip('/')}{path}"
