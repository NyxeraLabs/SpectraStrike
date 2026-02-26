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

"""Unit tests for unified telemetry schema parser."""

from __future__ import annotations

import pytest

from pkg.orchestrator.telemetry_schema import TelemetrySchemaError, TelemetrySchemaParser


def test_parse_cloudevent_payload() -> None:
    parser = TelemetrySchemaParser()
    parsed = parser.parse(
        {
            "specversion": "1.0",
            "type": "com.nyxeralabs.runner.execution.v1",
            "source": "urn:spectrastrike:runner",
            "subject": "task-1",
            "data": {
                "operator_id": "alice",
                "tenant_id": "tenant-a",
                "target_urn": "urn:target:ip:10.0.0.5",
                "status": "success",
                "exit_code": 0,
            },
        }
    )

    assert parsed.event_type == "com.nyxeralabs.runner.execution.v1"
    assert parsed.actor == "alice"
    assert parsed.target == "urn:target:ip:10.0.0.5"
    assert parsed.status == "success"
    assert parsed.tenant_id == "tenant-a"
    assert parsed.attributes["exit_code"] == 0


def test_parse_internal_payload() -> None:
    parser = TelemetrySchemaParser()
    parsed = parser.parse(
        {
            "event_type": "task_submitted",
            "actor": "alice",
            "target": "nmap",
            "status": "success",
            "tenant_id": "tenant-a",
            "attributes": {"task_id": "task-1"},
        }
    )

    assert parsed.event_type == "task_submitted"
    assert parsed.tenant_id == "tenant-a"
    assert parsed.attributes["task_id"] == "task-1"


def test_parse_legacy_payload() -> None:
    parser = TelemetrySchemaParser()
    parsed = parser.parse(
        {
            "event": {"type": "legacy_event"},
            "result": {"status": "failed"},
            "context": {
                "actor": "legacy-user",
                "target": "legacy-target",
                "tenant_id": "tenant-a",
            },
            "attributes": {"error": "boom"},
        }
    )

    assert parsed.event_type == "legacy_event"
    assert parsed.actor == "legacy-user"
    assert parsed.target == "legacy-target"
    assert parsed.status == "failed"
    assert parsed.tenant_id == "tenant-a"


def test_parse_invalid_payload_raises() -> None:
    parser = TelemetrySchemaParser()
    with pytest.raises(TelemetrySchemaError):
        parser.parse({"unexpected": "shape"})
