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

"""VectorVue integration client exports."""

from pkg.integration.vectorvue.client import VectorVueClient
from pkg.integration.vectorvue.config import VectorVueConfig
from pkg.integration.vectorvue.exceptions import (
    VectorVueAPIError,
    VectorVueConfigError,
    VectorVueError,
    VectorVueSerializationError,
    VectorVueTransportError,
)
from pkg.integration.vectorvue.models import ResponseEnvelope

__all__ = [
    "ResponseEnvelope",
    "VectorVueAPIError",
    "VectorVueClient",
    "VectorVueConfig",
    "VectorVueConfigError",
    "VectorVueError",
    "VectorVueSerializationError",
    "VectorVueTransportError",
]
