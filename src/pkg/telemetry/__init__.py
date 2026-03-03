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

"""Telemetry package for health checks and BYOT telemetry SDK helpers."""

from .sdk import (
    build_cloudevent_telemetry,
    build_internal_telemetry_event,
    build_legacy_telemetry_event,
)
from .sensor_core import (
    RemoteSensorConfigService,
    SensorCoreAgent,
    SensorCoreError,
    SensorHealthMonitor,
    SensorHealthSnapshot,
    SensorRuntimeConfig,
    SensorTransportConfig,
    SignedTelemetryBatch,
    TelemetryRecord,
)

__all__ = [
    "build_internal_telemetry_event",
    "build_cloudevent_telemetry",
    "build_legacy_telemetry_event",
    "SensorCoreError",
    "SensorTransportConfig",
    "SensorRuntimeConfig",
    "TelemetryRecord",
    "SignedTelemetryBatch",
    "SensorHealthSnapshot",
    "SensorHealthMonitor",
    "RemoteSensorConfigService",
    "SensorCoreAgent",
]
