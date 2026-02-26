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

"""Unit tests for Sprint 16.7 host integration smoke workflow."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from pkg.integration.host_integration_smoke import (
    HostIntegrationError,
    run_host_integration_smoke,
)


@dataclass(slots=True)
class _FakeScanResult:
    hosts: list[object]


@dataclass(slots=True)
class _FakeEvent:
    event_type: str
    tenant_id: str


class _FakeNmapWrapper:
    def run_scan(self, _options: object) -> _FakeScanResult:
        return _FakeScanResult(hosts=[])

    def send_to_orchestrator(
        self,
        _result: _FakeScanResult,
        *,
        telemetry: object,
        tenant_id: str,
        actor: str,
    ) -> _FakeEvent:
        assert telemetry is not None
        assert actor == "host-integration-smoke"
        return _FakeEvent(event_type="nmap_scan_completed", tenant_id=tenant_id)


class _FakeMetasploitWrapper:
    def __init__(self, config: object) -> None:
        self._config = config

    def connect(self) -> str:
        return "token-1"


@dataclass(slots=True)
class _FakeSmokeResult:
    login_ok: bool
    event_status: str
    finding_status: str
    status_poll_status: str


def test_host_smoke_requires_tenant_id() -> None:
    with pytest.raises(HostIntegrationError, match="tenant_id is required"):
        run_host_integration_smoke(tenant_id="")


def test_host_smoke_core_path(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "pkg.integration.host_integration_smoke._require_binary", lambda _name: None
    )
    monkeypatch.setattr(
        "pkg.integration.host_integration_smoke._run_command",
        lambda _cmd, _timeout: "ok",
    )
    monkeypatch.setattr(
        "pkg.integration.host_integration_smoke.NmapWrapper",
        _FakeNmapWrapper,
    )

    result = run_host_integration_smoke(tenant_id="tenant-a")

    assert result.nmap_binary_ok is True
    assert result.nmap_scan_ok is True
    assert result.telemetry_ingest_ok is True
    assert result.metasploit_binary_ok is True
    assert result.metasploit_rpc_ok is None
    assert result.vectorvue_ok is None
    assert result.checks == [
        "nmap.version",
        "nmap.scan",
        "telemetry.ingest",
        "metasploit.version",
    ]


def test_host_smoke_optional_msf_rpc_and_vectorvue(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "pkg.integration.host_integration_smoke._require_binary", lambda _name: None
    )
    monkeypatch.setattr(
        "pkg.integration.host_integration_smoke._run_command",
        lambda _cmd, _timeout: "ok",
    )
    monkeypatch.setattr(
        "pkg.integration.host_integration_smoke.NmapWrapper",
        _FakeNmapWrapper,
    )
    monkeypatch.setattr(
        "pkg.integration.host_integration_smoke.MetasploitWrapper",
        _FakeMetasploitWrapper,
    )
    monkeypatch.setattr(
        "pkg.integration.host_integration_smoke.run_smoke",
        lambda _cfg: _FakeSmokeResult(
            login_ok=True,
            event_status="accepted",
            finding_status="accepted",
            status_poll_status="accepted",
        ),
    )

    result = run_host_integration_smoke(
        tenant_id="tenant-a",
        check_metasploit_rpc=True,
        check_vectorvue=True,
    )

    assert result.metasploit_rpc_ok is True
    assert result.vectorvue_ok is True
    assert result.vectorvue_event_status == "accepted"
    assert result.vectorvue_finding_status == "accepted"
    assert result.vectorvue_status_poll_status == "accepted"
    assert "metasploit.rpc" in result.checks
    assert "vectorvue.smoke" in result.checks


def test_host_smoke_vectorvue_failure_marks_not_ok(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "pkg.integration.host_integration_smoke._require_binary", lambda _name: None
    )
    monkeypatch.setattr(
        "pkg.integration.host_integration_smoke._run_command",
        lambda _cmd, _timeout: "ok",
    )
    monkeypatch.setattr(
        "pkg.integration.host_integration_smoke.NmapWrapper",
        _FakeNmapWrapper,
    )
    monkeypatch.setattr(
        "pkg.integration.host_integration_smoke.run_smoke",
        lambda _cfg: _FakeSmokeResult(
            login_ok=True,
            event_status="accepted",
            finding_status="rejected",
            status_poll_status="accepted",
        ),
    )

    result = run_host_integration_smoke(
        tenant_id="tenant-a",
        check_vectorvue=True,
    )

    assert result.vectorvue_ok is False
    assert result.vectorvue_event_status == "accepted"
    assert result.vectorvue_finding_status == "rejected"
    assert result.vectorvue_status_poll_status == "accepted"
