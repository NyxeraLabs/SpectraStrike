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

"""Security package for AAA checks and framework."""

from .aaa_framework import (
    AAAError,
    AAAService,
    AccountingRecord,
    AuthenticationError,
    AuthorizationError,
    Principal,
)

__all__ = [
    "AAAError",
    "AuthenticationError",
    "AuthorizationError",
    "Principal",
    "AccountingRecord",
    "AAAService",
]
