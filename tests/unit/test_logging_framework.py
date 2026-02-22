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

"""Unit tests for the SpectraStrike logging framework."""

from __future__ import annotations

import json
import logging

from pkg.logging.framework import (
    emit_audit_event,
    get_audit_logger,
    get_logger,
    setup_logging,
)


def test_setup_logging_adds_handler() -> None:
    root_logger = logging.getLogger()
    previous_handlers = list(root_logger.handlers)
    previous_level = root_logger.level

    try:
        root_logger.handlers = []
        setup_logging(logging.DEBUG)

        assert root_logger.handlers
        assert root_logger.level == logging.DEBUG
    finally:
        root_logger.handlers = previous_handlers
        root_logger.setLevel(previous_level)


def test_get_logger_returns_named_logger() -> None:
    logger = get_logger("spectrastrike.test")
    assert logger.name == "spectrastrike.test"


def test_emit_audit_event_logs_json(caplog) -> None:  # type: ignore[no-untyped-def]
    setup_logging()
    audit_logger = get_audit_logger()

    with caplog.at_level(logging.INFO, logger=audit_logger.name):
        emit_audit_event(
            action="login_attempt",
            actor="tester",
            target="orchestrator",
            status="success",
            source_ip="127.0.0.1",
        )

    assert caplog.records
    payload = json.loads(caplog.records[-1].message)
    assert payload["action"] == "login_attempt"
    assert payload["actor"] == "tester"
    assert payload["status"] == "success"
    assert payload["metadata"]["source_ip"] == "127.0.0.1"
