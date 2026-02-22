"""Sprint 7 QA tests for Nmap accuracy and AAA enforcement."""

from __future__ import annotations

import subprocess

import pytest

from pkg.orchestrator.audit_trail import OrchestratorAuditTrail
from pkg.orchestrator.engine import OrchestratorEngine, TaskSubmissionRequest
from pkg.orchestrator.task_scheduler import TaskScheduler
from pkg.orchestrator.telemetry_ingestion import TelemetryIngestionPipeline
from pkg.security.aaa_framework import AAAService, AuthorizationError
from pkg.wrappers.nmap import NmapScanOptions, NmapWrapper


def test_qa_nmap_scan_accuracy_multi_host_xml() -> None:
    xml_output = """<?xml version="1.0"?>
<nmaprun>
  <host>
    <status state="up"/>
    <address addr="10.10.0.10"/>
    <ports>
      <port protocol="tcp" portid="22">
        <state state="open"/>
        <service name="ssh"/>
      </port>
      <port protocol="udp" portid="161">
        <state state="open"/>
        <service name="snmp"/>
      </port>
    </ports>
    <os>
      <osmatch name="Linux 5.x"/>
    </os>
  </host>
  <host>
    <status state="up"/>
    <address addr="10.10.0.20"/>
    <ports>
      <port protocol="tcp" portid="443">
        <state state="open"/>
        <service name="https"/>
      </port>
    </ports>
    <os>
      <osmatch name="Windows 11"/>
    </os>
  </host>
</nmaprun>
"""

    def fake_runner(*args, **kwargs):  # type: ignore[no-untyped-def]
        _ = args, kwargs
        return subprocess.CompletedProcess(
            args=["nmap"],
            returncode=0,
            stdout=xml_output,
            stderr="",
        )

    wrapper = NmapWrapper(runner=fake_runner)
    result = wrapper.run_scan(
        NmapScanOptions(
            targets=["10.10.0.0/24"],
            tcp_syn=True,
            udp_scan=True,
            os_detection=True,
            output_format="xml",
        )
    )

    assert result.summary["total_hosts"] == 2
    assert result.summary["up_hosts"] == 2
    assert result.summary["total_open_ports"] == 3
    assert set(result.summary["scanned_hosts"]) == {"10.10.0.10", "10.10.0.20"}

    host_by_ip = {host.address: host for host in result.hosts}
    assert host_by_ip["10.10.0.10"].open_ports == [22, 161]
    assert host_by_ip["10.10.0.20"].open_ports == [443]
    assert host_by_ip["10.10.0.10"].os_matches == ["Linux 5.x"]
    assert host_by_ip["10.10.0.20"].os_matches == ["Windows 11"]


def test_qa_nmap_aaa_enforcement_denies_unauthorized_submit() -> None:
    aaa = AAAService(users={"analyst": "pw"}, role_bindings={"analyst": {"viewer"}})
    engine = OrchestratorEngine(
        aaa_service=aaa,
        scheduler=TaskScheduler(),
        telemetry=TelemetryIngestionPipeline(batch_size=10),
        audit_trail=OrchestratorAuditTrail(),
    )
    nmap_task = TaskSubmissionRequest(
        source="api",
        tool="nmap",
        action="scan",
        payload={"target": "10.10.0.0/24"},
        requested_by="analyst",
        required_role="operator",
    )

    with pytest.raises(AuthorizationError):
        engine.submit_task(nmap_task, secret="pw")
