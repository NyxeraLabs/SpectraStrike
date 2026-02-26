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

"""Unified telemetry schema parser for incoming orchestrator payloads."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class TelemetrySchemaError(ValueError):
    """Raised when incoming telemetry payload does not match supported schemas."""


@dataclass(slots=True, frozen=True)
class ParsedTelemetryEvent:
    """Canonical parsed telemetry fields before pipeline ingestion."""

    event_type: str
    actor: str
    target: str
    status: str
    attributes: dict[str, Any] = field(default_factory=dict)


class TelemetrySchemaParser:
    """Parser supporting CloudEvents and internal telemetry payload contracts."""

    def parse(self, payload: dict[str, Any]) -> ParsedTelemetryEvent:
        """Parse one payload into canonical telemetry fields."""
        if not isinstance(payload, dict):
            raise TelemetrySchemaError("payload must be a dictionary")

        if self._is_cloudevent(payload):
            return self._parse_cloudevent(payload)
        if self._is_internal_event(payload):
            return self._parse_internal(payload)
        if self._is_legacy_event(payload):
            return self._parse_legacy(payload)

        raise TelemetrySchemaError("unsupported telemetry schema")

    @staticmethod
    def _is_cloudevent(payload: dict[str, Any]) -> bool:
        return payload.get("specversion") == "1.0" and "type" in payload and "data" in payload

    @staticmethod
    def _is_internal_event(payload: dict[str, Any]) -> bool:
        required = {"event_type", "actor", "target", "status"}
        return required.issubset(payload.keys())

    @staticmethod
    def _is_legacy_event(payload: dict[str, Any]) -> bool:
        return isinstance(payload.get("event"), dict) and isinstance(
            payload.get("result"), dict
        )

    def _parse_cloudevent(self, payload: dict[str, Any]) -> ParsedTelemetryEvent:
        data = payload.get("data")
        if not isinstance(data, dict):
            raise TelemetrySchemaError("CloudEvent data must be an object")

        event_type = self._require_string(payload.get("type"), "CloudEvent type")
        actor = self._first_non_empty(
            data.get("actor"),
            data.get("operator_id"),
            "unknown",
        )
        target = self._first_non_empty(
            data.get("target_urn"),
            data.get("target"),
            str(payload.get("subject", "unknown")),
        )
        status = self._first_non_empty(data.get("status"), "unknown")
        attributes = dict(data)
        attributes["cloudevent_source"] = str(payload.get("source", ""))
        attributes["cloudevent_subject"] = str(payload.get("subject", ""))
        return ParsedTelemetryEvent(
            event_type=event_type,
            actor=actor,
            target=target,
            status=status,
            attributes=attributes,
        )

    def _parse_internal(self, payload: dict[str, Any]) -> ParsedTelemetryEvent:
        event_type = self._require_string(payload.get("event_type"), "event_type")
        actor = self._require_string(payload.get("actor"), "actor")
        target = self._require_string(payload.get("target"), "target")
        status = self._require_string(payload.get("status"), "status")
        attributes = payload.get("attributes", {})
        if not isinstance(attributes, dict):
            raise TelemetrySchemaError("attributes must be an object")
        return ParsedTelemetryEvent(
            event_type=event_type,
            actor=actor,
            target=target,
            status=status,
            attributes=dict(attributes),
        )

    def _parse_legacy(self, payload: dict[str, Any]) -> ParsedTelemetryEvent:
        event = payload["event"]
        result = payload["result"]
        context = payload.get("context", {})
        attrs = payload.get("attributes", {})
        if not isinstance(event, dict) or not isinstance(result, dict):
            raise TelemetrySchemaError("legacy payload event/result must be objects")
        if not isinstance(context, dict) or not isinstance(attrs, dict):
            raise TelemetrySchemaError("legacy payload context/attributes must be objects")

        event_type = self._require_string(event.get("type"), "legacy event.type")
        actor = self._first_non_empty(context.get("actor"), "unknown")
        target = self._first_non_empty(context.get("target"), "unknown")
        status = self._require_string(result.get("status"), "legacy result.status")
        return ParsedTelemetryEvent(
            event_type=event_type,
            actor=actor,
            target=target,
            status=status,
            attributes=dict(attrs),
        )

    @staticmethod
    def _require_string(value: Any, label: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise TelemetrySchemaError(f"{label} must be a non-empty string")
        return value

    @staticmethod
    def _first_non_empty(*values: Any) -> str:
        for value in values:
            if isinstance(value, str) and value.strip():
                return value
        return "unknown"
