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

"""Unit tests for BYOT telemetry SDK helpers."""

from __future__ import annotations

from pkg.telemetry.sdk import (
    build_cloudevent_telemetry,
    build_internal_telemetry_event,
    build_legacy_telemetry_event,
)


def test_build_internal_telemetry_event() -> None:
    payload = build_internal_telemetry_event(
        event_type="tool.scan",
        actor="scanner-bot",
        target="urn:target:ip:10.0.0.5",
        status="success",
        tenant_id="tenant-a",
        attributes={"ports": [22, 443]},
    )

    assert payload["event_type"] == "tool.scan"
    assert payload["actor"] == "scanner-bot"
    assert payload["tenant_id"] == "tenant-a"
    assert payload["attributes"]["ports"] == [22, 443]


def test_build_cloudevent_telemetry() -> None:
    payload = build_cloudevent_telemetry(
        event_type="com.nyxera.tool.scan.v1",
        source="urn:tool:scanner",
        subject="task-1",
        tenant_id="tenant-a",
        data={"status": "success"},
        event_id="evt-1",
        timestamp="2026-02-26T00:00:00+00:00",
    )

    assert payload["specversion"] == "1.0"
    assert payload["id"] == "evt-1"
    assert payload["type"] == "com.nyxera.tool.scan.v1"
    assert payload["data"]["status"] == "success"
    assert payload["data"]["tenant_id"] == "tenant-a"


def test_build_legacy_telemetry_event() -> None:
    payload = build_legacy_telemetry_event(
        event_type="legacy.scan",
        status="failed",
        actor="legacy-bot",
        target="legacy-target",
        tenant_id="tenant-a",
        attributes={"error": "boom"},
    )

    assert payload["event"]["type"] == "legacy.scan"
    assert payload["result"]["status"] == "failed"
    assert payload["context"]["actor"] == "legacy-bot"
    assert payload["context"]["tenant_id"] == "tenant-a"
