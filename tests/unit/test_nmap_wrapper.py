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

"""Unit tests for Nmap wrapper command building, parsing, and telemetry handoff."""

from __future__ import annotations

import subprocess

import pytest

from pkg.orchestrator.telemetry_ingestion import TelemetryIngestionPipeline
from pkg.wrappers.nmap import NmapExecutionError, NmapScanOptions, NmapWrapper


def test_build_command_includes_tcp_udp_os_flags() -> None:
    wrapper = NmapWrapper()
    options = NmapScanOptions(
        targets=["10.0.0.1"],
        tcp_syn=True,
        udp_scan=True,
        os_detection=True,
        ports="22,53,80",
        timing_template=4,
        additional_args=["--reason"],
        output_format="xml",
    )

    command = wrapper.build_command(options)

    assert command[:1] == ["nmap"]
    assert "-sS" in command or "-sT" in command
    assert "-sU" in command
    assert "-O" in command
    assert ["-p", "22,53,80"] == command[command.index("-p") : command.index("-p") + 2]
    assert "-T4" in command
    assert ["-oX", "-"] == command[command.index("-oX") : command.index("-oX") + 2]
    assert "--reason" in command
    assert command[-1] == "10.0.0.1"


def test_build_command_uses_connect_scan_for_unprivileged_user() -> None:
    wrapper = NmapWrapper()
    options = NmapScanOptions(
        targets=["127.0.0.1"],
        tcp_syn=True,
        allow_unprivileged_fallback=True,
    )

    command = wrapper.build_command(options)

    assert "-sT" in command or "-sS" in command


def test_run_scan_parses_xml_output() -> None:
    xml_output = """<?xml version="1.0"?>
<nmaprun>
  <host>
    <status state="up"/>
    <address addr="10.0.0.1"/>
    <ports>
      <port protocol="tcp" portid="22">
        <state state="open"/>
        <service name="ssh"/>
      </port>
      <port protocol="udp" portid="53">
        <state state="closed"/>
        <service name="domain"/>
      </port>
    </ports>
    <os>
      <osmatch name="Linux 5.x"/>
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
    options = NmapScanOptions(targets=["10.0.0.1"], output_format="xml")

    result = wrapper.run_scan(options)

    assert result.summary["total_hosts"] == 1
    assert result.summary["up_hosts"] == 1
    assert result.summary["total_open_ports"] == 1
    assert result.hosts[0].address == "10.0.0.1"
    assert result.hosts[0].open_ports == [22]
    assert result.hosts[0].services[0]["name"] == "ssh"
    assert result.hosts[0].os_matches == ["Linux 5.x"]


def test_run_scan_parses_json_output() -> None:
    json_output = """
{
  "host": [
    {
      "address": "10.0.0.4",
      "status": "up",
      "services": [
        {"port": 80, "protocol": "tcp", "state": "open", "name": "http"},
        {"port": 443, "protocol": "tcp", "state": "closed", "name": "https"}
      ],
      "os_matches": ["Linux"]
    }
  ]
}
"""

    def fake_runner(*args, **kwargs):  # type: ignore[no-untyped-def]
        _ = args, kwargs
        return subprocess.CompletedProcess(
            args=["nmap"],
            returncode=0,
            stdout=json_output,
            stderr="",
        )

    wrapper = NmapWrapper(runner=fake_runner)
    options = NmapScanOptions(
        targets=["10.0.0.4"],
        output_format="json",
        tcp_syn=True,
        udp_scan=False,
    )

    result = wrapper.run_scan(options)

    assert result.summary["total_hosts"] == 1
    assert result.summary["total_open_ports"] == 1
    assert result.hosts[0].open_ports == [80]
    assert result.hosts[0].services[0]["protocol"] == "tcp"
    assert result.hosts[0].os_matches == ["Linux"]


def test_run_scan_raises_on_command_failure() -> None:
    def fake_runner(*args, **kwargs):  # type: ignore[no-untyped-def]
        _ = args, kwargs
        return subprocess.CompletedProcess(
            args=["nmap"],
            returncode=1,
            stdout="",
            stderr="nmap: command not found",
        )

    wrapper = NmapWrapper(runner=fake_runner)
    options = NmapScanOptions(targets=["127.0.0.1"])

    with pytest.raises(NmapExecutionError):
        wrapper.run_scan(options)


def test_send_to_orchestrator_emits_telemetry_event() -> None:
    xml_output = """<?xml version="1.0"?>
<nmaprun>
  <host>
    <status state="up"/>
    <address addr="10.0.0.7"/>
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
    options = NmapScanOptions(targets=["10.0.0.7"])
    result = wrapper.run_scan(options)
    telemetry = TelemetryIngestionPipeline(batch_size=10)

    event = wrapper.send_to_orchestrator(result=result, telemetry=telemetry, actor="qa-user")

    assert event.event_type == "nmap_scan_completed"
    assert event.actor == "qa-user"
    assert event.attributes["scan_summary"]["total_hosts"] == 1
    assert telemetry.buffered_count == 1
