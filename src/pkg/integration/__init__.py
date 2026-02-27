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

"""Integration adapters for external systems."""

from pkg.integration.c2_adapter_hardening import (
    C2AdapterHardeningError,
    C2DispatchBundle,
    HardenedC2AdapterBoundary,
    HardenedExecutionBoundaryConfig,
    simulate_malicious_adapter_payload,
)
from pkg.integration.c2_advanced import (
    C2AdvancedAdapterError,
    C2LiveSessionResult,
    HardenedSliverAdapter,
    MythicAdapterScaffold,
    execute_zero_trust_live_session,
)
from pkg.integration.metasploit_manual import (
    IngestionCheckpoint,
    IngestionCheckpointStore,
    IngestionResult,
    MetasploitManualAPIError,
    MetasploitManualClient,
    MetasploitManualConfig,
    MetasploitManualConfigError,
    MetasploitManualError,
    MetasploitManualIngestor,
    MetasploitManualTransportError,
    MetasploitSession,
    MetasploitSessionEvent,
)

__all__ = [
    "C2AdapterHardeningError",
    "C2DispatchBundle",
    "HardenedC2AdapterBoundary",
    "HardenedExecutionBoundaryConfig",
    "simulate_malicious_adapter_payload",
    "C2AdvancedAdapterError",
    "C2LiveSessionResult",
    "HardenedSliverAdapter",
    "MythicAdapterScaffold",
    "execute_zero_trust_live_session",
    "IngestionCheckpoint",
    "IngestionCheckpointStore",
    "IngestionResult",
    "MetasploitManualAPIError",
    "MetasploitManualClient",
    "MetasploitManualConfig",
    "MetasploitManualConfigError",
    "MetasploitManualError",
    "MetasploitManualIngestor",
    "MetasploitManualTransportError",
    "MetasploitSession",
    "MetasploitSessionEvent",
]
