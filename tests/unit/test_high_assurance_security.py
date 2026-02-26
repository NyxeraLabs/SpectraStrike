# Copyright (c) 2026 NyxeraLabs
# Author: Jose Maria Micoli
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

"""Unit tests for Sprint 20 high-assurance security controls."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from pkg.security.high_assurance import (
    BreakGlassError,
    PrivilegeElevationError,
    PrivilegeElevationService,
    PrivilegedSessionError,
    PrivilegedSessionRecorder,
)


def test_time_bound_privilege_elevation_token_consumes_once() -> None:
    service = PrivilegeElevationService(ttl_seconds=300)
    now = datetime(2026, 2, 26, 12, 0, tzinfo=UTC)
    token = service.issue_token(
        principal_id="alice",
        role="admin",
        justification="approve urgent manifest",
        now=now,
    )

    service.consume_token(
        token_id=token.token_id,
        principal_id="alice",
        role="admin",
        now=now + timedelta(seconds=10),
    )
    with pytest.raises(PrivilegeElevationError, match="already consumed"):
        service.consume_token(
            token_id=token.token_id,
            principal_id="alice",
            role="admin",
            now=now + timedelta(seconds=20),
        )


def test_time_bound_privilege_elevation_token_expires() -> None:
    service = PrivilegeElevationService(ttl_seconds=60)
    now = datetime(2026, 2, 26, 12, 0, tzinfo=UTC)
    token = service.issue_token(
        principal_id="alice",
        role="admin",
        justification="maintenance",
        now=now,
    )

    with pytest.raises(PrivilegeElevationError, match="expired"):
        service.consume_token(
            token_id=token.token_id,
            principal_id="alice",
            role="admin",
            now=now + timedelta(seconds=61),
        )


def test_break_glass_workflow_sets_irreversible_record() -> None:
    service = PrivilegeElevationService(ttl_seconds=300)
    now = datetime(2026, 2, 26, 12, 0, tzinfo=UTC)

    token = service.issue_break_glass_token(
        principal_id="alice",
        role="admin",
        incident_id="INC-123",
        reason="production outage containment",
        now=now,
    )

    assert token.break_glass is True
    assert len(service.break_glass_records) == 1
    assert service.break_glass_records[0].irreversible_audit_flag is True

    with pytest.raises(BreakGlassError):
        service.issue_break_glass_token(
            principal_id="alice",
            role="admin",
            incident_id="",
            reason="missing incident id",
            now=now,
        )


def test_privileged_session_recording_support() -> None:
    recorder = PrivilegedSessionRecorder()
    session_id = recorder.start_session(
        principal_id="alice",
        role="admin",
        reason="approve high-risk manifest",
        break_glass=False,
    )
    recorder.record_command(
        session_id=session_id,
        principal_id="alice",
        role="admin",
        command="approve-manifest",
        result="success",
    )
    recorder.end_session(
        session_id=session_id,
        principal_id="alice",
        role="admin",
        status="closed",
    )

    assert [event.event_type for event in recorder.events] == [
        "session_start",
        "command",
        "session_end",
    ]

    with pytest.raises(PrivilegedSessionError):
        recorder.record_command(
            session_id=session_id,
            principal_id="alice",
            role="admin",
            command="late-command",
            result="blocked",
        )
