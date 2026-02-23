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

"""Nmap wrapper module for orchestrated scan execution and parsing."""

from __future__ import annotations

import json
import os
import re
from asyncio import run
from asyncio.subprocess import PIPE, Process, create_subprocess_exec
from dataclasses import dataclass, field
from typing import Any, Literal

from pkg.logging.framework import get_logger
from pkg.orchestrator.telemetry_ingestion import (
    TelemetryEvent,
    TelemetryIngestionPipeline,
)

logger = get_logger("spectrastrike.wrappers.nmap")


class NmapExecutionError(RuntimeError):
    """Raised when Nmap execution fails or output cannot be parsed."""


@dataclass(slots=True)
class NmapScanOptions:
    """Runtime options for an Nmap wrapper scan."""

    targets: list[str]
    tcp_syn: bool = True
    udp_scan: bool = False
    os_detection: bool = False
    ports: str | None = None
    timing_template: int | None = None
    additional_args: list[str] = field(default_factory=list)
    output_format: Literal["xml", "json"] = "xml"
    allow_unprivileged_fallback: bool = True

    def __post_init__(self) -> None:
        if not self.targets:
            raise ValueError("at least one target is required")
        if not (self.tcp_syn or self.udp_scan or self.os_detection):
            raise ValueError(
                "enable at least one scan mode: tcp_syn, udp_scan, os_detection"
            )
        if self.timing_template is not None and not 0 <= self.timing_template <= 5:
            raise ValueError("timing_template must be between 0 and 5")


@dataclass(slots=True)
class NmapScanHost:
    """Normalized host-level scan output."""

    address: str
    status: str
    open_ports: list[int] = field(default_factory=list)
    services: list[dict[str, Any]] = field(default_factory=list)
    os_matches: list[str] = field(default_factory=list)


@dataclass(slots=True)
class NmapScanResult:
    """Normalized scan result for orchestrator handoff."""

    command: list[str]
    output_format: Literal["xml", "json"]
    raw_output: str
    hosts: list[NmapScanHost]
    summary: dict[str, Any]


@dataclass(slots=True)
class CommandResult:
    """Minimal command result contract for wrapper runner injection."""

    returncode: int
    stdout: str
    stderr: str


