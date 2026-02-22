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

"""Central logging setup utilities with audit trail support."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from logging import Logger
from typing import Any

_DEFAULT_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
_AUDIT_LOGGER_NAME = "spectrastrike.audit"


def setup_logging(level: int = logging.INFO) -> None:
    """Configure root logging with a consistent formatter and stream handler."""
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    if root_logger.handlers:
        for handler in root_logger.handlers:
            handler.setLevel(level)
            handler.setFormatter(logging.Formatter(_DEFAULT_FORMAT))
        return

    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(_DEFAULT_FORMAT))
    root_logger.addHandler(handler)


def get_logger(name: str) -> Logger:
    """Return an application logger by name."""
    return logging.getLogger(name)


def get_audit_logger() -> Logger:
    """Return the dedicated audit logger."""
    return logging.getLogger(_AUDIT_LOGGER_NAME)


def emit_audit_event(
    action: str, actor: str, target: str, status: str, **metadata: Any
) -> None:
    """Emit a structured audit event for sensitive operations."""
    event = {
        "timestamp": datetime.now(UTC).isoformat(),
        "action": action,
        "actor": actor,
        "target": target,
        "status": status,
        "metadata": metadata,
    }
    get_audit_logger().info(json.dumps(event, sort_keys=True))
