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

"""QA smoke tests for dnsx wrapper contract behavior."""

from __future__ import annotations

from pkg.orchestrator.telemetry_ingestion import TelemetryIngestionPipeline
from pkg.wrappers.dnsx import DnsxRequest, DnsxWrapper


def test_qa_dnsx_dry_run_smoke() -> None:
    wrapper = DnsxWrapper(
        signer=lambda _payload: "qa-ed25519-signature",
        runner=lambda _cmd, _timeout: type(
            "R", (), {"returncode": 0, "stdout": "Current Version: 1.2.3", "stderr": ""}
        )(),  # type: ignore[arg-type]
    )
    telemetry = TelemetryIngestionPipeline(batch_size=1)

    result = wrapper.execute(
        DnsxRequest(
            target="example.com",
            command="-silent -d example.com",
            extra_args=["--dry-run"],
            policy_decision_hash="qa-policy-allow",
        ),
        tenant_id="tenant-a",
        operator_id="qa-operator",
    )
    event = wrapper.send_to_orchestrator(
        result,
        telemetry=telemetry,
        tenant_id="tenant-a",
        operator_id="qa-operator",
        actor="qa-bot",
    )
    flushed = telemetry.flush_ready()

    assert result.status == "success"
    assert result.payload_signature_algorithm == "Ed25519"
    assert event.event_type == "dnsx_scan_completed"
    assert event.attributes["adapter"] == "dnsx"
    assert event.attributes["execution_fingerprint"] == result.execution_fingerprint
    assert len(flushed) == 1
