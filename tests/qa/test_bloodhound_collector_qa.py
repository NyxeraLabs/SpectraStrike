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

"""QA smoke tests for BloodHound collector wrapper contract behavior."""

from __future__ import annotations

from pkg.orchestrator.telemetry_ingestion import TelemetryIngestionPipeline
from pkg.wrappers.bloodhound_collector import (
    BloodhoundCollectorRequest,
    BloodhoundCollectorWrapper,
)


def test_qa_bloodhound_collector_dry_run_smoke() -> None:
    wrapper = BloodhoundCollectorWrapper(
        signer=lambda _payload: "qa-ed25519-signature",
        runner=lambda _cmd, _timeout: type(
            "R", (), {"returncode": 0, "stdout": "bloodhound-python 1.8.0", "stderr": ""}
        )(),  # type: ignore[arg-type]
    )
    telemetry = TelemetryIngestionPipeline(batch_size=1)

    result = wrapper.execute(
        BloodhoundCollectorRequest(
            target="10.20.30.45",
            username="administrator",
            no_pass=True,
            command="-c All",
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
    assert event.event_type == "bloodhound_collector_completed"
    assert event.attributes["adapter"] == "bloodhound"
    assert event.attributes["module"] == "collector"
    assert event.attributes["execution_fingerprint"] == result.execution_fingerprint
    assert len(flushed) == 1
