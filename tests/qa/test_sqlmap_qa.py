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

"""QA smoke tests for sqlmap wrapper contract behavior."""

from __future__ import annotations

from pkg.orchestrator.telemetry_ingestion import TelemetryIngestionPipeline
from pkg.wrappers.sqlmap import SqlmapRequest, SqlmapWrapper


def test_qa_sqlmap_dry_run_smoke() -> None:
    wrapper = SqlmapWrapper(
        signer=lambda _payload: "qa-ed25519-signature",
        runner=lambda _cmd, _timeout: type(
            "R", (), {"returncode": 0, "stdout": "1.8.2#stable", "stderr": ""}
        )(),  # type: ignore[arg-type]
    )
    telemetry = TelemetryIngestionPipeline(batch_size=1)

    result = wrapper.execute(
        SqlmapRequest(
            target="http://127.0.0.1/vuln.php?id=1",
            command="-u http://127.0.0.1/vuln.php?id=1 --batch --risk=1 --level=1",
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
    assert event.event_type == "sqlmap_scan_completed"
    assert event.attributes["adapter"] == "sqlmap"
    assert event.attributes["execution_fingerprint"] == result.execution_fingerprint
    assert len(flushed) == 1
