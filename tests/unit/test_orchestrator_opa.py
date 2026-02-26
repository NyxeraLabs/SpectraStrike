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

from dataclasses import dataclass, field
from typing import Any

import pytest
from requests import RequestException

from pkg.orchestrator.opa import (
    OPAClientError,
    OPAConfig,
    OPAAuthorizationError,
    OPAExecutionAuthorizer,
)


@dataclass
class FakeResponse:
    status_code: int
    payload: dict[str, Any] = field(default_factory=dict)

    def json(self) -> dict[str, Any]:
        return self.payload


class FakeSession:
    def __init__(self, queued: list[Any]) -> None:
        self._queued = queued
        self.calls: list[dict[str, Any]] = []

    def post(self, url: str, json: dict[str, Any], timeout: float) -> FakeResponse:
        self.calls.append({"url": url, "json": json, "timeout": timeout})
        if not self._queued:
            raise AssertionError("no queued fake response")
        item = self._queued.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def _payload() -> dict[str, str]:
    return {
        "operator_id": "operator-a",
        "tenant_id": "tenant-a",
        "tool_sha256": "sha256:" + ("a" * 64),
        "target_urn": "urn:target:ip:10.0.0.5",
        "action": "execute",
    }


def _config() -> OPAConfig:
    return OPAConfig(url="http://opa:8181", timeout_seconds=1.0)


def test_opa_authorizer_allows_on_contract_and_allow_true() -> None:
    session = FakeSession(
        [
            FakeResponse(200, {"result": True}),
            FakeResponse(200, {"result": True}),
        ]
    )
    authorizer = OPAExecutionAuthorizer(_config(), session=session)

    authorizer.authorize(_payload())

    assert len(session.calls) == 2
    assert session.calls[0]["url"].endswith(
        "/v1/data/spectrastrike/capabilities/input_contract_valid"
    )
    assert session.calls[1]["url"].endswith(
        "/v1/data/spectrastrike/capabilities/allow"
    )


def test_opa_authorizer_denies_on_invalid_contract() -> None:
    session = FakeSession([FakeResponse(200, {"result": False})])
    authorizer = OPAExecutionAuthorizer(_config(), session=session)

    with pytest.raises(OPAAuthorizationError, match="invalid input contract"):
        authorizer.authorize(_payload())


def test_opa_authorizer_denies_on_allow_false() -> None:
    session = FakeSession(
        [
            FakeResponse(200, {"result": True}),
            FakeResponse(200, {"result": False}),
        ]
    )
    authorizer = OPAExecutionAuthorizer(_config(), session=session)

    with pytest.raises(OPAAuthorizationError, match="not authorized"):
        authorizer.authorize(_payload())


def test_opa_authorizer_raises_client_error_on_transport_failure() -> None:
    session = FakeSession([RequestException("timeout")])
    authorizer = OPAExecutionAuthorizer(_config(), session=session)

    with pytest.raises(OPAClientError, match="request failed"):
        authorizer.authorize(_payload())
