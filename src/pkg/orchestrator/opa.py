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

"""OPA client used for pre-sign authorization checks in orchestrator."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.parse import urlparse

import requests

from pkg.security.aaa_framework import Principal


class OPAClientError(RuntimeError):
    """Raised when OPA query transport or response handling fails."""


class OPAAuthorizationError(PermissionError):
    """Raised when OPA denies pre-sign execution authorization."""


@dataclass(slots=True, frozen=True)
class OPAConfig:
    """Runtime configuration for orchestrator OPA queries."""

    url: str = "http://opa:8181"
    timeout_seconds: float = 2.0
    allow_path: str = "/v1/data/spectrastrike/capabilities/allow"
    input_contract_path: str = (
        "/v1/data/spectrastrike/capabilities/input_contract_valid"
    )

    @classmethod
    def from_env(cls) -> OPAConfig:
        return cls(
            url=os.getenv("OPA_URL", "http://opa:8181"),
            timeout_seconds=float(os.getenv("OPA_TIMEOUT_SECONDS", "2.0")),
            allow_path=os.getenv(
                "OPA_ALLOW_PATH",
                "/v1/data/spectrastrike/capabilities/allow",
            ),
            input_contract_path=os.getenv(
                "OPA_INPUT_CONTRACT_PATH",
                "/v1/data/spectrastrike/capabilities/input_contract_valid",
            ),
        )

    def __post_init__(self) -> None:
        parsed = urlparse(self.url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("OPA url must be an absolute URL")
        if self.timeout_seconds <= 0:
            raise ValueError("OPA timeout_seconds must be greater than zero")


class OPAQuerySession(Protocol):
    """Protocol for requests-like session object."""

    def post(self, url: str, json: dict[str, Any], timeout: float) -> Any:
        """Issue OPA policy query request."""


class OPAExecutionAuthorizer:
    """Performs policy checks before cryptographic manifest signing."""

    def __init__(
        self,
        config: OPAConfig | None = None,
        session: OPAQuerySession | None = None,
    ) -> None:
        self._config = config or OPAConfig.from_env()
        self._session = session or requests.Session()

    def authorize(self, payload: dict[str, Any]) -> None:
        """Validate input contract and enforce allow decision from OPA."""
        if not self._query_bool(self._config.input_contract_path, payload):
            raise OPAAuthorizationError("OPA denied request: invalid input contract")
        if not self._query_bool(self._config.allow_path, payload):
            raise OPAAuthorizationError("OPA denied request: execution not authorized")

    def _query_bool(self, path: str, payload: dict[str, Any]) -> bool:
        url = self._join_url(path)
        try:
            response = self._session.post(
                url,
                json={"input": payload},
                timeout=self._config.timeout_seconds,
            )
        except requests.RequestException as exc:
            raise OPAClientError("OPA request failed") from exc

        if response.status_code >= 400:
            raise OPAClientError(f"OPA request failed with status {response.status_code}")

        try:
            body = response.json()
        except ValueError as exc:
            raise OPAClientError("OPA response is not valid JSON") from exc

        result = body.get("result")
        if not isinstance(result, bool):
            raise OPAClientError("OPA response missing boolean result")
        return result

    def _join_url(self, path: str) -> str:
        normalized = path if path.startswith("/") else f"/{path}"
        return f"{self._config.url.rstrip('/')}{normalized}"


class OPAAAAPolicyAdapter:
    """AAA adapter that delegates complex execution checks to OPA."""

    def __init__(self, authorizer: OPAExecutionAuthorizer | None = None) -> None:
        self._authorizer = authorizer or OPAExecutionAuthorizer()

    def authorize_execution(
        self,
        *,
        principal: Principal,
        action: str,
        target: str,
        context: dict[str, Any],
    ) -> None:
        del target
        payload = {
            "operator_id": principal.principal_id,
            "tenant_id": str(context.get("tenant_id", "")),
            "tool_sha256": str(context.get("tool_sha256", "")),
            "target_urn": str(context.get("target_urn", "")),
            "action": action,
        }
        self._authorizer.authorize(payload)
