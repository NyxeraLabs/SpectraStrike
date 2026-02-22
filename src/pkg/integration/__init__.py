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
