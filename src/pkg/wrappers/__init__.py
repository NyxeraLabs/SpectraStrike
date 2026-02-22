"""Tool wrappers for external security utilities."""

from pkg.wrappers.nmap import (
    NmapExecutionError,
    NmapScanHost,
    NmapScanOptions,
    NmapScanResult,
    NmapWrapper,
)
from pkg.wrappers.metasploit import (
    ExploitRequest,
    MetasploitConfig,
    MetasploitExploitResult,
    MetasploitRPCError,
    MetasploitTransportError,
    MetasploitWrapper,
    SessionTranscript,
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
