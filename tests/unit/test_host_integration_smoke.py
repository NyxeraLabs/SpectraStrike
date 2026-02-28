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
        ingest = getattr(telemetry, "ingest", None)
        if callable(ingest):
            ingest(
                event_type="nmap_scan_completed",
                actor=actor,
                target="orchestrator",
                status="success",
                tenant_id=tenant_id,
                command=["nmap", "127.0.0.1"],
            )
        return _FakeEvent(event_type="nmap_scan_completed", tenant_id=tenant_id)


class _FakeMetasploitWrapper:
    def __init__(self, config: object) -> None:
        self._config = config

    def connect(self) -> str:
        return "token-1"


class _FakeSliverWrapper:
    def __init__(self, timeout_seconds: float) -> None:
        self._timeout_seconds = timeout_seconds

    def execute(self, _request: object) -> object:
        class _R:
            status = "success"
            task_id = "slv-1"
            session_id = "s-1"
            output = "ok"
            target = "127.0.0.1"
            command = "whoami"

        return _R()

    def send_to_orchestrator(
        self,
        _result: object,
        *,
        telemetry: object,
        tenant_id: str,
        actor: str,
    ) -> _FakeEvent:
        ingest = getattr(telemetry, "ingest", None)
        if callable(ingest):
            ingest(
                event_type="sliver_command_completed",
                actor=actor,
                target="orchestrator",
                status="success",
                tenant_id=tenant_id,
                task_id="slv-1",
            )
        return _FakeEvent(event_type="sliver_command_completed", tenant_id=tenant_id)


class _FakeImpacketPsexecWrapper:
    def __init__(self, timeout_seconds: float) -> None:
        self._timeout_seconds = timeout_seconds

    def execute(
        self,
        _request: object,
        *,
        tenant_id: str,
        operator_id: str,
    ) -> object:
        assert tenant_id == "tenant-a"
        assert operator_id == "host-integration-smoke"

        class _R:
            status = "success"
            return_code = 0
            target = "127.0.0.1"
            username = "smoke"
            command = "whoami"
            tool_version = "0.13.0"
            output = "ok"
            execution_fingerprint = "a" * 64
            attestation_measurement_hash = "b" * 64
            payload_signature = "sig"
            payload_signature_algorithm = "Ed25519"

        return _R()

    def send_to_orchestrator(
        self,
        _result: object,
        *,
        telemetry: object,
        tenant_id: str,
        operator_id: str,
        actor: str,
    ) -> _FakeEvent:
        assert operator_id == "host-integration-smoke"
        ingest = getattr(telemetry, "ingest", None)
        if callable(ingest):
            ingest(
                event_type="impacket_psexec_completed",
                actor=actor,
                target="orchestrator",
                status="success",
                tenant_id=tenant_id,
                module="psexec.py",
            )
        return _FakeEvent(event_type="impacket_psexec_completed", tenant_id=tenant_id)


class _FakeImpacketWmiexecWrapper:
    def __init__(self, timeout_seconds: float) -> None:
        self._timeout_seconds = timeout_seconds

    def execute(
        self,
        _request: object,
        *,
        tenant_id: str,
        operator_id: str,
    ) -> object:
        assert tenant_id == "tenant-a"
        assert operator_id == "host-integration-smoke"

        class _R:
            status = "success"
            return_code = 0
            target = "127.0.0.1"
            username = "smoke"
            command = "whoami"
            tool_version = "0.13.0"
            output = "ok"
            execution_fingerprint = "c" * 64
            attestation_measurement_hash = "d" * 64
            payload_signature = "sig"
            payload_signature_algorithm = "Ed25519"

        return _R()

    def send_to_orchestrator(
        self,
        _result: object,
        *,
        telemetry: object,
        tenant_id: str,
        operator_id: str,
        actor: str,
    ) -> _FakeEvent:
        assert operator_id == "host-integration-smoke"
        ingest = getattr(telemetry, "ingest", None)
        if callable(ingest):
            ingest(
                event_type="impacket_wmiexec_completed",
                actor=actor,
                target="orchestrator",
                status="success",
                tenant_id=tenant_id,
                module="wmiexec.py",
            )
        return _FakeEvent(event_type="impacket_wmiexec_completed", tenant_id=tenant_id)


