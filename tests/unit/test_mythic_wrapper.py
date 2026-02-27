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

"""Unit tests for Mythic wrapper SDK telemetry path."""

from __future__ import annotations

from pkg.orchestrator.telemetry_ingestion import TelemetryIngestionPipeline
from pkg.wrappers.mythic import MythicExecutionError, MythicTaskRequest, MythicWrapper


def test_execute_parses_json_response() -> None:
    def fake_runner(_command: list[str], _timeout: float):
        class R:
            returncode = 0
            stdout = '{"status":"success","task_id":"my-1","callback_id":"cb-1","output":"ok"}'
            stderr = ""

        return R()

    wrapper = MythicWrapper(runner=fake_runner)
    result = wrapper.execute(
        MythicTaskRequest(target="10.0.0.8", operation="op-a", command="pwd")
    )
    assert result.status == "success"
    assert result.task_id == "my-1"
    assert result.callback_id == "cb-1"
    assert result.output == "ok"


def test_execute_raises_on_non_zero_exit() -> None:
    def fake_runner(_command: list[str], _timeout: float):
        class R:
            returncode = 1
            stdout = ""
            stderr = "mythic failed"

        return R()

    wrapper = MythicWrapper(runner=fake_runner)
    try:
        wrapper.execute(
            MythicTaskRequest(target="10.0.0.8", operation="op-a", command="pwd")
        )
        assert False, "expected MythicExecutionError"
    except MythicExecutionError as exc:
        assert "mythic failed" in str(exc)


def test_send_to_orchestrator_emits_sdk_event() -> None:
    def fake_runner(_command: list[str], _timeout: float):
        class R:
            returncode = 0
            stdout = "plain-output"
            stderr = ""

        return R()

    wrapper = MythicWrapper(runner=fake_runner)
    result = wrapper.execute(
        MythicTaskRequest(target="10.0.0.8", operation="op-a", command="pwd")
    )
    telemetry = TelemetryIngestionPipeline(batch_size=1)
    event = wrapper.send_to_orchestrator(
        result,
        telemetry=telemetry,
        tenant_id="tenant-a",
    )
    assert event.event_type == "mythic_task_completed"
    assert event.tenant_id == "tenant-a"