class NmapWrapper:
    """Wrapper for running Nmap with deterministic parsing behavior."""

    def __init__(
        self,
        runner: Any | None = None,
    ) -> None:
        self._runner = runner or self._run_command

    @staticmethod
    def _run_command(command: list[str]) -> CommandResult:
        """Execute nmap command without shell expansion."""

        async def _execute() -> CommandResult:
            process: Process = await create_subprocess_exec(
                *command,
                stdout=PIPE,
                stderr=PIPE,
            )
            stdout_b, stderr_b = await process.communicate()
            return CommandResult(
                returncode=process.returncode or 0,
                stdout=stdout_b.decode("utf-8", errors="replace"),
                stderr=stderr_b.decode("utf-8", errors="replace"),
            )

        return run(_execute())

    def build_command(self, options: NmapScanOptions) -> list[str]:
        """Build the concrete Nmap command from scan options."""
        command = ["nmap"]

        if options.tcp_syn:
            if options.allow_unprivileged_fallback and os.geteuid() != 0:
                command.append("-sT")
            else:
                command.append("-sS")
        if options.udp_scan:
            command.append("-sU")
        if options.os_detection:
            command.append("-O")
        if options.ports:
            command.extend(["-p", options.ports])
        if options.timing_template is not None:
            command.append(f"-T{options.timing_template}")
        if options.output_format == "xml":
            command.extend(["-oX", "-"])
        else:
            command.extend(["-oJ", "-"])

        command.extend(options.additional_args)
        command.extend(options.targets)
        return command

    def run_scan(self, options: NmapScanOptions) -> NmapScanResult:
        """Execute Nmap scan and return normalized parsed output."""
        command = self.build_command(options)
        logger.info("Executing nmap scan command: %s", " ".join(command))

        completed = self._runner(command)

        if completed.returncode != 0:
            stderr = (completed.stderr or "").strip()
            stdout = (completed.stdout or "").strip()
            message = stderr or stdout or "nmap command failed"
            raise NmapExecutionError(message)

        raw_output = completed.stdout or ""
        if options.output_format == "xml":
            hosts = self._parse_xml(raw_output)
        else:
            hosts = self._parse_json(raw_output)

        summary = self._build_summary(hosts)
        logger.info(
            "Nmap scan completed: hosts=%s open_ports=%s",
            summary["total_hosts"],
            summary["total_open_ports"],
        )

        return NmapScanResult(
            command=command,
            output_format=options.output_format,
            raw_output=raw_output,
            hosts=hosts,
            summary=summary,
        )

    def send_to_orchestrator(
        self,
        result: NmapScanResult,
        telemetry: TelemetryIngestionPipeline,
        actor: str = "nmap-wrapper",
    ) -> TelemetryEvent:
        """Emit normalized scan summary into orchestrator telemetry."""
        return telemetry.ingest(
            event_type="nmap_scan_completed",
            actor=actor,
            target="orchestrator",
            status="success",
            scan_summary=result.summary,
            host_count=len(result.hosts),
            output_format=result.output_format,
            command=result.command,
        )

    def _parse_xml(self, xml_output: str) -> list[NmapScanHost]:
        parsed_hosts: list[NmapScanHost] = []
        host_blocks = re.findall(r"<host\b[^>]*>(.*?)</host>", xml_output, flags=re.S)
        if not host_blocks:
            raise NmapExecutionError(
                "failed to parse nmap XML output: no <host> blocks"
            )

        for host_block in host_blocks:
            address_match = re.search(r'<address\b[^>]*\baddr="([^"]+)"', host_block)
            status_match = re.search(r'<status\b[^>]*\bstate="([^"]+)"', host_block)
            address = address_match.group(1) if address_match else "unknown"
            status = status_match.group(1) if status_match else "unknown"
            services: list[dict[str, Any]] = []
            open_ports: list[int] = []
            port_matches = re.findall(
                r"<port\b([^>]*)>(.*?)</port>",
                host_block,
                flags=re.S,
            )
            for port_attrs, port_block in port_matches:
                state_match = re.search(
                    r'<state\b[^>]*\bstate="([^"]+)"',
                    port_block,
                )
                if not state_match or state_match.group(1) != "open":
                    continue

                port_id_match = re.search(r'\bportid="([^"]+)"', port_attrs)
                protocol_match = re.search(r'\bprotocol="([^"]+)"', port_attrs)
                service_match = re.search(
                    r'<service\b[^>]*\bname="([^"]+)"',
                    port_block,
                )
                port_id = int(port_id_match.group(1)) if port_id_match else 0
                open_ports.append(port_id)
                services.append(
                    {
                        "port": port_id,
                        "protocol": (
                            protocol_match.group(1) if protocol_match else "unknown"
                        ),
                        "name": service_match.group(1) if service_match else "unknown",
                    }
                )

            os_matches: list[str] = []
            for match in re.findall(r'<osmatch\b[^>]*\bname="([^"]+)"', host_block):
                if match:
                    os_matches.append(match)

            parsed_hosts.append(
                NmapScanHost(
                    address=address,
                    status=status,
                    open_ports=open_ports,
                    services=services,
                    os_matches=os_matches,
                )
            )
        return parsed_hosts

    def _parse_json(self, json_output: str) -> list[NmapScanHost]:
        try:
            payload = json.loads(json_output)
        except json.JSONDecodeError as exc:
            raise NmapExecutionError(
                f"failed to parse nmap JSON output: {exc}"
            ) from exc

        host_nodes: list[dict[str, Any]] = []
        if isinstance(payload, dict):
            if isinstance(payload.get("host"), list):
                host_nodes = [h for h in payload["host"] if isinstance(h, dict)]
            elif isinstance(payload.get("nmaprun"), dict):
                nmaprun = payload["nmaprun"]
                maybe_hosts = nmaprun.get("host", [])
                if isinstance(maybe_hosts, list):
                    host_nodes = [h for h in maybe_hosts if isinstance(h, dict)]

        parsed_hosts: list[NmapScanHost] = []
        for host_node in host_nodes:
            address = str(host_node.get("address", "unknown"))
            status = str(host_node.get("status", "unknown"))

            open_ports: list[int] = []
            services: list[dict[str, Any]] = []
            for service in host_node.get("services", []):
                if not isinstance(service, dict):
                    continue
                if service.get("state") != "open":
                    continue
                port = int(service.get("port", 0))
                open_ports.append(port)
                services.append(
                    {
                        "port": port,
                        "protocol": str(service.get("protocol", "unknown")),
                        "name": str(service.get("name", "unknown")),
                    }
                )

            os_matches = [str(name) for name in host_node.get("os_matches", []) if name]
            parsed_hosts.append(
                NmapScanHost(
                    address=address,
                    status=status,
                    open_ports=open_ports,
                    services=services,
                    os_matches=os_matches,
                )
            )

        return parsed_hosts

    def _build_summary(self, hosts: list[NmapScanHost]) -> dict[str, Any]:
        total_open_ports = sum(len(host.open_ports) for host in hosts)
        return {
            "total_hosts": len(hosts),
            "up_hosts": sum(1 for host in hosts if host.status == "up"),
            "total_open_ports": total_open_ports,
            "scanned_hosts": [host.address for host in hosts],
        }