class _FakeImpacketSmbexecWrapper:
    def __init__(self, timeout_seconds: float) -> None:
        self._timeout_seconds = timeout_seconds

    def execute(
        self,
        _request: object,
        *,
        tenant_id: str,
        operator_id: str,
    ) -> object:
        assert tenant_id == "tenant-a"
        assert operator_id == "host-integration-smoke"

        class _R:
            status = "success"
            return_code = 0
            target = "127.0.0.1"
            username = "smoke"
            command = "whoami"
            tool_version = "0.13.0"
            output = "ok"
            execution_fingerprint = "e" * 64
            attestation_measurement_hash = "f" * 64
            payload_signature = "sig"
            payload_signature_algorithm = "Ed25519"

        return _R()

    def send_to_orchestrator(
        self,
        _result: object,
        *,
        telemetry: object,
        tenant_id: str,
        operator_id: str,
        actor: str,
    ) -> _FakeEvent:
        assert operator_id == "host-integration-smoke"
        ingest = getattr(telemetry, "ingest", None)
        if callable(ingest):
            ingest(
                event_type="impacket_smbexec_completed",
                actor=actor,
                target="orchestrator",
                status="success",
                tenant_id=tenant_id,
                module="smbexec.py",
            )
        return _FakeEvent(event_type="impacket_smbexec_completed", tenant_id=tenant_id)


class _FakeImpacketSecretsdumpWrapper:
    def __init__(self, timeout_seconds: float) -> None:
        self._timeout_seconds = timeout_seconds

    def execute(
        self,
        _request: object,
        *,
        tenant_id: str,
        operator_id: str,
    ) -> object:
        assert tenant_id == "tenant-a"
        assert operator_id == "host-integration-smoke"

        class _R:
            status = "success"
            return_code = 0
            target = "127.0.0.1"
            username = "smoke"
            command = "-just-dc-user administrator"
            tool_version = "0.13.0"
            output = "administrator:500:aad3..."
            execution_fingerprint = "1" * 64
            attestation_measurement_hash = "2" * 64
            payload_signature = "sig"
            payload_signature_algorithm = "Ed25519"

        return _R()

    def send_to_orchestrator(
        self,
        _result: object,
        *,
        telemetry: object,
        tenant_id: str,
        operator_id: str,
        actor: str,
    ) -> _FakeEvent:
        assert operator_id == "host-integration-smoke"
        ingest = getattr(telemetry, "ingest", None)
        if callable(ingest):
            ingest(
                event_type="impacket_secretsdump_completed",
                actor=actor,
                target="orchestrator",
                status="success",
                tenant_id=tenant_id,
                module="secretsdump.py",
            )
        return _FakeEvent(
            event_type="impacket_secretsdump_completed", tenant_id=tenant_id
        )


class _FakeImpacketNtlmrelayxWrapper:
    def __init__(self, timeout_seconds: float) -> None:
        self._timeout_seconds = timeout_seconds

    def execute(
        self,
        _request: object,
        *,
        tenant_id: str,
        operator_id: str,
    ) -> object:
        assert tenant_id == "tenant-a"
        assert operator_id == "host-integration-smoke"

        class _R:
            status = "success"
            return_code = 0
            target = "127.0.0.1"
            username = "smoke"
            command = "-t smb://127.0.0.1 -smb2support"
            tool_version = "0.13.0"
            output = "SMBD-Thread started"
            execution_fingerprint = "3" * 64
            attestation_measurement_hash = "4" * 64
            payload_signature = "sig"
            payload_signature_algorithm = "Ed25519"

        return _R()

    def send_to_orchestrator(
        self,
        _result: object,
        *,
        telemetry: object,
        tenant_id: str,
        operator_id: str,
        actor: str,
    ) -> _FakeEvent:
        assert operator_id == "host-integration-smoke"
        ingest = getattr(telemetry, "ingest", None)
        if callable(ingest):
            ingest(
                event_type="impacket_ntlmrelayx_completed",
                actor=actor,
                target="orchestrator",
                status="success",
                tenant_id=tenant_id,
                module="ntlmrelayx.py",
            )
        return _FakeEvent(
            event_type="impacket_ntlmrelayx_completed", tenant_id=tenant_id
        )


