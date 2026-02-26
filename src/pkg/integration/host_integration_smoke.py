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
from pkg.orchestrator.messaging import InMemoryRabbitBroker, RabbitMQTelemetryPublisher
from pkg.orchestrator.telemetry_ingestion import TelemetryIngestionPipeline
from pkg.wrappers.metasploit import MetasploitConfig, MetasploitWrapper
from pkg.wrappers.nmap import NmapScanOptions, NmapWrapper


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


def _build_vectorvue_config(timeout_seconds: float) -> VectorVueConfig:
    return VectorVueConfig(
        base_url=os.getenv("VECTORVUE_BASE_URL", "https://127.0.0.1"),
        username=os.getenv("VECTORVUE_USERNAME", "acme_viewer"),
        password=os.getenv("VECTORVUE_PASSWORD", "AcmeView3r!"),
        tenant_id=os.getenv(
            "VECTORVUE_TENANT_ID", "10000000-0000-0000-0000-000000000001"
        ),
        timeout_seconds=timeout_seconds,
        verify_tls=os.getenv("VECTORVUE_VERIFY_TLS", "0") == "1",
        signature_secret=os.getenv("VECTORVUE_SIGNATURE_SECRET"),
        mtls_client_cert_file=os.getenv("VECTORVUE_MTLS_CLIENT_CERT_FILE"),
        mtls_client_key_file=os.getenv("VECTORVUE_MTLS_CLIENT_KEY_FILE"),
        max_retries=1,
        backoff_seconds=0,
    )


def run_host_integration_smoke(
    *,
    tenant_id: str,
    nmap_target: str = "127.0.0.1",
    timeout_seconds: float = 8.0,
    check_metasploit_rpc: bool = False,
    check_vectorvue: bool = False,
) -> HostIntegrationResult:
    """Execute host integration smoke path for Sprint 16.8."""
    resolved_tenant = _must_have_tenant(tenant_id)
    result = HostIntegrationResult(tenant_id=resolved_tenant)

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
            additional_args=["-n", "--max-retries", "1", "--host-timeout", "5s"],
        )
    )
    result.nmap_scan_ok = True
    result.checks.append("nmap.scan")

    telemetry = TelemetryIngestionPipeline(batch_size=1)
    event = nmap_wrapper.send_to_orchestrator(
        nmap_scan,
        telemetry=telemetry,
        tenant_id=resolved_tenant,
        actor="host-integration-smoke",
    )
    result.telemetry_ingest_ok = (
        event.event_type == "nmap_scan_completed" and event.tenant_id == resolved_tenant
    )
    result.checks.append("telemetry.ingest")

    _require_binary("msfconsole")
    _run_command(["msfconsole", "--version"], timeout_seconds)
    result.metasploit_binary_ok = True
    result.checks.append("metasploit.version")

    if check_metasploit_rpc:
        wrapper = MetasploitWrapper(config=MetasploitConfig.from_env())
        wrapper.connect()
        result.metasploit_rpc_ok = True
        result.checks.append("metasploit.rpc")

    if check_vectorvue:
        broker = InMemoryRabbitBroker()
        publisher = RabbitMQTelemetryPublisher(broker=broker)
        telemetry_with_broker = TelemetryIngestionPipeline(batch_size=1, publisher=publisher)
        nmap_wrapper.send_to_orchestrator(
            nmap_scan,
            telemetry=telemetry_with_broker,
            tenant_id=resolved_tenant,
            actor="host-integration-smoke",
        )
        publish_result = asyncio.run(telemetry_with_broker.flush_all_async())
        result.rabbitmq_publish_ok = publish_result.published > 0
        result.checks.append("rabbitmq.publish")

        client = VectorVueClient(_build_vectorvue_config(timeout_seconds))
        client.login()
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
        "--check-vectorvue",
        action="store_true",
        help="run VectorVue API smoke using VECTORVUE_* env",
    )
    return parser


def main() -> int:
    """CLI entrypoint for host smoke checks."""
    args = _build_parser().parse_args()

    result = run_host_integration_smoke(
        tenant_id=args.tenant_id,
        nmap_target=args.nmap_target,
        timeout_seconds=args.timeout_seconds,
        check_metasploit_rpc=args.check_metasploit_rpc,
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
