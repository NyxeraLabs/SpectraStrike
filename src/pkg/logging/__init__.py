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

"""Logging framework package for SpectraStrike."""

from .framework import emit_audit_event, get_audit_logger, get_logger, setup_logging

__all__ = ["setup_logging", "get_logger", "get_audit_logger", "emit_audit_event"]