class _FakeMythicWrapper:
    def __init__(self, timeout_seconds: float) -> None:
        self._timeout_seconds = timeout_seconds

    def execute(self, _request: object) -> object:
        class _R:
            status = "success"
            task_id = "my-1"
            callback_id = "cb-1"
            output = "ok"
            target = "127.0.0.1"
            command = "pwd"
            operation = "spectra-smoke"

        return _R()

    def send_to_orchestrator(
        self,
        _result: object,
        *,
        telemetry: object,
        tenant_id: str,
        actor: str,
    ) -> _FakeEvent:
        ingest = getattr(telemetry, "ingest", None)
        if callable(ingest):
            ingest(
                event_type="mythic_task_completed",
                actor=actor,
                target="orchestrator",
                status="success",
                tenant_id=tenant_id,
                task_id="my-1",
            )
        return _FakeEvent(event_type="mythic_task_completed", tenant_id=tenant_id)


@dataclass(slots=True)
class _FakeBridgeResult:
    consumed: int
    forwarded_events: int
    forwarded_findings: int
    failed: int
    event_statuses: list[str]
    finding_statuses: list[str]
    status_poll_statuses: list[str]


class _FakeVectorVueClient:
    def __init__(self, _cfg: object) -> None:
        self._cfg = _cfg

    def login(self) -> str:
        return "token-1"


class _FakeBridgeOK:
    def __init__(
        self,
        *,
        broker: object,
        client: object,
        emit_findings_for_all: bool,
    ) -> None:
        assert broker is not None
        assert client is not None
        assert emit_findings_for_all is True

    def drain(self, limit: int) -> _FakeBridgeResult:
        assert limit == 10
        return _FakeBridgeResult(
            consumed=1,
            forwarded_events=1,
            forwarded_findings=1,
            failed=0,
            event_statuses=["accepted"],
            finding_statuses=["accepted"],
            status_poll_statuses=["accepted"],
        )


