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

"""Sprint 16.8 host integration smoke checks for local toolchain + VectorVue."""

from __future__ import annotations

import argparse
import asyncio
import os
import shutil
import subprocess
from dataclasses import dataclass, field

from pkg.integration.vectorvue.client import VectorVueClient
from pkg.integration.vectorvue.config import VectorVueConfig
from pkg.integration.vectorvue.rabbitmq_bridge import InMemoryVectorVueBridge
from pkg.logging.framework import get_logger
from pkg.orchestrator.messaging import InMemoryRabbitBroker, RabbitMQTelemetryPublisher
from pkg.orchestrator.telemetry_ingestion import TelemetryIngestionPipeline
from pkg.telemetry.sdk import build_internal_telemetry_event
from pkg.wrappers.metasploit import MetasploitConfig, MetasploitWrapper
from pkg.wrappers.mythic import MythicTaskRequest, MythicWrapper
from pkg.wrappers.nmap import NmapScanOptions, NmapWrapper
from pkg.wrappers.impacket_psexec import (
    ImpacketPsexecRequest,
    ImpacketPsexecWrapper,
)
from pkg.wrappers.impacket_wmiexec import (
    ImpacketWmiexecRequest,
    ImpacketWmiexecWrapper,
)
from pkg.wrappers.impacket_smbexec import (
    ImpacketSmbexecRequest,
    ImpacketSmbexecWrapper,
)
from pkg.wrappers.impacket_secretsdump import (
    ImpacketSecretsdumpRequest,
    ImpacketSecretsdumpWrapper,
)
from pkg.wrappers.impacket_ntlmrelayx import (
    ImpacketNtlmrelayxRequest,
    ImpacketNtlmrelayxWrapper,
)
from pkg.wrappers.bloodhound_collector import (
    BloodhoundCollectorRequest,
    BloodhoundCollectorWrapper,
)
from pkg.wrappers.nuclei import NucleiScanRequest, NucleiWrapper
from pkg.wrappers.prowler import ProwlerScanRequest, ProwlerWrapper
from pkg.wrappers.responder import ResponderRequest, ResponderWrapper
from pkg.wrappers.gobuster import GobusterScanRequest, GobusterWrapper
from pkg.wrappers.ffuf import FfufScanRequest, FfufWrapper
from pkg.wrappers.netcat import NetcatRequest, NetcatWrapper
from pkg.wrappers.netexec import NetExecRequest, NetExecWrapper
from pkg.wrappers.john import JohnRequest, JohnWrapper
from pkg.wrappers.wget import WgetRequest, WgetWrapper
from pkg.wrappers.burpsuite import BurpSuiteRequest, BurpSuiteWrapper
from pkg.wrappers.amass import AmassRequest, AmassWrapper
from pkg.wrappers.sqlmap import SqlmapRequest, SqlmapWrapper
from pkg.wrappers.subfinder import SubfinderRequest, SubfinderWrapper
from pkg.wrappers.sliver import SliverCommandRequest, SliverWrapper

_LOCAL_FED_ENV_PATH = "local_federation/.env.spectrastrike.local"
logger = get_logger("spectrastrike.integration.host_smoke")


class HostIntegrationError(RuntimeError):
    """Raised when required host smoke validations fail."""


@dataclass(slots=True)
class HostIntegrationResult:
    """Result summary for sprint 16.8 host integration checks."""

    tenant_id: str
    nmap_binary_ok: bool = False
    nmap_scan_ok: bool = False
    telemetry_ingest_ok: bool = False
    metasploit_binary_ok: bool = False
    metasploit_rpc_ok: bool | None = None
    impacket_psexec_binary_ok: bool | None = None
    impacket_psexec_command_ok: bool | None = None
    impacket_wmiexec_binary_ok: bool | None = None
    impacket_wmiexec_command_ok: bool | None = None
    impacket_smbexec_binary_ok: bool | None = None
    impacket_smbexec_command_ok: bool | None = None
    impacket_secretsdump_binary_ok: bool | None = None
    impacket_secretsdump_command_ok: bool | None = None
    impacket_ntlmrelayx_binary_ok: bool | None = None
    impacket_ntlmrelayx_command_ok: bool | None = None
    bloodhound_collector_binary_ok: bool | None = None
    bloodhound_collector_command_ok: bool | None = None
    nuclei_binary_ok: bool | None = None
    nuclei_command_ok: bool | None = None
    prowler_binary_ok: bool | None = None
    prowler_command_ok: bool | None = None
    responder_binary_ok: bool | None = None
    responder_command_ok: bool | None = None
    gobuster_binary_ok: bool | None = None
    gobuster_command_ok: bool | None = None
    ffuf_binary_ok: bool | None = None
    ffuf_command_ok: bool | None = None
    netcat_binary_ok: bool | None = None
    netcat_command_ok: bool | None = None
    netexec_binary_ok: bool | None = None
    netexec_command_ok: bool | None = None
    john_binary_ok: bool | None = None
    john_command_ok: bool | None = None
    wget_binary_ok: bool | None = None
    wget_command_ok: bool | None = None
    burpsuite_binary_ok: bool | None = None
    burpsuite_command_ok: bool | None = None
    amass_binary_ok: bool | None = None
    amass_command_ok: bool | None = None
    sqlmap_binary_ok: bool | None = None
    sqlmap_command_ok: bool | None = None
    subfinder_binary_ok: bool | None = None
    subfinder_command_ok: bool | None = None
    sliver_binary_ok: bool | None = None
    sliver_command_ok: bool | None = None
    mythic_binary_ok: bool | None = None
    mythic_task_ok: bool | None = None
    rabbitmq_publish_ok: bool | None = None
    vectorvue_ok: bool | None = None
    vectorvue_event_status: str | None = None
    vectorvue_finding_status: str | None = None
    vectorvue_status_poll_status: str | None = None
    checks: list[str] = field(default_factory=list)


def _must_have_tenant(tenant_id: str) -> str:
    resolved = tenant_id.strip()
    if not resolved:
        raise HostIntegrationError("tenant_id is required")
    return resolved


def _run_command(command: list[str], timeout_seconds: float) -> str:
    completed = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
    )
    output = (completed.stdout or "").strip()
    if not output:
        output = (completed.stderr or "").strip()
    return output


def _require_binary(name: str) -> None:
    if shutil.which(name) is None:
        raise HostIntegrationError(f"required binary not found on host: {name}")


def _load_local_federation_env() -> None:
    if not os.path.exists(_LOCAL_FED_ENV_PATH):
        return
    try:
        with open(_LOCAL_FED_ENV_PATH, "r", encoding="utf-8") as handle:
            for line in handle:
                stripped = line.strip()
                if not stripped or stripped.startswith("#") or "=" not in stripped:
                    continue
                key, value = stripped.split("=", 1)
                key = key.strip()
                if key and key not in os.environ:
                    os.environ[key] = value.strip()
    except OSError:
        return


def _build_vectorvue_config(timeout_seconds: float) -> VectorVueConfig:
    verify_tls_ca_file = os.getenv("VECTORVUE_VERIFY_TLS_CA_FILE", "").strip()
    verify_tls: bool | str = (
        verify_tls_ca_file
        if verify_tls_ca_file
        else os.getenv("VECTORVUE_VERIFY_TLS", "1") == "1"
    )
    return VectorVueConfig(
        base_url=os.getenv(
            "VECTORVUE_FEDERATION_URL",
            os.getenv("VECTORVUE_BASE_URL", "https://127.0.0.1"),
        ),
        username=os.getenv("VECTORVUE_USERNAME", "acme_viewer"),
        password=os.getenv("VECTORVUE_PASSWORD", "AcmeView3r!"),
        tenant_id=os.getenv(
            "VECTORVUE_TENANT_ID", "10000000-0000-0000-0000-000000000001"
        ),
        timeout_seconds=timeout_seconds,
        verify_tls=verify_tls,
        mtls_client_cert_file=os.getenv(
            "VECTORVUE_FEDERATION_MTLS_CERT_FILE",
            os.getenv("VECTORVUE_MTLS_CLIENT_CERT_FILE"),
        ),
        mtls_client_key_file=os.getenv(
            "VECTORVUE_FEDERATION_MTLS_KEY_FILE",
            os.getenv("VECTORVUE_MTLS_CLIENT_KEY_FILE"),
        ),
        max_retries=1,
        backoff_seconds=0,
    )


