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

import hashlib
import json
import logging
from datetime import UTC, datetime
from logging import Logger
from threading import Lock
from typing import Any

_DEFAULT_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
_AUDIT_LOGGER_NAME = "spectrastrike.audit"
_AUDIT_CHAIN_LOCK = Lock()
_AUDIT_PREV_HASH = "GENESIS"


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
    global _AUDIT_PREV_HASH

    base_event = {
        "timestamp": datetime.now(UTC).isoformat(),
        "action": action,
        "actor": actor,
        "target": target,
        "status": status,
        "metadata": metadata,
    }
    with _AUDIT_CHAIN_LOCK:
        prev_hash = _AUDIT_PREV_HASH
        canonical = json.dumps(base_event, sort_keys=True, separators=(",", ":"))
        current_hash = hashlib.sha256(
            f"{prev_hash}:{canonical}".encode("utf-8")
        ).hexdigest()
        _AUDIT_PREV_HASH = current_hash

    event = dict(base_event)
    event["prev_hash"] = prev_hash
    event["event_hash"] = current_hash
    get_audit_logger().info(json.dumps(event, sort_keys=True))