class _FakeBridgeFailure:
    def __init__(
        self,
        *,
        broker: object,
        client: object,
        emit_findings_for_all: bool,
    ) -> None:
        assert broker is not None
        assert client is not None
        assert emit_findings_for_all is True

    def drain(self, limit: int) -> _FakeBridgeResult:
        assert limit == 10
        return _FakeBridgeResult(
            consumed=1,
            forwarded_events=1,
            forwarded_findings=1,
            failed=0,
            event_statuses=["accepted"],
            finding_statuses=["rejected"],
            status_poll_statuses=["accepted"],
        )


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
        "pkg.integration.host_integration_smoke.SliverWrapper",
        _FakeSliverWrapper,
    )
    monkeypatch.setattr(
        "pkg.integration.host_integration_smoke.ImpacketPsexecWrapper",
        _FakeImpacketPsexecWrapper,
    )
    monkeypatch.setattr(
        "pkg.integration.host_integration_smoke.ImpacketWmiexecWrapper",
        _FakeImpacketWmiexecWrapper,
    )
    monkeypatch.setattr(
        "pkg.integration.host_integration_smoke.ImpacketSmbexecWrapper",
        _FakeImpacketSmbexecWrapper,
    )
    monkeypatch.setattr(
        "pkg.integration.host_integration_smoke.ImpacketSecretsdumpWrapper",
        _FakeImpacketSecretsdumpWrapper,
    )
    monkeypatch.setattr(
        "pkg.integration.host_integration_smoke.ImpacketNtlmrelayxWrapper",
        _FakeImpacketNtlmrelayxWrapper,
    )
    monkeypatch.setattr(
        "pkg.integration.host_integration_smoke.MythicWrapper",
        _FakeMythicWrapper,
    )
    monkeypatch.setattr(
        "pkg.integration.host_integration_smoke.VectorVueClient",
        _FakeVectorVueClient,
    )
    monkeypatch.setattr(
        "pkg.integration.host_integration_smoke.InMemoryVectorVueBridge",
        _FakeBridgeOK,
    )

    result = run_host_integration_smoke(
        tenant_id="tenant-a",
        check_metasploit_rpc=True,
        check_impacket_psexec=True,
        check_impacket_wmiexec=True,
        check_impacket_smbexec=True,
        check_impacket_secretsdump=True,
        check_impacket_ntlmrelayx=True,
        check_sliver_command=True,
        check_mythic_task=True,
        check_vectorvue=True,
    )

    assert result.metasploit_rpc_ok is True
    assert result.sliver_binary_ok is True
    assert result.sliver_command_ok is True
    assert result.impacket_psexec_binary_ok is True
    assert result.impacket_psexec_command_ok is True
    assert result.impacket_wmiexec_binary_ok is True
    assert result.impacket_wmiexec_command_ok is True
    assert result.impacket_smbexec_binary_ok is True
    assert result.impacket_smbexec_command_ok is True
    assert result.impacket_secretsdump_binary_ok is True
    assert result.impacket_secretsdump_command_ok is True
    assert result.impacket_ntlmrelayx_binary_ok is True
    assert result.impacket_ntlmrelayx_command_ok is True
    assert result.mythic_binary_ok is True
    assert result.mythic_task_ok is True
    assert result.rabbitmq_publish_ok is True
    assert result.vectorvue_ok is True
    assert result.vectorvue_event_status == "accepted"
    assert result.vectorvue_finding_status == "accepted"
    assert result.vectorvue_status_poll_status == "accepted"
    assert "metasploit.rpc" in result.checks
    assert "impacket.psexec.version" in result.checks
    assert "impacket.psexec.command" in result.checks
    assert "impacket.wmiexec.version" in result.checks
    assert "impacket.wmiexec.command" in result.checks
    assert "impacket.smbexec.version" in result.checks
    assert "impacket.smbexec.command" in result.checks
    assert "impacket.secretsdump.version" in result.checks
    assert "impacket.secretsdump.command" in result.checks
    assert "impacket.ntlmrelayx.version" in result.checks
    assert "impacket.ntlmrelayx.command" in result.checks
    assert "sliver.version" in result.checks
    assert "sliver.command" in result.checks
    assert "mythic.version" in result.checks
    assert "mythic.task" in result.checks
    assert "rabbitmq.publish" in result.checks
    assert "vectorvue.rabbitmq.bridge" in result.checks


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
        "pkg.integration.host_integration_smoke.VectorVueClient",
        _FakeVectorVueClient,
    )
    monkeypatch.setattr(
        "pkg.integration.host_integration_smoke.InMemoryVectorVueBridge",
        _FakeBridgeFailure,
    )

    result = run_host_integration_smoke(
        tenant_id="tenant-a",
        check_vectorvue=True,
    )

    assert result.vectorvue_ok is False
    assert result.rabbitmq_publish_ok is True
    assert result.vectorvue_event_status == "accepted"
    assert result.vectorvue_finding_status == "rejected"
    assert result.vectorvue_status_poll_status == "accepted"


def test_host_smoke_impacket_wmiexec_live_requires_credentials(
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
    with pytest.raises(
        HostIntegrationError,
        match="IMPACKET_WMIEXEC_PASSWORD or IMPACKET_WMIEXEC_HASHES is required",
    ):
        run_host_integration_smoke(
            tenant_id="tenant-a",
            check_impacket_wmiexec=True,
            check_impacket_wmiexec_live=True,
        )


def test_host_smoke_impacket_smbexec_live_requires_credentials(
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
    with pytest.raises(
        HostIntegrationError,
        match="IMPACKET_SMBEXEC_PASSWORD or IMPACKET_SMBEXEC_HASHES is required",
    ):
        run_host_integration_smoke(
            tenant_id="tenant-a",
            check_impacket_smbexec=True,
            check_impacket_smbexec_live=True,
        )


def test_host_smoke_impacket_secretsdump_live_requires_credentials(
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
    with pytest.raises(
        HostIntegrationError,
        match="IMPACKET_SECRETSDUMP_PASSWORD or IMPACKET_SECRETSDUMP_HASHES is required",
    ):
        run_host_integration_smoke(
            tenant_id="tenant-a",
            check_impacket_secretsdump=True,
            check_impacket_secretsdump_live=True,
        )


def test_host_smoke_impacket_ntlmrelayx_live_requires_credentials(
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
    with pytest.raises(
        HostIntegrationError,
        match="IMPACKET_NTLMRELAYX_PASSWORD or IMPACKET_NTLMRELAYX_HASHES is required",
    ):
        run_host_integration_smoke(
            tenant_id="tenant-a",
            check_impacket_ntlmrelayx=True,
            check_impacket_ntlmrelayx_live=True,
        )