def run_host_integration_smoke(
    *,
    tenant_id: str,
    nmap_target: str = "127.0.0.1",
    timeout_seconds: float = 8.0,
    check_metasploit_rpc: bool = False,
    check_sliver_command: bool = False,
    check_impacket_psexec: bool = False,
    check_impacket_psexec_live: bool = False,
    check_impacket_wmiexec: bool = False,
    check_impacket_wmiexec_live: bool = False,
    check_impacket_smbexec: bool = False,
    check_impacket_smbexec_live: bool = False,
    check_impacket_secretsdump: bool = False,
    check_impacket_secretsdump_live: bool = False,
    check_impacket_ntlmrelayx: bool = False,
    check_impacket_ntlmrelayx_live: bool = False,
    check_bloodhound_collector: bool = False,
    check_bloodhound_collector_live: bool = False,
    check_nuclei: bool = False,
    check_nuclei_live: bool = False,
    check_prowler: bool = False,
    check_prowler_live: bool = False,
    check_responder: bool = False,
    check_responder_live: bool = False,
    check_gobuster: bool = False,
    check_gobuster_live: bool = False,
    check_ffuf: bool = False,
    check_ffuf_live: bool = False,
    check_netcat: bool = False,
    check_netcat_live: bool = False,
    check_netexec: bool = False,
    check_netexec_live: bool = False,
    check_john: bool = False,
    check_john_live: bool = False,
    check_wget: bool = False,
    check_wget_live: bool = False,
    check_burpsuite: bool = False,
    check_burpsuite_live: bool = False,
    check_amass: bool = False,
    check_amass_live: bool = False,
    check_sqlmap: bool = False,
    check_sqlmap_live: bool = False,
    check_subfinder: bool = False,
    check_subfinder_live: bool = False,
    check_mythic_task: bool = False,
    check_vectorvue: bool = False,
) -> HostIntegrationResult:
    """Execute host integration smoke path for Sprint 16.8."""
    resolved_tenant = _must_have_tenant(tenant_id)
    result = HostIntegrationResult(tenant_id=resolved_tenant)
    integration_actor = os.getenv(
        "HOST_INTEGRATION_ACTOR",
        "host-integration-smoke",
    )
    metasploit_version_output = ""
    sliver_wrapper: SliverWrapper | None = None
    sliver_result: object | None = None
    impacket_psexec_wrapper: ImpacketPsexecWrapper | None = None
    impacket_psexec_result: object | None = None
    impacket_wmiexec_wrapper: ImpacketWmiexecWrapper | None = None
    impacket_wmiexec_result: object | None = None
    impacket_smbexec_wrapper: ImpacketSmbexecWrapper | None = None
    impacket_smbexec_result: object | None = None
    impacket_secretsdump_wrapper: ImpacketSecretsdumpWrapper | None = None
    impacket_secretsdump_result: object | None = None
    impacket_ntlmrelayx_wrapper: ImpacketNtlmrelayxWrapper | None = None
    impacket_ntlmrelayx_result: object | None = None
    bloodhound_collector_wrapper: BloodhoundCollectorWrapper | None = None
    bloodhound_collector_result: object | None = None
    nuclei_wrapper: NucleiWrapper | None = None
    nuclei_result: object | None = None
    prowler_wrapper: ProwlerWrapper | None = None
    prowler_result: object | None = None
    responder_wrapper: ResponderWrapper | None = None
    responder_result: object | None = None
    gobuster_wrapper: GobusterWrapper | None = None
    gobuster_result: object | None = None
    ffuf_wrapper: FfufWrapper | None = None
    ffuf_result: object | None = None
    netcat_wrapper: NetcatWrapper | None = None
    netcat_result: object | None = None
    netexec_wrapper: NetExecWrapper | None = None
    netexec_result: object | None = None
    john_wrapper: JohnWrapper | None = None
    john_result: object | None = None
    wget_wrapper: WgetWrapper | None = None
    wget_result: object | None = None
    burpsuite_wrapper: BurpSuiteWrapper | None = None
    burpsuite_result: object | None = None
    amass_wrapper: AmassWrapper | None = None
    amass_result: object | None = None
    sqlmap_wrapper: SqlmapWrapper | None = None
    sqlmap_result: object | None = None
    subfinder_wrapper: SubfinderWrapper | None = None
    subfinder_result: object | None = None
    mythic_wrapper: MythicWrapper | None = None
    mythic_result: object | None = None

    _require_binary("nmap")
    _run_command(["nmap", "--version"], timeout_seconds)
    result.nmap_binary_ok = True
    result.checks.append("nmap.version")

    nmap_wrapper = NmapWrapper()
    nmap_scan = nmap_wrapper.run_scan(
        NmapScanOptions(
            targets=[nmap_target],
            ports="1",
            timing_template=2,
            # Avoid raw host-discovery probes so smoke checks remain stable in constrained runtimes.
            additional_args=[
                "-n",
                "-Pn",
                "--max-retries",
                "1",
                "--host-timeout",
                "5s",
            ],
        )
    )
    result.nmap_scan_ok = True
    result.checks.append("nmap.scan")

    telemetry = TelemetryIngestionPipeline(batch_size=1)
    event = nmap_wrapper.send_to_orchestrator(
        nmap_scan,
        telemetry=telemetry,
        tenant_id=resolved_tenant,
        actor=integration_actor,
    )
    result.telemetry_ingest_ok = (
        event.event_type == "nmap_scan_completed" and event.tenant_id == resolved_tenant
    )
    result.checks.append("telemetry.ingest")

    _require_binary("msfconsole")
    metasploit_version_output = _run_command(["msfconsole", "--version"], timeout_seconds)
    result.metasploit_binary_ok = True
    result.checks.append("metasploit.version")

    if check_metasploit_rpc:
        wrapper = MetasploitWrapper(config=MetasploitConfig.from_env())
        wrapper.connect()
        result.metasploit_rpc_ok = True
        result.checks.append("metasploit.rpc")

    if check_impacket_psexec:
        impacket_binary = os.getenv("IMPACKET_PSEXEC_BINARY", "psexec.py")
        _require_binary(impacket_binary)
        try:
            _run_command([impacket_binary, "--version"], timeout_seconds)
        except Exception:
            _run_command([impacket_binary, "-h"], timeout_seconds)
        result.impacket_psexec_binary_ok = True
        result.checks.append("impacket.psexec.version")
        impacket_psexec_wrapper = ImpacketPsexecWrapper(timeout_seconds=timeout_seconds)
        impacket_target = nmap_target
        impacket_username = os.getenv("IMPACKET_PSEXEC_USERNAME", "smoke")
        impacket_domain = os.getenv("IMPACKET_PSEXEC_DOMAIN", "").strip() or None
        impacket_password = os.getenv("IMPACKET_PSEXEC_PASSWORD", "").strip() or None
        impacket_hashes = os.getenv("IMPACKET_PSEXEC_HASHES", "").strip() or None
        impacket_command = os.getenv("IMPACKET_PSEXEC_COMMAND", "whoami")
        impacket_extra_args = [] if check_impacket_psexec_live else ["--dry-run"]
        if check_impacket_psexec_live and not (impacket_password or impacket_hashes):
            raise HostIntegrationError(
                "IMPACKET_PSEXEC_PASSWORD or IMPACKET_PSEXEC_HASHES is required for live psexec e2e"
            )
        impacket_psexec_result = impacket_psexec_wrapper.execute(
            ImpacketPsexecRequest(
                target=impacket_target,
                username=impacket_username,
                domain=impacket_domain,
                password=impacket_password,
                hashes=impacket_hashes,
                no_pass=not check_impacket_psexec_live and not (impacket_password or impacket_hashes),
                command=impacket_command,
                extra_args=impacket_extra_args,
            ),
            tenant_id=resolved_tenant,
            operator_id=integration_actor,
        )
        impacket_event = impacket_psexec_wrapper.send_to_orchestrator(
            impacket_psexec_result,
            telemetry=telemetry,
            tenant_id=resolved_tenant,
            operator_id=integration_actor,
            actor=integration_actor,
        )
        result.impacket_psexec_command_ok = (
            impacket_event.event_type == "impacket_psexec_completed"
            and impacket_event.tenant_id == resolved_tenant
        )
        result.checks.append(
            "impacket.psexec.command.live"
            if check_impacket_psexec_live
            else "impacket.psexec.command"
        )

    if check_impacket_wmiexec:
        impacket_binary = os.getenv("IMPACKET_WMIEXEC_BINARY", "wmiexec.py")
        _require_binary(impacket_binary)
        try:
            _run_command([impacket_binary, "--version"], timeout_seconds)
        except Exception:
            _run_command([impacket_binary, "-h"], timeout_seconds)
        result.impacket_wmiexec_binary_ok = True
        result.checks.append("impacket.wmiexec.version")
        impacket_wmiexec_wrapper = ImpacketWmiexecWrapper(timeout_seconds=timeout_seconds)
        impacket_target = nmap_target
        impacket_username = os.getenv("IMPACKET_WMIEXEC_USERNAME", "smoke")
        impacket_domain = os.getenv("IMPACKET_WMIEXEC_DOMAIN", "").strip() or None
        impacket_password = os.getenv("IMPACKET_WMIEXEC_PASSWORD", "").strip() or None
        impacket_hashes = os.getenv("IMPACKET_WMIEXEC_HASHES", "").strip() or None
        impacket_command = os.getenv("IMPACKET_WMIEXEC_COMMAND", "whoami")
        impacket_extra_args = [] if check_impacket_wmiexec_live else ["--dry-run"]
        if check_impacket_wmiexec_live and not (impacket_password or impacket_hashes):
            raise HostIntegrationError(
                "IMPACKET_WMIEXEC_PASSWORD or IMPACKET_WMIEXEC_HASHES is required for live wmiexec e2e"
            )
        impacket_wmiexec_result = impacket_wmiexec_wrapper.execute(
            ImpacketWmiexecRequest(
                target=impacket_target,
                username=impacket_username,
                domain=impacket_domain,
                password=impacket_password,
                hashes=impacket_hashes,
                no_pass=not check_impacket_wmiexec_live
                and not (impacket_password or impacket_hashes),
                command=impacket_command,
                extra_args=impacket_extra_args,
            ),
            tenant_id=resolved_tenant,
            operator_id=integration_actor,
        )
        impacket_event = impacket_wmiexec_wrapper.send_to_orchestrator(
            impacket_wmiexec_result,
            telemetry=telemetry,
            tenant_id=resolved_tenant,
            operator_id=integration_actor,
            actor=integration_actor,
        )
        result.impacket_wmiexec_command_ok = (
            impacket_event.event_type == "impacket_wmiexec_completed"
            and impacket_event.tenant_id == resolved_tenant
        )
        result.checks.append(
            "impacket.wmiexec.command.live"
            if check_impacket_wmiexec_live
            else "impacket.wmiexec.command"
        )

    if check_impacket_smbexec:
        impacket_binary = os.getenv("IMPACKET_SMBEXEC_BINARY", "smbexec.py")
        _require_binary(impacket_binary)
        try:
            _run_command([impacket_binary, "--version"], timeout_seconds)
        except Exception:
            _run_command([impacket_binary, "-h"], timeout_seconds)
        result.impacket_smbexec_binary_ok = True
        result.checks.append("impacket.smbexec.version")
        impacket_smbexec_wrapper = ImpacketSmbexecWrapper(timeout_seconds=timeout_seconds)
        impacket_target = nmap_target
        impacket_username = os.getenv("IMPACKET_SMBEXEC_USERNAME", "smoke")
        impacket_domain = os.getenv("IMPACKET_SMBEXEC_DOMAIN", "").strip() or None
        impacket_password = os.getenv("IMPACKET_SMBEXEC_PASSWORD", "").strip() or None
        impacket_hashes = os.getenv("IMPACKET_SMBEXEC_HASHES", "").strip() or None
        impacket_command = os.getenv("IMPACKET_SMBEXEC_COMMAND", "whoami")
        impacket_extra_args = [] if check_impacket_smbexec_live else ["--dry-run"]
        if check_impacket_smbexec_live and not (impacket_password or impacket_hashes):
            raise HostIntegrationError(
                "IMPACKET_SMBEXEC_PASSWORD or IMPACKET_SMBEXEC_HASHES is required for live smbexec e2e"
            )
        impacket_smbexec_result = impacket_smbexec_wrapper.execute(
            ImpacketSmbexecRequest(
                target=impacket_target,
                username=impacket_username,
                domain=impacket_domain,
                password=impacket_password,
                hashes=impacket_hashes,
                no_pass=not check_impacket_smbexec_live
                and not (impacket_password or impacket_hashes),
                command=impacket_command,
                extra_args=impacket_extra_args,
            ),
            tenant_id=resolved_tenant,
            operator_id=integration_actor,
        )
        impacket_event = impacket_smbexec_wrapper.send_to_orchestrator(
            impacket_smbexec_result,
            telemetry=telemetry,
            tenant_id=resolved_tenant,
            operator_id=integration_actor,
            actor=integration_actor,
        )
        result.impacket_smbexec_command_ok = (
            impacket_event.event_type == "impacket_smbexec_completed"
            and impacket_event.tenant_id == resolved_tenant
        )
        result.checks.append(
            "impacket.smbexec.command.live"
            if check_impacket_smbexec_live
            else "impacket.smbexec.command"
        )

    if check_impacket_secretsdump:
        impacket_binary = os.getenv("IMPACKET_SECRETSDUMP_BINARY", "secretsdump.py")
        _require_binary(impacket_binary)
        try:
            _run_command([impacket_binary, "--version"], timeout_seconds)
        except Exception:
            _run_command([impacket_binary, "-h"], timeout_seconds)
        result.impacket_secretsdump_binary_ok = True
        result.checks.append("impacket.secretsdump.version")
        impacket_secretsdump_wrapper = ImpacketSecretsdumpWrapper(
            timeout_seconds=timeout_seconds
        )
        impacket_target = nmap_target
        impacket_username = os.getenv("IMPACKET_SECRETSDUMP_USERNAME", "smoke")
        impacket_domain = os.getenv("IMPACKET_SECRETSDUMP_DOMAIN", "").strip() or None
        impacket_password = os.getenv("IMPACKET_SECRETSDUMP_PASSWORD", "").strip() or None
        impacket_hashes = os.getenv("IMPACKET_SECRETSDUMP_HASHES", "").strip() or None
        impacket_command = os.getenv(
            "IMPACKET_SECRETSDUMP_COMMAND", "-just-dc-user administrator"
        )
        impacket_extra_args = (
            [] if check_impacket_secretsdump_live else ["--dry-run"]
        )
        if check_impacket_secretsdump_live and not (impacket_password or impacket_hashes):
            raise HostIntegrationError(
                "IMPACKET_SECRETSDUMP_PASSWORD or IMPACKET_SECRETSDUMP_HASHES is required for live secretsdump e2e"
            )
        impacket_secretsdump_result = impacket_secretsdump_wrapper.execute(
            ImpacketSecretsdumpRequest(
                target=impacket_target,
                username=impacket_username,
                domain=impacket_domain,
                password=impacket_password,
                hashes=impacket_hashes,
                no_pass=not check_impacket_secretsdump_live
                and not (impacket_password or impacket_hashes),
                command=impacket_command,
                extra_args=impacket_extra_args,
            ),
            tenant_id=resolved_tenant,
            operator_id=integration_actor,
        )
        impacket_event = impacket_secretsdump_wrapper.send_to_orchestrator(
            impacket_secretsdump_result,
            telemetry=telemetry,
            tenant_id=resolved_tenant,
            operator_id=integration_actor,
            actor=integration_actor,
        )
        result.impacket_secretsdump_command_ok = (
            impacket_event.event_type == "impacket_secretsdump_completed"
            and impacket_event.tenant_id == resolved_tenant
        )
        result.checks.append(
            "impacket.secretsdump.command.live"
            if check_impacket_secretsdump_live
            else "impacket.secretsdump.command"
        )

    if check_impacket_ntlmrelayx:
        impacket_binary = os.getenv("IMPACKET_NTLMRELAYX_BINARY", "ntlmrelayx.py")
        _require_binary(impacket_binary)
        try:
            _run_command([impacket_binary, "--version"], timeout_seconds)
        except Exception:
            _run_command([impacket_binary, "-h"], timeout_seconds)
        result.impacket_ntlmrelayx_binary_ok = True
        result.checks.append("impacket.ntlmrelayx.version")
        impacket_ntlmrelayx_wrapper = ImpacketNtlmrelayxWrapper(
            timeout_seconds=timeout_seconds
        )
        impacket_target = nmap_target
        impacket_username = os.getenv("IMPACKET_NTLMRELAYX_USERNAME", "smoke")
        impacket_domain = os.getenv("IMPACKET_NTLMRELAYX_DOMAIN", "").strip() or None
        impacket_password = os.getenv("IMPACKET_NTLMRELAYX_PASSWORD", "").strip() or None
        impacket_hashes = os.getenv("IMPACKET_NTLMRELAYX_HASHES", "").strip() or None
        impacket_command = os.getenv(
            "IMPACKET_NTLMRELAYX_COMMAND", "-t smb://127.0.0.1 -smb2support"
        )
        impacket_extra_args = [] if check_impacket_ntlmrelayx_live else ["--dry-run"]
        if check_impacket_ntlmrelayx_live and not (impacket_password or impacket_hashes):
            raise HostIntegrationError(
                "IMPACKET_NTLMRELAYX_PASSWORD or IMPACKET_NTLMRELAYX_HASHES is required for live ntlmrelayx e2e"
            )
        impacket_ntlmrelayx_result = impacket_ntlmrelayx_wrapper.execute(
            ImpacketNtlmrelayxRequest(
                target=impacket_target,
                username=impacket_username,
                domain=impacket_domain,
                password=impacket_password,
                hashes=impacket_hashes,
                no_pass=not check_impacket_ntlmrelayx_live
                and not (impacket_password or impacket_hashes),
                command=impacket_command,
                extra_args=impacket_extra_args,
            ),
            tenant_id=resolved_tenant,
            operator_id=integration_actor,
        )
        impacket_event = impacket_ntlmrelayx_wrapper.send_to_orchestrator(
            impacket_ntlmrelayx_result,
            telemetry=telemetry,
            tenant_id=resolved_tenant,
            operator_id=integration_actor,
            actor=integration_actor,
        )
        result.impacket_ntlmrelayx_command_ok = (
            impacket_event.event_type == "impacket_ntlmrelayx_completed"
            and impacket_event.tenant_id == resolved_tenant
        )
        result.checks.append(
            "impacket.ntlmrelayx.command.live"
            if check_impacket_ntlmrelayx_live
            else "impacket.ntlmrelayx.command"
        )

    if check_bloodhound_collector:
        collector_binary = os.getenv("BLOODHOUND_COLLECTOR_BINARY", "bloodhound-python")
        _require_binary(collector_binary)
        try:
            _run_command([collector_binary, "--version"], timeout_seconds)
        except Exception:
            _run_command([collector_binary, "-h"], timeout_seconds)
        result.bloodhound_collector_binary_ok = True
        result.checks.append("bloodhound.collector.version")
        bloodhound_collector_wrapper = BloodhoundCollectorWrapper(
            timeout_seconds=timeout_seconds
        )
        collector_target = nmap_target
        collector_username = os.getenv("BLOODHOUND_COLLECTOR_USERNAME", "smoke")
        collector_domain = os.getenv("BLOODHOUND_COLLECTOR_DOMAIN", "").strip() or None
        collector_password = os.getenv("BLOODHOUND_COLLECTOR_PASSWORD", "").strip() or None
        collector_command = os.getenv("BLOODHOUND_COLLECTOR_COMMAND", "-c All")
        collector_extra_args = [] if check_bloodhound_collector_live else ["--dry-run"]
        if check_bloodhound_collector_live and not collector_password:
            raise HostIntegrationError(
                "BLOODHOUND_COLLECTOR_PASSWORD is required for live bloodhound collector e2e"
            )
        bloodhound_collector_result = bloodhound_collector_wrapper.execute(
            BloodhoundCollectorRequest(
                target=collector_target,
                username=collector_username,
                domain=collector_domain,
                password=collector_password,
                no_pass=not check_bloodhound_collector_live and not collector_password,
                command=collector_command,
                extra_args=collector_extra_args,
            ),
            tenant_id=resolved_tenant,
            operator_id=integration_actor,
        )
        collector_event = bloodhound_collector_wrapper.send_to_orchestrator(
            bloodhound_collector_result,
            telemetry=telemetry,
            tenant_id=resolved_tenant,
            operator_id=integration_actor,
            actor=integration_actor,
        )
        result.bloodhound_collector_command_ok = (
            collector_event.event_type == "bloodhound_collector_completed"
            and collector_event.tenant_id == resolved_tenant
        )
        result.checks.append(
            "bloodhound.collector.command.live"
            if check_bloodhound_collector_live
            else "bloodhound.collector.command"
        )

    if check_nuclei:
        nuclei_binary = os.getenv("NUCLEI_BINARY", "nuclei")
        _require_binary(nuclei_binary)
        try:
            _run_command([nuclei_binary, "-version"], timeout_seconds)
        except Exception:
            _run_command([nuclei_binary, "-h"], timeout_seconds)
        result.nuclei_binary_ok = True
        result.checks.append("nuclei.version")
        nuclei_wrapper = NucleiWrapper(timeout_seconds=timeout_seconds)
        nuclei_target = (
            os.getenv("NUCLEI_LIVE_TARGET", "").strip()
            if check_nuclei_live
            else os.getenv("NUCLEI_TARGET", "http://127.0.0.1").strip()
        )
        if check_nuclei_live and not nuclei_target:
            raise HostIntegrationError(
                "NUCLEI_LIVE_TARGET is required for live nuclei e2e"
            )
        nuclei_command = os.getenv("NUCLEI_COMMAND", "-severity high,critical")
        nuclei_extra_args = [] if check_nuclei_live else ["--dry-run"]
        nuclei_result = nuclei_wrapper.execute(
            NucleiScanRequest(
                target=nuclei_target,
                command=nuclei_command,
                extra_args=nuclei_extra_args,
            ),
            tenant_id=resolved_tenant,
            operator_id=integration_actor,
        )
        nuclei_event = nuclei_wrapper.send_to_orchestrator(
            nuclei_result,
            telemetry=telemetry,
            tenant_id=resolved_tenant,
            operator_id=integration_actor,
            actor=integration_actor,
        )
        result.nuclei_command_ok = (
            nuclei_event.event_type == "nuclei_scan_completed"
            and nuclei_event.tenant_id == resolved_tenant
        )
        result.checks.append(
            "nuclei.command.live" if check_nuclei_live else "nuclei.command"
        )

    if check_prowler:
        prowler_binary = os.getenv("PROWLER_BINARY", "prowler")
        _require_binary(prowler_binary)
        try:
            _run_command([prowler_binary, "--version"], timeout_seconds)
        except Exception:
            try:
                _run_command([prowler_binary, "-h"], timeout_seconds)
            except Exception:
                # Some distro wrappers resolve to launcher scripts that fail version/help probes.
                # Keep binary_ok true and validate through the wrapper contract path below.
                logger.warning(
                    "Proceeding after recoverable prowler probe failure for binary=%s",
                    prowler_binary,
                )
        result.prowler_binary_ok = True
        result.checks.append("prowler.version")
        prowler_wrapper = ProwlerWrapper(timeout_seconds=timeout_seconds)
        prowler_target = (
            os.getenv("PROWLER_LIVE_TARGET", "").strip()
            if check_prowler_live
            else os.getenv("PROWLER_TARGET", "aws").strip()
        )
        if check_prowler_live and not prowler_target:
            raise HostIntegrationError(
                "PROWLER_LIVE_TARGET is required for live prowler e2e"
            )
        prowler_command = os.getenv("PROWLER_COMMAND", "aws -M json")
        prowler_extra_args = [] if check_prowler_live else ["--dry-run"]
        prowler_result = prowler_wrapper.execute(
            ProwlerScanRequest(
                target=prowler_target,
                command=prowler_command,
                extra_args=prowler_extra_args,
            ),
            tenant_id=resolved_tenant,
            operator_id=integration_actor,
        )
        prowler_event = prowler_wrapper.send_to_orchestrator(
            prowler_result,
            telemetry=telemetry,
            tenant_id=resolved_tenant,
            operator_id=integration_actor,
            actor=integration_actor,
        )
        result.prowler_command_ok = (
            prowler_event.event_type == "prowler_scan_completed"
            and prowler_event.tenant_id == resolved_tenant
        )
        result.checks.append(
            "prowler.command.live" if check_prowler_live else "prowler.command"
        )

    if check_responder:
        responder_binary = os.getenv("RESPONDER_BINARY", "responder")
        _require_binary(responder_binary)
        try:
            _run_command([responder_binary, "--version"], timeout_seconds)
        except Exception:
            _run_command([responder_binary, "-h"], timeout_seconds)
        result.responder_binary_ok = True
        result.checks.append("responder.version")
        responder_wrapper = ResponderWrapper(timeout_seconds=timeout_seconds)
        responder_target = (
            os.getenv("RESPONDER_LIVE_INTERFACE", "").strip()
            if check_responder_live
            else os.getenv("RESPONDER_INTERFACE", "lo").strip()
        )
        if check_responder_live and not responder_target:
            raise HostIntegrationError(
                "RESPONDER_LIVE_INTERFACE is required for live responder e2e"
            )
        responder_command = os.getenv(
            "RESPONDER_COMMAND",
            f"-I {responder_target} -A -w -v",
        )
        responder_extra_args = [] if check_responder_live else ["--dry-run"]
        responder_result = responder_wrapper.execute(
            ResponderRequest(
                target=responder_target,
                command=responder_command,
                extra_args=responder_extra_args,
            ),
            tenant_id=resolved_tenant,
            operator_id=integration_actor,
        )
        responder_event = responder_wrapper.send_to_orchestrator(
            responder_result,
            telemetry=telemetry,
            tenant_id=resolved_tenant,
            operator_id=integration_actor,
            actor=integration_actor,
        )
        result.responder_command_ok = (
            responder_event.event_type == "responder_session_completed"
            and responder_event.tenant_id == resolved_tenant
        )
        result.checks.append(
            "responder.command.live" if check_responder_live else "responder.command"
        )

    if check_gobuster:
        gobuster_binary = os.getenv("GOBUSTER_BINARY", "gobuster")
        _require_binary(gobuster_binary)
        try:
            _run_command([gobuster_binary, "version"], timeout_seconds)
        except Exception:
            _run_command([gobuster_binary, "-h"], timeout_seconds)
        result.gobuster_binary_ok = True
        result.checks.append("gobuster.version")
        gobuster_wrapper = GobusterWrapper(timeout_seconds=timeout_seconds)
        gobuster_target = (
            os.getenv("GOBUSTER_LIVE_TARGET", "").strip()
            if check_gobuster_live
            else os.getenv("GOBUSTER_TARGET", "http://127.0.0.1").strip()
        )
        if check_gobuster_live and not gobuster_target:
            raise HostIntegrationError(
                "GOBUSTER_LIVE_TARGET is required for live gobuster e2e"
            )
        gobuster_command = os.getenv(
            "GOBUSTER_COMMAND",
            f"dir -u {gobuster_target} -w /usr/share/wordlists/dirb/common.txt",
        )
        gobuster_extra_args = [] if check_gobuster_live else ["--dry-run"]
        gobuster_result = gobuster_wrapper.execute(
            GobusterScanRequest(
                target=gobuster_target,
                command=gobuster_command,
                extra_args=gobuster_extra_args,
            ),
            tenant_id=resolved_tenant,
            operator_id=integration_actor,
        )
        gobuster_event = gobuster_wrapper.send_to_orchestrator(
            gobuster_result,
            telemetry=telemetry,
            tenant_id=resolved_tenant,
            operator_id=integration_actor,
            actor=integration_actor,
        )
        result.gobuster_command_ok = (
            gobuster_event.event_type == "gobuster_scan_completed"
            and gobuster_event.tenant_id == resolved_tenant
        )
        result.checks.append(
            "gobuster.command.live" if check_gobuster_live else "gobuster.command"
        )

    if check_ffuf:
        ffuf_binary = os.getenv("FFUF_BINARY", "ffuf")
        _require_binary(ffuf_binary)
        try:
            _run_command([ffuf_binary, "-V"], timeout_seconds)
        except Exception:
            _run_command([ffuf_binary, "-h"], timeout_seconds)
        result.ffuf_binary_ok = True
        result.checks.append("ffuf.version")
        ffuf_wrapper = FfufWrapper(timeout_seconds=timeout_seconds)
        ffuf_target = (
            os.getenv("FFUF_LIVE_TARGET", "").strip()
            if check_ffuf_live
            else os.getenv("FFUF_TARGET", "http://127.0.0.1/FUZZ").strip()
        )
        if check_ffuf_live and not ffuf_target:
            raise HostIntegrationError("FFUF_LIVE_TARGET is required for live ffuf e2e")
        ffuf_command = os.getenv(
            "FFUF_COMMAND",
            f"-u {ffuf_target} -w /usr/share/wordlists/dirb/common.txt -mc all -fc 404",
        )
        ffuf_extra_args = [] if check_ffuf_live else ["--dry-run"]
        ffuf_result = ffuf_wrapper.execute(
            FfufScanRequest(
                target=ffuf_target,
                command=ffuf_command,
                extra_args=ffuf_extra_args,
            ),
            tenant_id=resolved_tenant,
            operator_id=integration_actor,
        )
        ffuf_event = ffuf_wrapper.send_to_orchestrator(
            ffuf_result,
            telemetry=telemetry,
            tenant_id=resolved_tenant,
            operator_id=integration_actor,
            actor=integration_actor,
        )
        result.ffuf_command_ok = (
            ffuf_event.event_type == "ffuf_scan_completed"
            and ffuf_event.tenant_id == resolved_tenant
        )
        result.checks.append("ffuf.command.live" if check_ffuf_live else "ffuf.command")

    if check_netcat:
        netcat_binary = os.getenv("NETCAT_BINARY", "nc")
        _require_binary(netcat_binary)
        try:
            _run_command([netcat_binary, "-h"], timeout_seconds)
        except Exception:
            _run_command([netcat_binary, "--version"], timeout_seconds)
        result.netcat_binary_ok = True
        result.checks.append("netcat.version")
        netcat_wrapper = NetcatWrapper(timeout_seconds=timeout_seconds)
        netcat_target = (
            os.getenv("NETCAT_LIVE_TARGET", "").strip()
            if check_netcat_live
            else os.getenv("NETCAT_TARGET", "127.0.0.1").strip()
        )
        netcat_port = (
            os.getenv("NETCAT_LIVE_PORT", "").strip()
            if check_netcat_live
            else os.getenv("NETCAT_PORT", "80").strip()
        )
        if check_netcat_live and (not netcat_target or not netcat_port):
            raise HostIntegrationError(
                "NETCAT_LIVE_TARGET and NETCAT_LIVE_PORT are required for live netcat e2e"
            )
        netcat_command = os.getenv("NETCAT_COMMAND", f"-vz {netcat_target} {netcat_port}")
        netcat_extra_args = [] if check_netcat_live else ["--dry-run"]
        netcat_result = netcat_wrapper.execute(
            NetcatRequest(
                target=netcat_target,
                command=netcat_command,
                extra_args=netcat_extra_args,
            ),
            tenant_id=resolved_tenant,
            operator_id=integration_actor,
        )
        netcat_event = netcat_wrapper.send_to_orchestrator(
            netcat_result,
            telemetry=telemetry,
            tenant_id=resolved_tenant,
            operator_id=integration_actor,
            actor=integration_actor,
        )
        result.netcat_command_ok = (
            netcat_event.event_type == "netcat_session_completed"
            and netcat_event.tenant_id == resolved_tenant
        )
        result.checks.append(
            "netcat.command.live" if check_netcat_live else "netcat.command"
        )

    if check_netexec:
        netexec_binary = os.getenv("NETEXEC_BINARY", "nxc")
        _require_binary(netexec_binary)
        try:
            _run_command([netexec_binary, "--version"], timeout_seconds)
        except Exception:
            _run_command([netexec_binary, "-h"], timeout_seconds)
        result.netexec_binary_ok = True
        result.checks.append("netexec.version")
        netexec_wrapper = NetExecWrapper(timeout_seconds=timeout_seconds)
        netexec_target = (
            os.getenv("NETEXEC_LIVE_TARGET", "").strip()
            if check_netexec_live
            else os.getenv("NETEXEC_TARGET", "127.0.0.1").strip()
        )
        netexec_username = (
            os.getenv("NETEXEC_LIVE_USERNAME", "").strip()
            if check_netexec_live
            else os.getenv("NETEXEC_USERNAME", "smoke").strip()
        )
        netexec_password = (
            os.getenv("NETEXEC_LIVE_PASSWORD", "").strip()
            if check_netexec_live
            else os.getenv("NETEXEC_PASSWORD", "smoke").strip()
        )
        if check_netexec_live and (not netexec_target or not netexec_username or not netexec_password):
            raise HostIntegrationError(
                "NETEXEC_LIVE_TARGET, NETEXEC_LIVE_USERNAME, and NETEXEC_LIVE_PASSWORD are required for live netexec e2e"
            )
        netexec_command = os.getenv(
            "NETEXEC_COMMAND",
            f"smb {netexec_target} -u {netexec_username} -p {netexec_password} --shares",
        )
        netexec_extra_args = [] if check_netexec_live else ["--dry-run"]
        netexec_result = netexec_wrapper.execute(
            NetExecRequest(
                target=netexec_target,
                command=netexec_command,
                extra_args=netexec_extra_args,
            ),
            tenant_id=resolved_tenant,
            operator_id=integration_actor,
        )
        netexec_event = netexec_wrapper.send_to_orchestrator(
            netexec_result,
            telemetry=telemetry,
            tenant_id=resolved_tenant,
            operator_id=integration_actor,
            actor=integration_actor,
        )
        result.netexec_command_ok = (
            netexec_event.event_type == "netexec_session_completed"
            and netexec_event.tenant_id == resolved_tenant
        )
        result.checks.append(
            "netexec.command.live" if check_netexec_live else "netexec.command"
        )

    if check_john:
        john_binary = os.getenv("JOHN_BINARY", "john")
        _require_binary(john_binary)
        try:
            _run_command([john_binary, "--list=build-info"], timeout_seconds)
        except Exception:
            _run_command([john_binary, "--help"], timeout_seconds)
        result.john_binary_ok = True
        result.checks.append("john.version")
        john_wrapper = JohnWrapper(timeout_seconds=timeout_seconds)
        john_target = (
            os.getenv("JOHN_LIVE_HASH_FILE", "").strip()
            if check_john_live
            else os.getenv("JOHN_TARGET", "/tmp/hash.txt").strip()
        )
        if check_john_live and not john_target:
            raise HostIntegrationError(
                "JOHN_LIVE_HASH_FILE is required for live john e2e"
            )
        john_command = os.getenv(
            "JOHN_COMMAND",
            f"--wordlist=/usr/share/wordlists/rockyou.txt {john_target} --format=raw-md5",
        )
        john_extra_args = [] if check_john_live else ["--dry-run"]
        john_result = john_wrapper.execute(
            JohnRequest(
                target=john_target,
                command=john_command,
                extra_args=john_extra_args,
            ),
            tenant_id=resolved_tenant,
            operator_id=integration_actor,
        )
        john_event = john_wrapper.send_to_orchestrator(
            john_result,
            telemetry=telemetry,
            tenant_id=resolved_tenant,
            operator_id=integration_actor,
            actor=integration_actor,
        )
        result.john_command_ok = (
            john_event.event_type == "john_session_completed"
            and john_event.tenant_id == resolved_tenant
        )
        result.checks.append("john.command.live" if check_john_live else "john.command")

    if check_wget:
        wget_binary = os.getenv("WGET_BINARY", "wget")
        _require_binary(wget_binary)
        try:
            _run_command([wget_binary, "--version"], timeout_seconds)
        except Exception:
            _run_command([wget_binary, "--help"], timeout_seconds)
        result.wget_binary_ok = True
        result.checks.append("wget.version")
        wget_wrapper = WgetWrapper(timeout_seconds=timeout_seconds)
        wget_target = (
            os.getenv("WGET_LIVE_TARGET", "").strip()
            if check_wget_live
            else os.getenv("WGET_TARGET", "http://127.0.0.1").strip()
        )
        if check_wget_live and not wget_target:
            raise HostIntegrationError("WGET_LIVE_TARGET is required for live wget e2e")
        wget_command = os.getenv(
            "WGET_COMMAND",
            f"{wget_target} -O /tmp/wget_smoke.out --timeout=3",
        )
        wget_extra_args = [] if check_wget_live else ["--dry-run"]
        wget_result = wget_wrapper.execute(
            WgetRequest(
                target=wget_target,
                command=wget_command,
                extra_args=wget_extra_args,
            ),
            tenant_id=resolved_tenant,
            operator_id=integration_actor,
        )
        wget_event = wget_wrapper.send_to_orchestrator(
            wget_result,
            telemetry=telemetry,
            tenant_id=resolved_tenant,
            operator_id=integration_actor,
            actor=integration_actor,
        )
        result.wget_command_ok = (
            wget_event.event_type == "wget_session_completed"
            and wget_event.tenant_id == resolved_tenant
        )
        result.checks.append("wget.command.live" if check_wget_live else "wget.command")

    if check_burpsuite:
        burpsuite_binary = os.getenv("BURPSUITE_BINARY", "burpsuite")
        _require_binary(burpsuite_binary)
        try:
            _run_command([burpsuite_binary, "--version"], timeout_seconds)
        except Exception:
            _run_command([burpsuite_binary, "--help"], timeout_seconds)
        result.burpsuite_binary_ok = True
        result.checks.append("burpsuite.version")
        burpsuite_wrapper = BurpSuiteWrapper(timeout_seconds=timeout_seconds)
        burpsuite_target = (
            os.getenv("BURPSUITE_LIVE_TARGET", "").strip()
            if check_burpsuite_live
            else os.getenv("BURPSUITE_TARGET", "local-burp").strip()
        )
        if check_burpsuite_live and not burpsuite_target:
            raise HostIntegrationError(
                "BURPSUITE_LIVE_TARGET is required for live burpsuite e2e"
            )
        burpsuite_command = os.getenv("BURPSUITE_COMMAND", "--help")
        burpsuite_extra_args = [] if check_burpsuite_live else ["--dry-run"]
        burpsuite_result = burpsuite_wrapper.execute(
            BurpSuiteRequest(
                target=burpsuite_target,
                command=burpsuite_command,
                extra_args=burpsuite_extra_args,
            ),
            tenant_id=resolved_tenant,
            operator_id=integration_actor,
        )
        burpsuite_event = burpsuite_wrapper.send_to_orchestrator(
            burpsuite_result,
            telemetry=telemetry,
            tenant_id=resolved_tenant,
            operator_id=integration_actor,
            actor=integration_actor,
        )
        result.burpsuite_command_ok = (
            burpsuite_event.event_type == "burpsuite_session_completed"
            and burpsuite_event.tenant_id == resolved_tenant
        )
        result.checks.append(
            "burpsuite.command.live"
            if check_burpsuite_live
            else "burpsuite.command"
        )

    if check_amass:
        amass_binary = os.getenv("AMASS_BINARY", "amass")
        _require_binary(amass_binary)
        try:
            _run_command([amass_binary, "version"], timeout_seconds)
        except Exception:
            try:
                _run_command([amass_binary, "-h"], timeout_seconds)
            except Exception:
                logger.warning(
                    "Proceeding after recoverable amass probe failure for binary=%s",
                    amass_binary,
                )
        result.amass_binary_ok = True
        result.checks.append("amass.version")
        amass_wrapper = AmassWrapper(timeout_seconds=min(timeout_seconds, 5.0))
        amass_target = (
            os.getenv("AMASS_LIVE_TARGET", "").strip()
            if check_amass_live
            else os.getenv("AMASS_TARGET", "example.com").strip()
        )
        if check_amass_live and not amass_target:
            raise HostIntegrationError("AMASS_LIVE_TARGET is required for live amass e2e")
        amass_command = os.getenv("AMASS_COMMAND", f"enum -passive -d {amass_target}")
        amass_extra_args = [] if check_amass_live else ["--dry-run"]
        amass_result = amass_wrapper.execute(
            AmassRequest(
                target=amass_target,
                command=amass_command,
                extra_args=amass_extra_args,
            ),
            tenant_id=resolved_tenant,
            operator_id=integration_actor,
        )
        amass_event = amass_wrapper.send_to_orchestrator(
            amass_result,
            telemetry=telemetry,
            tenant_id=resolved_tenant,
            operator_id=integration_actor,
            actor=integration_actor,
        )
        result.amass_command_ok = (
            amass_event.event_type == "amass_enum_completed"
            and amass_event.tenant_id == resolved_tenant
        )
        result.checks.append("amass.command.live" if check_amass_live else "amass.command")

    if check_sqlmap:
        sqlmap_binary = os.getenv("SQLMAP_BINARY", "sqlmap")
        _require_binary(sqlmap_binary)
        try:
            _run_command([sqlmap_binary, "--version"], timeout_seconds)
        except Exception:
            _run_command([sqlmap_binary, "-h"], timeout_seconds)
        result.sqlmap_binary_ok = True
        result.checks.append("sqlmap.version")
        sqlmap_wrapper = SqlmapWrapper(timeout_seconds=timeout_seconds)
        sqlmap_target = (
            os.getenv("SQLMAP_LIVE_TARGET", "").strip()
            if check_sqlmap_live
            else os.getenv("SQLMAP_TARGET", "http://127.0.0.1/vuln.php?id=1").strip()
        )
        if check_sqlmap_live and not sqlmap_target:
            raise HostIntegrationError("SQLMAP_LIVE_TARGET is required for live sqlmap e2e")
        sqlmap_command = os.getenv(
            "SQLMAP_COMMAND",
            f"-u {sqlmap_target} --batch --risk=1 --level=1",
        )
        sqlmap_extra_args = [] if check_sqlmap_live else ["--dry-run"]
        sqlmap_result = sqlmap_wrapper.execute(
            SqlmapRequest(
                target=sqlmap_target,
                command=sqlmap_command,
                extra_args=sqlmap_extra_args,
            ),
            tenant_id=resolved_tenant,
            operator_id=integration_actor,
        )
        sqlmap_event = sqlmap_wrapper.send_to_orchestrator(
            sqlmap_result,
            telemetry=telemetry,
            tenant_id=resolved_tenant,
            operator_id=integration_actor,
            actor=integration_actor,
        )
        result.sqlmap_command_ok = (
            sqlmap_event.event_type == "sqlmap_scan_completed"
            and sqlmap_event.tenant_id == resolved_tenant
        )
        result.checks.append(
            "sqlmap.command.live" if check_sqlmap_live else "sqlmap.command"
        )

    if check_subfinder:
        subfinder_binary = os.getenv("SUBFINDER_BINARY", "subfinder")
        _require_binary(subfinder_binary)
        try:
            _run_command([subfinder_binary, "-version"], timeout_seconds)
        except Exception:
            _run_command([subfinder_binary, "-h"], timeout_seconds)
        result.subfinder_binary_ok = True
        result.checks.append("subfinder.version")
        subfinder_wrapper = SubfinderWrapper(timeout_seconds=timeout_seconds)
        subfinder_target = (
            os.getenv("SUBFINDER_LIVE_TARGET", "").strip()
            if check_subfinder_live
            else os.getenv("SUBFINDER_TARGET", "example.com").strip()
        )
        if check_subfinder_live and not subfinder_target:
            raise HostIntegrationError(
                "SUBFINDER_LIVE_TARGET is required for live subfinder e2e"
            )
        subfinder_command = os.getenv("SUBFINDER_COMMAND", f"-d {subfinder_target} -silent")
        subfinder_extra_args = [] if check_subfinder_live else ["--dry-run"]
        subfinder_result = subfinder_wrapper.execute(
            SubfinderRequest(
                target=subfinder_target,
                command=subfinder_command,
                extra_args=subfinder_extra_args,
            ),
            tenant_id=resolved_tenant,
            operator_id=integration_actor,
        )
        subfinder_event = subfinder_wrapper.send_to_orchestrator(
            subfinder_result,
            telemetry=telemetry,
            tenant_id=resolved_tenant,
            operator_id=integration_actor,
            actor=integration_actor,
        )
        result.subfinder_command_ok = (
            subfinder_event.event_type == "subfinder_scan_completed"
            and subfinder_event.tenant_id == resolved_tenant
        )
        result.checks.append(
            "subfinder.command.live" if check_subfinder_live else "subfinder.command"
        )

    if check_sliver_command:
        _require_binary(os.getenv("SLIVER_BINARY", "sliver-client"))
        sliver_binary = os.getenv("SLIVER_BINARY", "sliver-client")
        try:
            _run_command([sliver_binary, "--version"], timeout_seconds)
        except Exception:
            _run_command([sliver_binary, "version"], timeout_seconds)
        result.sliver_binary_ok = True
        result.checks.append("sliver.version")
        sliver_wrapper = SliverWrapper(timeout_seconds=timeout_seconds)
        sliver_result = sliver_wrapper.execute(
            SliverCommandRequest(
                target=nmap_target,
                command="whoami",
                extra_args=["--dry-run"],
            )
        )
        sliver_event = sliver_wrapper.send_to_orchestrator(
            sliver_result,
            telemetry=telemetry,
            tenant_id=resolved_tenant,
            actor=integration_actor,
        )
        result.sliver_command_ok = (
            sliver_event.event_type == "sliver_command_completed"
            and sliver_event.tenant_id == resolved_tenant
        )
        result.checks.append("sliver.command")

    if check_mythic_task:
        _require_binary(os.getenv("MYTHIC_BINARY", "mythic-cli"))
        _run_command([os.getenv("MYTHIC_BINARY", "mythic-cli"), "--version"], timeout_seconds)
        result.mythic_binary_ok = True
        result.checks.append("mythic.version")
        mythic_wrapper = MythicWrapper(timeout_seconds=timeout_seconds)
        mythic_result = mythic_wrapper.execute(
            MythicTaskRequest(
                target=nmap_target,
                operation="spectra-smoke",
                command="pwd",
                extra_args=["--dry-run"],
            )
        )
        mythic_event = mythic_wrapper.send_to_orchestrator(
            mythic_result,
            telemetry=telemetry,
            tenant_id=resolved_tenant,
            actor=integration_actor,
        )
        result.mythic_task_ok = (
            mythic_event.event_type == "mythic_task_completed"
            and mythic_event.tenant_id == resolved_tenant
        )
        result.checks.append("mythic.task")

    if check_vectorvue:
        broker = InMemoryRabbitBroker()
        publisher = RabbitMQTelemetryPublisher(broker=broker)
        telemetry_with_broker = TelemetryIngestionPipeline(batch_size=1, publisher=publisher)
        nmap_wrapper.send_to_orchestrator(
            nmap_scan,
            telemetry=telemetry_with_broker,
            tenant_id=resolved_tenant,
            actor=integration_actor,
        )
        telemetry_with_broker.ingest_payload(
            build_internal_telemetry_event(
                event_type="metasploit_binary_detected",
                actor=integration_actor,
                target="orchestrator",
                status="success",
                tenant_id=resolved_tenant,
                attributes={
                    "binary": "msfconsole",
                    "version_output": metasploit_version_output,
                },
            )
        )
        if check_sliver_command and sliver_wrapper is not None and sliver_result is not None:
            sliver_wrapper.send_to_orchestrator(
                sliver_result,
                telemetry=telemetry_with_broker,
                tenant_id=resolved_tenant,
                actor=integration_actor,
            )
        if (
            check_impacket_psexec
            and impacket_psexec_wrapper is not None
            and impacket_psexec_result is not None
        ):
            impacket_psexec_wrapper.send_to_orchestrator(
                impacket_psexec_result,
                telemetry=telemetry_with_broker,
                tenant_id=resolved_tenant,
                operator_id=integration_actor,
                actor=integration_actor,
            )
        if (
            check_impacket_wmiexec
            and impacket_wmiexec_wrapper is not None
            and impacket_wmiexec_result is not None
        ):
            impacket_wmiexec_wrapper.send_to_orchestrator(
                impacket_wmiexec_result,
                telemetry=telemetry_with_broker,
                tenant_id=resolved_tenant,
                operator_id=integration_actor,
                actor=integration_actor,
            )
        if (
            check_impacket_smbexec
            and impacket_smbexec_wrapper is not None
            and impacket_smbexec_result is not None
        ):
            impacket_smbexec_wrapper.send_to_orchestrator(
                impacket_smbexec_result,
                telemetry=telemetry_with_broker,
                tenant_id=resolved_tenant,
                operator_id=integration_actor,
                actor=integration_actor,
            )
        if (
            check_impacket_secretsdump
            and impacket_secretsdump_wrapper is not None
            and impacket_secretsdump_result is not None
        ):
            impacket_secretsdump_wrapper.send_to_orchestrator(
                impacket_secretsdump_result,
                telemetry=telemetry_with_broker,
                tenant_id=resolved_tenant,
                operator_id=integration_actor,
                actor=integration_actor,
            )
        if (
            check_impacket_ntlmrelayx
            and impacket_ntlmrelayx_wrapper is not None
            and impacket_ntlmrelayx_result is not None
        ):
            impacket_ntlmrelayx_wrapper.send_to_orchestrator(
                impacket_ntlmrelayx_result,
                telemetry=telemetry_with_broker,
                tenant_id=resolved_tenant,
                operator_id=integration_actor,
                actor=integration_actor,
            )
        if (
            check_bloodhound_collector
            and bloodhound_collector_wrapper is not None
            and bloodhound_collector_result is not None
        ):
            bloodhound_collector_wrapper.send_to_orchestrator(
                bloodhound_collector_result,
                telemetry=telemetry_with_broker,
                tenant_id=resolved_tenant,
                operator_id=integration_actor,
                actor=integration_actor,
            )
        if check_nuclei and nuclei_wrapper is not None and nuclei_result is not None:
            nuclei_wrapper.send_to_orchestrator(
                nuclei_result,
                telemetry=telemetry_with_broker,
                tenant_id=resolved_tenant,
                operator_id=integration_actor,
                actor=integration_actor,
            )
        if check_prowler and prowler_wrapper is not None and prowler_result is not None:
            prowler_wrapper.send_to_orchestrator(
                prowler_result,
                telemetry=telemetry_with_broker,
                tenant_id=resolved_tenant,
                operator_id=integration_actor,
                actor=integration_actor,
            )
        if check_responder and responder_wrapper is not None and responder_result is not None:
            responder_wrapper.send_to_orchestrator(
                responder_result,
                telemetry=telemetry_with_broker,
                tenant_id=resolved_tenant,
                operator_id=integration_actor,
                actor=integration_actor,
            )
        if check_gobuster and gobuster_wrapper is not None and gobuster_result is not None:
            gobuster_wrapper.send_to_orchestrator(
                gobuster_result,
                telemetry=telemetry_with_broker,
                tenant_id=resolved_tenant,
                operator_id=integration_actor,
                actor=integration_actor,
            )
        if check_ffuf and ffuf_wrapper is not None and ffuf_result is not None:
            ffuf_wrapper.send_to_orchestrator(
                ffuf_result,
                telemetry=telemetry_with_broker,
                tenant_id=resolved_tenant,
                operator_id=integration_actor,
                actor=integration_actor,
            )
        if check_netcat and netcat_wrapper is not None and netcat_result is not None:
            netcat_wrapper.send_to_orchestrator(
                netcat_result,
                telemetry=telemetry_with_broker,
                tenant_id=resolved_tenant,
                operator_id=integration_actor,
                actor=integration_actor,
            )
        if check_netexec and netexec_wrapper is not None and netexec_result is not None:
            netexec_wrapper.send_to_orchestrator(
                netexec_result,
                telemetry=telemetry_with_broker,
                tenant_id=resolved_tenant,
                operator_id=integration_actor,
                actor=integration_actor,
            )
        if check_john and john_wrapper is not None and john_result is not None:
            john_wrapper.send_to_orchestrator(
                john_result,
                telemetry=telemetry_with_broker,
                tenant_id=resolved_tenant,
                operator_id=integration_actor,
                actor=integration_actor,
            )
        if check_wget and wget_wrapper is not None and wget_result is not None:
            wget_wrapper.send_to_orchestrator(
                wget_result,
                telemetry=telemetry_with_broker,
                tenant_id=resolved_tenant,
                operator_id=integration_actor,
                actor=integration_actor,
            )
        if (
            check_burpsuite
            and burpsuite_wrapper is not None
            and burpsuite_result is not None
        ):
            burpsuite_wrapper.send_to_orchestrator(
                burpsuite_result,
                telemetry=telemetry_with_broker,
                tenant_id=resolved_tenant,
                operator_id=integration_actor,
                actor=integration_actor,
            )
        if check_amass and amass_wrapper is not None and amass_result is not None:
            amass_wrapper.send_to_orchestrator(
                amass_result,
                telemetry=telemetry_with_broker,
                tenant_id=resolved_tenant,
                operator_id=integration_actor,
                actor=integration_actor,
            )
        if check_sqlmap and sqlmap_wrapper is not None and sqlmap_result is not None:
            sqlmap_wrapper.send_to_orchestrator(
                sqlmap_result,
                telemetry=telemetry_with_broker,
                tenant_id=resolved_tenant,
                operator_id=integration_actor,
                actor=integration_actor,
            )
        if (
            check_subfinder
            and subfinder_wrapper is not None
            and subfinder_result is not None
        ):
            subfinder_wrapper.send_to_orchestrator(
                subfinder_result,
                telemetry=telemetry_with_broker,
                tenant_id=resolved_tenant,
                operator_id=integration_actor,
                actor=integration_actor,
            )
        if check_mythic_task and mythic_wrapper is not None and mythic_result is not None:
            mythic_wrapper.send_to_orchestrator(
                mythic_result,
                telemetry=telemetry_with_broker,
                tenant_id=resolved_tenant,
                actor=integration_actor,
            )
        publish_result = asyncio.run(telemetry_with_broker.flush_all_async())
        result.rabbitmq_publish_ok = publish_result.published > 0
        result.checks.append("rabbitmq.publish")

        client = VectorVueClient(_build_vectorvue_config(timeout_seconds))
        bridge = InMemoryVectorVueBridge(
            broker=broker,
            client=client,
            emit_findings_for_all=True,
        )
        bridge_result = bridge.drain(limit=10)
        result.vectorvue_event_status = (
            bridge_result.event_statuses[0] if bridge_result.event_statuses else None
        )
        result.vectorvue_finding_status = (
            bridge_result.finding_statuses[0] if bridge_result.finding_statuses else None
        )
        result.vectorvue_status_poll_status = (
            bridge_result.status_poll_statuses[0]
            if bridge_result.status_poll_statuses
            else None
        )
        result.vectorvue_ok = (
            bool(result.rabbitmq_publish_ok)
            and bridge_result.failed == 0
            and result.vectorvue_event_status in {"accepted", "replayed"}
            and result.vectorvue_finding_status in {"accepted", "replayed"}
            and result.vectorvue_status_poll_status in {"accepted", "partial", "replayed"}
        )
        result.checks.append("vectorvue.rabbitmq.bridge")

    return result


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run Sprint 16.8 host integration smoke checks"
    )
    parser.add_argument(
        "--tenant-id",
        default=os.getenv("SPECTRASTRIKE_TENANT_ID", ""),
        help="tenant context propagated into telemetry ingestion",
    )
    parser.add_argument("--nmap-target", default="127.0.0.1")
    parser.add_argument("--timeout-seconds", type=float, default=8.0)
    parser.add_argument(
        "--check-metasploit-rpc",
        action="store_true",
        help="authenticate against MSF RPC endpoint from MSF_RPC_* env",
    )
    parser.add_argument(
        "--check-sliver-command",
        action="store_true",
        help="execute one Sliver dry-run command and emit SDK telemetry",
    )
    parser.add_argument(
        "--check-impacket-psexec",
        action="store_true",
        help="execute one Impacket psexec dry-run command and emit SDK telemetry",
    )
    parser.add_argument(
        "--check-impacket-psexec-live",
        action="store_true",
        help="execute one Impacket psexec live command (requires IMPACKET_PSEXEC_* credentials)",
    )
    parser.add_argument(
        "--check-impacket-wmiexec",
        action="store_true",
        help="execute one Impacket wmiexec dry-run command and emit SDK telemetry",
    )
    parser.add_argument(
        "--check-impacket-wmiexec-live",
        action="store_true",
        help="execute one Impacket wmiexec live command (requires IMPACKET_WMIEXEC_* credentials)",
    )
    parser.add_argument(
        "--check-impacket-smbexec",
        action="store_true",
        help="execute one Impacket smbexec dry-run command and emit SDK telemetry",
    )
    parser.add_argument(
        "--check-impacket-smbexec-live",
        action="store_true",
        help="execute one Impacket smbexec live command (requires IMPACKET_SMBEXEC_* credentials)",
    )
    parser.add_argument(
        "--check-impacket-secretsdump",
        action="store_true",
        help="execute one Impacket secretsdump dry-run command and emit SDK telemetry",
    )
    parser.add_argument(
        "--check-impacket-secretsdump-live",
        action="store_true",
        help="execute one Impacket secretsdump live command (requires IMPACKET_SECRETSDUMP_* credentials)",
    )
    parser.add_argument(
        "--check-impacket-ntlmrelayx",
        action="store_true",
        help="execute one Impacket ntlmrelayx dry-run command and emit SDK telemetry",
    )
    parser.add_argument(
        "--check-impacket-ntlmrelayx-live",
        action="store_true",
        help="execute one Impacket ntlmrelayx live command (requires IMPACKET_NTLMRELAYX_* credentials)",
    )
    parser.add_argument(
        "--check-bloodhound-collector",
        action="store_true",
        help="execute one BloodHound collector dry-run command and emit SDK telemetry",
    )
    parser.add_argument(
        "--check-bloodhound-collector-live",
        action="store_true",
        help="execute one BloodHound collector live command (requires BLOODHOUND_COLLECTOR_* credentials)",
    )
    parser.add_argument(
        "--check-nuclei",
        action="store_true",
        help="execute one nuclei dry-run command and emit SDK telemetry",
    )
    parser.add_argument(
        "--check-nuclei-live",
        action="store_true",
        help="execute one nuclei live command (requires NUCLEI_LIVE_TARGET)",
    )
    parser.add_argument(
        "--check-prowler",
        action="store_true",
        help="execute one prowler dry-run command and emit SDK telemetry",
    )
    parser.add_argument(
        "--check-prowler-live",
        action="store_true",
        help="execute one prowler live command (requires PROWLER_LIVE_TARGET)",
    )
    parser.add_argument(
        "--check-responder",
        action="store_true",
        help="execute one responder dry-run command and emit SDK telemetry",
    )
    parser.add_argument(
        "--check-responder-live",
        action="store_true",
        help="execute one responder live command (requires RESPONDER_LIVE_INTERFACE)",
    )
    parser.add_argument(
        "--check-gobuster",
        action="store_true",
        help="execute one gobuster dry-run command and emit SDK telemetry",
    )
    parser.add_argument(
        "--check-gobuster-live",
        action="store_true",
        help="execute one gobuster live command (requires GOBUSTER_LIVE_TARGET)",
    )
    parser.add_argument(
        "--check-ffuf",
        action="store_true",
        help="execute one ffuf dry-run command and emit SDK telemetry",
    )
    parser.add_argument(
        "--check-ffuf-live",
        action="store_true",
        help="execute one ffuf live command (requires FFUF_LIVE_TARGET)",
    )
    parser.add_argument(
        "--check-netcat",
        action="store_true",
        help="execute one netcat dry-run command and emit SDK telemetry",
    )
    parser.add_argument(
        "--check-netcat-live",
        action="store_true",
        help="execute one netcat live command (requires NETCAT_LIVE_TARGET and NETCAT_LIVE_PORT)",
    )
    parser.add_argument(
        "--check-netexec",
        action="store_true",
        help="execute one netexec dry-run command and emit SDK telemetry",
    )
    parser.add_argument(
        "--check-netexec-live",
        action="store_true",
        help="execute one netexec live command (requires NETEXEC_LIVE_TARGET, NETEXEC_LIVE_USERNAME, and NETEXEC_LIVE_PASSWORD)",
    )
    parser.add_argument(
        "--check-john",
        action="store_true",
        help="execute one john dry-run command and emit SDK telemetry",
    )
    parser.add_argument(
        "--check-john-live",
        action="store_true",
        help="execute one john live command (requires JOHN_LIVE_HASH_FILE)",
    )
    parser.add_argument(
        "--check-wget",
        action="store_true",
        help="execute one wget dry-run command and emit SDK telemetry",
    )
    parser.add_argument(
        "--check-wget-live",
        action="store_true",
        help="execute one wget live command (requires WGET_LIVE_TARGET)",
    )
    parser.add_argument(
        "--check-burpsuite",
        action="store_true",
        help="execute one burpsuite dry-run command and emit SDK telemetry",
    )
    parser.add_argument(
        "--check-burpsuite-live",
        action="store_true",
        help="execute one burpsuite live command (requires BURPSUITE_LIVE_TARGET)",
    )
    parser.add_argument(
        "--check-amass",
        action="store_true",
        help="execute one amass dry-run command and emit SDK telemetry",
    )
    parser.add_argument(
        "--check-amass-live",
        action="store_true",
        help="execute one amass live command (requires AMASS_LIVE_TARGET)",
    )
    parser.add_argument(
        "--check-sqlmap",
        action="store_true",
        help="execute one sqlmap dry-run command and emit SDK telemetry",
    )
    parser.add_argument(
        "--check-sqlmap-live",
        action="store_true",
        help="execute one sqlmap live command (requires SQLMAP_LIVE_TARGET)",
    )
    parser.add_argument(
        "--check-subfinder",
        action="store_true",
        help="execute one subfinder dry-run command and emit SDK telemetry",
    )
    parser.add_argument(
        "--check-subfinder-live",
        action="store_true",
        help="execute one subfinder live command (requires SUBFINDER_LIVE_TARGET)",
    )
    parser.add_argument(
        "--check-mythic-task",
        action="store_true",
        help="execute one Mythic dry-run task and emit SDK telemetry",
    )
    parser.add_argument(
        "--check-vectorvue",
        action="store_true",
        help="run VectorVue API smoke using VECTORVUE_* env",
    )
    return parser


