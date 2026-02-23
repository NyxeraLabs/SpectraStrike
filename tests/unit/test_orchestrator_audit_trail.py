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

"""Unit tests for orchestrator logging and audit trail behavior."""

from __future__ import annotations

import json
import logging

from _pytest.logging import LogCaptureFixture

from pkg.logging.framework import setup_logging
from pkg.orchestrator.audit_trail import OrchestratorAuditTrail


def test_task_lifecycle_records_and_audit_logs(
    caplog: LogCaptureFixture,
) -> None:
    setup_logging()
    trail = OrchestratorAuditTrail()

    with caplog.at_level(logging.INFO, logger="spectrastrike.audit"):
        accepted = trail.task_received(
            task_id="task-1",
            actor="alice",
            target="nmap",
            source="api",
        )
        running = trail.task_started(
            task_id="task-1",
            actor="alice",
            target="nmap",
            worker="worker-1",
        )
        success = trail.task_completed(
            task_id="task-1",
            actor="alice",
            target="nmap",
            duration_ms=42,
        )

    assert accepted.status == "accepted"
    assert running.status == "running"
    assert success.status == "success"
    assert len(trail.records) == 3

    payloads = [
        json.loads(record.message)
        for record in caplog.records
        if record.name == "spectrastrike.audit"
    ]
    assert payloads[0]["action"] == "task_received"
    assert payloads[1]["action"] == "task_started"
    assert payloads[2]["action"] == "task_completed"


def test_task_failed_recorded() -> None:
    trail = OrchestratorAuditTrail()
    failed = trail.task_failed(
        task_id="task-9",
        actor="alice",
        target="nmap",
        error="timeout",
    )

    assert failed.status == "failed"
    assert failed.details["error"] == "timeout"
    assert trail.records[-1].action == "task_failed"
