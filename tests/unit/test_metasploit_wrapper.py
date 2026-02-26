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

"""Unit tests for Metasploit wrapper integration behavior."""

from __future__ import annotations

import hashlib
from collections.abc import Iterator
from typing import Any

import pytest

from pkg.orchestrator.telemetry_ingestion import TelemetryIngestionPipeline
from pkg.wrappers.metasploit import (
    ExploitRequest,
    MetasploitConfig,
    MetasploitRPCError,
    MetasploitTransportError,
    MetasploitWrapper,
    _enforce_tls_pin,
)


class FakeTransport:
    def __init__(self, responses: list[Any]) -> None:
        self._responses = list(responses)
        self.calls: list[tuple[str, list[Any], MetasploitConfig]] = []

    def __call__(
        self, method: str, params: list[Any], config: MetasploitConfig
    ) -> dict[str, Any]:
        self.calls.append((method, params, config))
        if not self._responses:
            raise AssertionError("no fake response queued")
        item = self._responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def _iterable_transport(sequence: Iterator[Any]):  # type: ignore[no-untyped-def]
    def _transport(
        method: str, params: list[Any], config: MetasploitConfig
    ) -> dict[str, Any]:
        _ = method, params, config
        item = next(sequence)
        if isinstance(item, Exception):
            raise item
        return item

    return _transport


def test_connect_authenticates_and_caches_token() -> None:
    fake = FakeTransport([{"result": "success", "token": "tok-1"}])
    wrapper = MetasploitWrapper(
        config=MetasploitConfig(username="msf", password="pw"),
        transport=fake,
    )

    token_a = wrapper.connect()
    token_b = wrapper.connect()

    assert token_a == "tok-1"
    assert token_b == "tok-1"
    assert len(fake.calls) == 1
    assert fake.calls[0][0] == "auth.login"


def test_load_module_calls_rpc_with_token() -> None:
    fake = FakeTransport(
        [
            {"result": "success", "token": "tok-1"},
            {"name": "ms17_010_eternalblue", "rank": "great"},
        ]
    )
    wrapper = MetasploitWrapper(transport=fake)

    response = wrapper.load_module("exploit", "windows/smb/ms17_010_eternalblue")

    assert response["rank"] == "great"
    assert fake.calls[1][0] == "module.info"
    assert fake.calls[1][1][0] == "tok-1"


def test_execute_exploit_and_capture_sessions() -> None:
    fake = FakeTransport(
        [
            {"result": "success", "token": "tok-1"},
            {"name": "multi/handler"},
            {"job_id": 7, "uuid": "exec-7"},
            {
                "1": {"type": "shell"},
                "2": {"type": "meterpreter"},
            },
            {"data": "uid=0(root)"},
            {"data": "meterpreter > getuid"},
        ]
    )
    wrapper = MetasploitWrapper(transport=fake)

    result = wrapper.execute_exploit(
        ExploitRequest(
            module_type="exploit",
            module_name="linux/http/sample_exploit",
            target_host="10.0.0.8",
            target_port=8080,
            payload="cmd/unix/reverse",
        )
    )

    assert result.job_id == "7"
    assert result.uuid == "exec-7"
    assert result.status == "success"
    assert len(result.sessions) == 2
    assert result.sessions[0].output == "uid=0(root)"
    assert fake.calls[2][0] == "module.execute"
    execute_opts = fake.calls[2][1][3]
    assert execute_opts["RHOSTS"] == "10.0.0.8"
    assert execute_opts["RPORT"] == 8080
    assert execute_opts["PAYLOAD"] == "cmd/unix/reverse"


def test_send_to_orchestrator_emits_telemetry() -> None:
    fake = FakeTransport(
        [
            {"result": "success", "token": "tok-1"},
            {"name": "sample"},
            {"job_id": 77, "uuid": "u-77"},
            {"5": {"type": "shell"}},
            {"data": "shell output"},
        ]
    )
    wrapper = MetasploitWrapper(transport=fake)
    telemetry = TelemetryIngestionPipeline(batch_size=10)
    result = wrapper.execute_exploit(
        ExploitRequest(
            module_type="exploit",
            module_name="unix/ftp/example",
            target_host="10.0.0.9",
        )
    )

    event = wrapper.send_to_orchestrator(
        result=result,
        telemetry=telemetry,
        tenant_id="tenant-a",
        actor="qa-user",
    )

    assert event.event_type == "metasploit_exploit_completed"
    assert event.actor == "qa-user"
    assert event.attributes["module_name"] == "unix/ftp/example"
    assert event.attributes["session_count"] == 1
    assert telemetry.buffered_count == 1


def test_retry_on_transport_failure_then_success() -> None:
    responses = iter(
        [
            {"result": "success", "token": "tok-1"},
            MetasploitTransportError("temporary network"),
            {"name": "ok-module"},
        ]
    )
    wrapper = MetasploitWrapper(
        config=MetasploitConfig(max_retries=2, backoff_seconds=0),
        transport=_iterable_transport(responses),
    )

    response = wrapper.load_module("exploit", "test/module")

    assert response["name"] == "ok-module"


def test_retry_exhaustion_raises() -> None:
    responses = iter(
        [
            {"result": "success", "token": "tok-1"},
            MetasploitTransportError("down-1"),
            MetasploitTransportError("down-2"),
        ]
    )
    wrapper = MetasploitWrapper(
        config=MetasploitConfig(max_retries=1, backoff_seconds=0),
        transport=_iterable_transport(responses),
    )

    with pytest.raises(MetasploitRPCError):
        wrapper.load_module("exploit", "test/module")


class _FakeSock:
    def __init__(self, cert: bytes) -> None:
        self._cert = cert

    def getpeercert(self, binary_form: bool = False) -> bytes | dict[str, Any]:
        if binary_form:
            return self._cert
        return {}


class _FakeConn:
    def __init__(self, cert: bytes) -> None:
        self.sock = _FakeSock(cert)


class _FakeRaw:
    def __init__(self, cert: bytes) -> None:
        self.connection = _FakeConn(cert)


class _FakeResponse:
    def __init__(self, cert: bytes) -> None:
        self.raw = _FakeRaw(cert)


def test_tls_pinning_accepts_matching_cert() -> None:
    cert = b"metasploit-cert"
    digest = hashlib.sha256(cert).hexdigest()
    _enforce_tls_pin(_FakeResponse(cert), digest)


def test_tls_pinning_rejects_mismatch() -> None:
    cert = b"metasploit-cert"
    with pytest.raises(MetasploitTransportError, match="tls pinning validation failed"):
        _enforce_tls_pin(_FakeResponse(cert), "deadbeef")
