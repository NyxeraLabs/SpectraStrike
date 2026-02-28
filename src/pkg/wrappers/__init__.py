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
from pkg.wrappers.impacket_psexec import (
    ImpacketPsexecError,
    ImpacketPsexecRequest,
    ImpacketPsexecResult,
    ImpacketPsexecWrapper,
)
from pkg.wrappers.impacket_wmiexec import (
    ImpacketWmiexecError,
    ImpacketWmiexecRequest,
    ImpacketWmiexecResult,
    ImpacketWmiexecWrapper,
)
from pkg.wrappers.impacket_smbexec import (
    ImpacketSmbexecError,
    ImpacketSmbexecRequest,
    ImpacketSmbexecResult,
    ImpacketSmbexecWrapper,
)
from pkg.wrappers.impacket_secretsdump import (
    ImpacketSecretsdumpError,
    ImpacketSecretsdumpRequest,
    ImpacketSecretsdumpResult,
    ImpacketSecretsdumpWrapper,
)
from pkg.wrappers.impacket_ntlmrelayx import (
    ImpacketNtlmrelayxError,
    ImpacketNtlmrelayxRequest,
    ImpacketNtlmrelayxResult,
    ImpacketNtlmrelayxWrapper,
)
from pkg.wrappers.bloodhound_collector import (
    BloodhoundCollectorError,
    BloodhoundCollectorRequest,
    BloodhoundCollectorResult,
    BloodhoundCollectorWrapper,
)
from pkg.wrappers.nuclei import (
    NucleiExecutionError,
    NucleiScanRequest,
    NucleiScanResult,
    NucleiWrapper,
)
from pkg.wrappers.prowler import (
    ProwlerExecutionError,
    ProwlerScanRequest,
    ProwlerScanResult,
    ProwlerWrapper,
)
from pkg.wrappers.responder import (
    ResponderExecutionError,
    ResponderRequest,
    ResponderResult,
    ResponderWrapper,
)
from pkg.wrappers.gobuster import (
    GobusterExecutionError,
    GobusterScanRequest,
    GobusterScanResult,
    GobusterWrapper,
)
from pkg.wrappers.ffuf import (
    FfufExecutionError,
    FfufScanRequest,
    FfufScanResult,
    FfufWrapper,
)
from pkg.wrappers.netcat import (
    NetcatExecutionError,
    NetcatRequest,
    NetcatResult,
    NetcatWrapper,
)
from pkg.wrappers.netexec import (
    NetExecExecutionError,
    NetExecRequest,
    NetExecResult,
    NetExecWrapper,
)
from pkg.wrappers.john import (
    JohnExecutionError,
    JohnRequest,
    JohnResult,
    JohnWrapper,
)
from pkg.wrappers.wget import (
    WgetExecutionError,
    WgetRequest,
    WgetResult,
    WgetWrapper,
)
from pkg.wrappers.burpsuite import (
    BurpSuiteExecutionError,
    BurpSuiteRequest,
    BurpSuiteResult,
    BurpSuiteWrapper,
)
from pkg.wrappers.amass import (
    AmassExecutionError,
    AmassRequest,
    AmassResult,
    AmassWrapper,
)
from pkg.wrappers.sqlmap import (
    SqlmapExecutionError,
    SqlmapRequest,
    SqlmapResult,
    SqlmapWrapper,
)
from pkg.wrappers.subfinder import (
    SubfinderExecutionError,
    SubfinderRequest,
    SubfinderResult,
    SubfinderWrapper,
)
from pkg.wrappers.mythic import (
    MythicExecutionError,
    MythicTaskRequest,
    MythicTaskResult,
    MythicWrapper,
)
from pkg.wrappers.nmap import (
    NmapExecutionError,
    NmapScanHost,
    NmapScanOptions,
    NmapScanResult,
    NmapWrapper,
)
from pkg.wrappers.sliver import (
    SliverCommandRequest,
    SliverCommandResult,
    SliverExecutionError,
    SliverWrapper,
)

__all__ = [
    "ExploitRequest",
    "MetasploitConfig",
    "MetasploitExploitResult",
    "MetasploitRPCError",
    "MetasploitTransportError",
    "MetasploitWrapper",
    "ImpacketPsexecError",
    "ImpacketPsexecRequest",
    "ImpacketPsexecResult",
    "ImpacketPsexecWrapper",
    "ImpacketWmiexecError",
    "ImpacketWmiexecRequest",
    "ImpacketWmiexecResult",
    "ImpacketWmiexecWrapper",
    "ImpacketSmbexecError",
    "ImpacketSmbexecRequest",
    "ImpacketSmbexecResult",
    "ImpacketSmbexecWrapper",
    "ImpacketSecretsdumpError",
    "ImpacketSecretsdumpRequest",
    "ImpacketSecretsdumpResult",
    "ImpacketSecretsdumpWrapper",
    "ImpacketNtlmrelayxError",
    "ImpacketNtlmrelayxRequest",
    "ImpacketNtlmrelayxResult",
    "ImpacketNtlmrelayxWrapper",
    "BloodhoundCollectorError",
    "BloodhoundCollectorRequest",
    "BloodhoundCollectorResult",
    "BloodhoundCollectorWrapper",
    "NucleiExecutionError",
    "NucleiScanRequest",
    "NucleiScanResult",
    "NucleiWrapper",
    "ProwlerExecutionError",
    "ProwlerScanRequest",
    "ProwlerScanResult",
    "ProwlerWrapper",
    "ResponderExecutionError",
    "ResponderRequest",
    "ResponderResult",
    "ResponderWrapper",
    "GobusterExecutionError",
    "GobusterScanRequest",
    "GobusterScanResult",
    "GobusterWrapper",
    "FfufExecutionError",
    "FfufScanRequest",
    "FfufScanResult",
    "FfufWrapper",
    "NetcatExecutionError",
    "NetcatRequest",
    "NetcatResult",
    "NetcatWrapper",
    "NetExecExecutionError",
    "NetExecRequest",
    "NetExecResult",
    "NetExecWrapper",
    "JohnExecutionError",
    "JohnRequest",
    "JohnResult",
    "JohnWrapper",
    "WgetExecutionError",
    "WgetRequest",
    "WgetResult",
    "WgetWrapper",
    "BurpSuiteExecutionError",
    "BurpSuiteRequest",
    "BurpSuiteResult",
    "BurpSuiteWrapper",
    "AmassExecutionError",
    "AmassRequest",
    "AmassResult",
    "AmassWrapper",
    "SqlmapExecutionError",
    "SqlmapRequest",
    "SqlmapResult",
    "SqlmapWrapper",
    "SubfinderExecutionError",
    "SubfinderRequest",
    "SubfinderResult",
    "SubfinderWrapper",
    "MythicExecutionError",
    "MythicTaskRequest",
    "MythicTaskResult",
    "MythicWrapper",
    "NmapExecutionError",
    "NmapScanHost",
    "NmapScanOptions",
    "NmapScanResult",
    "NmapWrapper",
    "SessionTranscript",
    "SliverCommandRequest",
    "SliverCommandResult",
    "SliverExecutionError",
    "SliverWrapper",
]
