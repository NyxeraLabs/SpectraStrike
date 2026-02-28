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

"""QA smoke tests for Impacket smbexec wrapper contract behavior."""

from __future__ import annotations

from pkg.orchestrator.telemetry_ingestion import TelemetryIngestionPipeline
from pkg.wrappers.impacket_smbexec import ImpacketSmbexecRequest, ImpacketSmbexecWrapper


def test_qa_impacket_smbexec_dry_run_smoke() -> None:
    wrapper = ImpacketSmbexecWrapper(
        signer=lambda _payload: "qa-ed25519-signature",
        runner=lambda _cmd, _timeout: type(
            "R", (), {"returncode": 0, "stdout": "Impacket v0.13.0", "stderr": ""}
        )(),  # type: ignore[arg-type]
    )
    telemetry = TelemetryIngestionPipeline(batch_size=1)

    result = wrapper.execute(
        ImpacketSmbexecRequest(
            target="10.20.30.42",
            username="administrator",
            no_pass=True,
            command="whoami",
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
    assert event.event_type == "impacket_smbexec_completed"
    assert event.attributes["adapter"] == "impacket"
    assert event.attributes["module"] == "smbexec.py"
    assert event.attributes["execution_fingerprint"] == result.execution_fingerprint
    assert event.attributes["attestation_measurement_hash"] == (
        result.attestation_measurement_hash
    )
    assert len(flushed) == 1
