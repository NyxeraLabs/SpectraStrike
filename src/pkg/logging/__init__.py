"""Logging framework package for SpectraStrike."""

from .framework import emit_audit_event, get_audit_logger, get_logger, setup_logging

__all__ = ["setup_logging", "get_logger", "get_audit_logger", "emit_audit_event"]
