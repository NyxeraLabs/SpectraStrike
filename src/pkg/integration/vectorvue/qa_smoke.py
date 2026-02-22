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

"""Sprint 5 QA smoke checks for VectorVue integration APIs."""

from __future__ import annotations

import argparse
from dataclasses import dataclass

from pkg.integration.vectorvue.client import VectorVueClient
from pkg.integration.vectorvue.config import VectorVueConfig


@dataclass(slots=True)
class SmokeResult:
    """Outcome summary for a QA smoke run."""

    login_ok: bool
    event_status: str
    finding_status: str
    status_poll_status: str


def run_smoke(config: VectorVueConfig) -> SmokeResult:
    """Execute Sprint 5 QA checks against live VectorVue endpoints."""
    client = VectorVueClient(config)
    token = client.login()

    event_envelope = client.send_event(
        {
            "source_system": "spectrastrike-sensor",
            "event_type": "PROCESS_ANOMALY",
            "occurred_at": "2026-02-22T10:00:00Z",
            "severity": "high",
            "asset_ref": "host-nyc-01",
            "message": "Unexpected parent-child process chain",
            "metadata": {
                "pid": 2244,
                "parent_pid": 2210,
                "technique": "T1059",
            },
        }
    )

    finding_envelope = client.send_finding(
        {
            "title": "Suspicious PowerShell Script",
            "description": "Encoded command observed in endpoint telemetry",
            "severity": "critical",
            "status": "open",
            "first_seen": "2026-02-22T09:45:00Z",
            "asset_ref": "host-nyc-01",
            "recommendation": "Block script hash and isolate endpoint",
            "metadata": {"technique": "T1059.001"},
        }
    )

    status_envelope = client.get_ingest_status(event_envelope.request_id or "")

    return SmokeResult(
        login_ok=bool(token),
        event_status=event_envelope.status,
        finding_status=finding_envelope.status,
        status_poll_status=status_envelope.status,
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Sprint 5 VectorVue API QA smoke checks")
    parser.add_argument("--base-url", default="https://127.0.0.1")
    parser.add_argument("--username", default="acme_viewer")
    parser.add_argument("--password", default="AcmeView3r!")
    parser.add_argument("--tenant-id", default="10000000-0000-0000-0000-000000000001")
    parser.add_argument("--timeout-seconds", type=float, default=5.0)
    parser.add_argument("--verify-tls", action="store_true", help="Enable TLS certificate verify")
    return parser


def main() -> int:
    """Run QA smoke checks and print a compact summary."""
    args = _build_parser().parse_args()
    config = VectorVueConfig(
        base_url=args.base_url,
        username=args.username,
        password=args.password,
        tenant_id=args.tenant_id,
        timeout_seconds=args.timeout_seconds,
        verify_tls=args.verify_tls,
        max_retries=1,
        backoff_seconds=0,
    )

    result = run_smoke(config)
    print(
        "QA_SMOKE"
        f" login_ok={result.login_ok}"
        f" event_status={result.event_status}"
        f" finding_status={result.finding_status}"
        f" status_poll={result.status_poll_status}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
