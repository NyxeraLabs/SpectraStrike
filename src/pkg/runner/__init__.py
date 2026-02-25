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

"""Universal Edge Runner and execution-contract primitives."""

from .cloudevents import CloudEventEnvelope, map_execution_to_cloudevent
from .jws_verify import JWSVerificationError, RunnerJWSVerifier
from .universal import (
    RunnerExecutionError,
    RunnerExecutionResult,
    RunnerSandboxProfile,
    UniversalEdgeRunner,
)

__all__ = [
    "JWSVerificationError",
    "RunnerJWSVerifier",
    "CloudEventEnvelope",
    "map_execution_to_cloudevent",
    "RunnerSandboxProfile",
    "RunnerExecutionError",
    "RunnerExecutionResult",
    "UniversalEdgeRunner",
]