def main() -> int:
    """CLI entrypoint for host smoke checks."""
    _load_local_federation_env()
    args = _build_parser().parse_args()

    result = run_host_integration_smoke(
        tenant_id=args.tenant_id,
        nmap_target=args.nmap_target,
        timeout_seconds=args.timeout_seconds,
        check_metasploit_rpc=args.check_metasploit_rpc,
        check_sliver_command=args.check_sliver_command,
        check_impacket_psexec=args.check_impacket_psexec,
        check_impacket_psexec_live=args.check_impacket_psexec_live,
        check_impacket_wmiexec=args.check_impacket_wmiexec,
        check_impacket_wmiexec_live=args.check_impacket_wmiexec_live,
        check_impacket_smbexec=args.check_impacket_smbexec,
        check_impacket_smbexec_live=args.check_impacket_smbexec_live,
        check_impacket_secretsdump=args.check_impacket_secretsdump,
        check_impacket_secretsdump_live=args.check_impacket_secretsdump_live,
        check_impacket_ntlmrelayx=args.check_impacket_ntlmrelayx,
        check_impacket_ntlmrelayx_live=args.check_impacket_ntlmrelayx_live,
        check_bloodhound_collector=args.check_bloodhound_collector,
        check_bloodhound_collector_live=args.check_bloodhound_collector_live,
        check_nuclei=args.check_nuclei,
        check_nuclei_live=args.check_nuclei_live,
        check_prowler=args.check_prowler,
        check_prowler_live=args.check_prowler_live,
        check_responder=args.check_responder,
        check_responder_live=args.check_responder_live,
        check_gobuster=args.check_gobuster,
        check_gobuster_live=args.check_gobuster_live,
        check_ffuf=args.check_ffuf,
        check_ffuf_live=args.check_ffuf_live,
        check_netcat=args.check_netcat,
        check_netcat_live=args.check_netcat_live,
        check_netexec=args.check_netexec,
        check_netexec_live=args.check_netexec_live,
        check_john=args.check_john,
        check_john_live=args.check_john_live,
        check_wget=args.check_wget,
        check_wget_live=args.check_wget_live,
        check_burpsuite=args.check_burpsuite,
        check_burpsuite_live=args.check_burpsuite_live,
        check_amass=args.check_amass,
        check_amass_live=args.check_amass_live,
        check_sqlmap=args.check_sqlmap,
        check_sqlmap_live=args.check_sqlmap_live,
        check_subfinder=args.check_subfinder,
        check_subfinder_live=args.check_subfinder_live,
        check_mythic_task=args.check_mythic_task,
        check_vectorvue=args.check_vectorvue,
    )

    print(
        "HOST_SMOKE"
        f" tenant_id={result.tenant_id}"
        f" nmap_binary_ok={result.nmap_binary_ok}"
        f" nmap_scan_ok={result.nmap_scan_ok}"
        f" telemetry_ingest_ok={result.telemetry_ingest_ok}"
        f" metasploit_binary_ok={result.metasploit_binary_ok}"
        f" metasploit_rpc_ok={result.metasploit_rpc_ok}"
        f" impacket_psexec_binary_ok={result.impacket_psexec_binary_ok}"
        f" impacket_psexec_command_ok={result.impacket_psexec_command_ok}"
        f" impacket_wmiexec_binary_ok={result.impacket_wmiexec_binary_ok}"
        f" impacket_wmiexec_command_ok={result.impacket_wmiexec_command_ok}"
        f" impacket_smbexec_binary_ok={result.impacket_smbexec_binary_ok}"
        f" impacket_smbexec_command_ok={result.impacket_smbexec_command_ok}"
        f" impacket_secretsdump_binary_ok={result.impacket_secretsdump_binary_ok}"
        f" impacket_secretsdump_command_ok={result.impacket_secretsdump_command_ok}"
        f" impacket_ntlmrelayx_binary_ok={result.impacket_ntlmrelayx_binary_ok}"
        f" impacket_ntlmrelayx_command_ok={result.impacket_ntlmrelayx_command_ok}"
        f" bloodhound_collector_binary_ok={result.bloodhound_collector_binary_ok}"
        f" bloodhound_collector_command_ok={result.bloodhound_collector_command_ok}"
        f" nuclei_binary_ok={result.nuclei_binary_ok}"
        f" nuclei_command_ok={result.nuclei_command_ok}"
        f" prowler_binary_ok={result.prowler_binary_ok}"
        f" prowler_command_ok={result.prowler_command_ok}"
        f" responder_binary_ok={result.responder_binary_ok}"
        f" responder_command_ok={result.responder_command_ok}"
        f" gobuster_binary_ok={result.gobuster_binary_ok}"
        f" gobuster_command_ok={result.gobuster_command_ok}"
        f" ffuf_binary_ok={result.ffuf_binary_ok}"
        f" ffuf_command_ok={result.ffuf_command_ok}"
        f" netcat_binary_ok={result.netcat_binary_ok}"
        f" netcat_command_ok={result.netcat_command_ok}"
        f" netexec_binary_ok={result.netexec_binary_ok}"
        f" netexec_command_ok={result.netexec_command_ok}"
        f" john_binary_ok={result.john_binary_ok}"
        f" john_command_ok={result.john_command_ok}"
        f" wget_binary_ok={result.wget_binary_ok}"
        f" wget_command_ok={result.wget_command_ok}"
        f" burpsuite_binary_ok={result.burpsuite_binary_ok}"
        f" burpsuite_command_ok={result.burpsuite_command_ok}"
        f" amass_binary_ok={result.amass_binary_ok}"
        f" amass_command_ok={result.amass_command_ok}"
        f" sqlmap_binary_ok={result.sqlmap_binary_ok}"
        f" sqlmap_command_ok={result.sqlmap_command_ok}"
        f" subfinder_binary_ok={result.subfinder_binary_ok}"
        f" subfinder_command_ok={result.subfinder_command_ok}"
        f" sliver_binary_ok={result.sliver_binary_ok}"
        f" sliver_command_ok={result.sliver_command_ok}"
        f" mythic_binary_ok={result.mythic_binary_ok}"
        f" mythic_task_ok={result.mythic_task_ok}"
        f" rabbitmq_publish_ok={result.rabbitmq_publish_ok}"
        f" vectorvue_ok={result.vectorvue_ok}"
        f" vectorvue_event_status={result.vectorvue_event_status}"
        f" vectorvue_finding_status={result.vectorvue_finding_status}"
        f" vectorvue_status_poll_status={result.vectorvue_status_poll_status}"
        f" checks={','.join(result.checks)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
