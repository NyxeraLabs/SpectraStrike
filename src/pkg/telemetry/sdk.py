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

"""BYOT telemetry SDK helpers for Python tool developers."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


def build_internal_telemetry_event(
    *,
    event_type: str,
    actor: str,
    target: str,
    status: str,
    tenant_id: str,
    attributes: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build orchestrator-native telemetry payload."""
    return {
        "event_type": event_type,
        "actor": actor,
        "target": target,
        "status": status,
        "tenant_id": tenant_id,
        "attributes": dict(attributes or {}),
    }


def build_cloudevent_telemetry(
    *,
    event_type: str,
    source: str,
    subject: str,
    tenant_id: str,
    data: dict[str, Any],
    event_id: str | None = None,
    timestamp: str | None = None,
) -> dict[str, Any]:
    """Build CloudEvents v1.0 telemetry payload."""
    event_data = dict(data)
    event_data["tenant_id"] = tenant_id
    return {
        "id": event_id or str(uuid4()),
        "specversion": "1.0",
        "type": event_type,
        "source": source,
        "subject": subject,
        "time": timestamp or datetime.now(UTC).isoformat(),
        "data": event_data,
    }


def build_legacy_telemetry_event(
    *,
    event_type: str,
    status: str,
    actor: str,
    target: str,
    tenant_id: str,
    attributes: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build compatibility payload for legacy telemetry producers."""
    return {
        "event": {"type": event_type},
        "result": {"status": status},
        "context": {"actor": actor, "target": target, "tenant_id": tenant_id},
        "attributes": dict(attributes or {}),
    }
