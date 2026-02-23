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

"""Tool wrappers for external security utilities."""

from pkg.wrappers.metasploit import (
    ExploitRequest,
    MetasploitConfig,
    MetasploitExploitResult,
    MetasploitRPCError,
    MetasploitTransportError,
    MetasploitWrapper,
    SessionTranscript,
)
from pkg.wrappers.nmap import (
    NmapExecutionError,
    NmapScanHost,
    NmapScanOptions,
    NmapScanResult,
    NmapWrapper,
)

__all__ = [
    "ExploitRequest",
    "MetasploitConfig",
    "MetasploitExploitResult",
    "MetasploitRPCError",
    "MetasploitTransportError",
    "MetasploitWrapper",
    "NmapExecutionError",
    "NmapScanHost",
    "NmapScanOptions",
    "NmapScanResult",
    "NmapWrapper",
    "SessionTranscript",
]
