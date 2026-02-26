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

"""Sprint 20 high-assurance controls for privileged operations."""

from __future__ import annotations

import secrets
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

from pkg.logging.framework import emit_integrity_audit_event


class PrivilegeElevationError(PermissionError):
    """Raised when privilege elevation token checks fail."""


class BreakGlassError(PermissionError):
    """Raised when break-glass workflow constraints fail."""


class PrivilegedSessionError(RuntimeError):
    """Raised when privileged session recording constraints fail."""


@dataclass(slots=True)
class PrivilegeElevationToken:
    """Time-bound one-time token for privileged role elevation."""

    token_id: str
    principal_id: str
    role: str
    justification: str
    issued_at: str
    expires_at: str
    break_glass: bool = False
    consumed: bool = False
    consumed_at: str | None = None


@dataclass(slots=True, frozen=True)
class BreakGlassRecord:
    """Irreversible break-glass activation record."""

    record_id: str
    principal_id: str
    role: str
    incident_id: str
    reason: str
    activated_at: str
    irreversible_audit_flag: bool = True


@dataclass(slots=True)
class SessionRecordingEvent:
    """Single privileged session recording event."""

    timestamp: str
    event_type: str
    session_id: str
    principal_id: str
    role: str
    payload: dict[str, Any] = field(default_factory=dict)


class PrivilegeElevationService:
    """Issue and validate short-lived one-time elevation tokens."""

    def __init__(self, *, ttl_seconds: int = 900) -> None:
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be greater than zero")
        self._ttl_seconds = ttl_seconds
        self._tokens: dict[str, PrivilegeElevationToken] = {}
        self._break_glass_records: list[BreakGlassRecord] = []

    def issue_token(
        self,
        *,
        principal_id: str,
        role: str,
        justification: str,
        break_glass: bool = False,
        now: datetime | None = None,
    ) -> PrivilegeElevationToken:
        if not principal_id.strip():
            raise ValueError("principal_id is required")
        if not role.strip():
            raise ValueError("role is required")
        if not justification.strip():
            raise ValueError("justification is required")

        issued_dt = now or datetime.now(UTC)
        expires_dt = issued_dt + timedelta(seconds=self._ttl_seconds)
        token = PrivilegeElevationToken(
            token_id=secrets.token_hex(16),
            principal_id=principal_id,
            role=role,
            justification=justification,
            issued_at=issued_dt.isoformat(),
            expires_at=expires_dt.isoformat(),
            break_glass=break_glass,
        )
        self._tokens[token.token_id] = token
        emit_integrity_audit_event(
            action="privilege_elevation_issue",
            actor=principal_id,
            target=role,
            status="success",
            token_id=token.token_id,
            expires_at=token.expires_at,
            break_glass=break_glass,
            irreversible_audit_flag=break_glass,
        )
        return token

    def issue_break_glass_token(
        self,
        *,
        principal_id: str,
        role: str,
        incident_id: str,
        reason: str,
        now: datetime | None = None,
    ) -> PrivilegeElevationToken:
        if not incident_id.strip():
            raise BreakGlassError("incident_id is required for break-glass")
        if not reason.strip():
            raise BreakGlassError("reason is required for break-glass")

        token = self.issue_token(
            principal_id=principal_id,
            role=role,
            justification=reason,
            break_glass=True,
            now=now,
        )
        record = BreakGlassRecord(
            record_id=secrets.token_hex(12),
            principal_id=principal_id,
            role=role,
            incident_id=incident_id,
            reason=reason,
            activated_at=(now or datetime.now(UTC)).isoformat(),
        )
        self._break_glass_records.append(record)
        emit_integrity_audit_event(
            action="break_glass_activate",
            actor=principal_id,
            target=role,
            status="success",
            token_id=token.token_id,
            incident_id=incident_id,
            irreversible_audit_flag=True,
        )
        return token

    def consume_token(
        self,
        *,
        token_id: str,
        principal_id: str,
        role: str,
        now: datetime | None = None,
    ) -> None:
        token = self._tokens.get(token_id)
        if token is None:
            raise PrivilegeElevationError("elevation token not found")
        if token.consumed:
            raise PrivilegeElevationError("elevation token already consumed")
        if token.principal_id != principal_id or token.role != role:
            raise PrivilegeElevationError("elevation token subject/role mismatch")

        current = now or datetime.now(UTC)
        expires_at = datetime.fromisoformat(token.expires_at.replace("Z", "+00:00"))
        if current > expires_at:
            raise PrivilegeElevationError("elevation token expired")

        token.consumed = True
        token.consumed_at = current.isoformat()
        emit_integrity_audit_event(
            action="privilege_elevation_consume",
            actor=principal_id,
            target=role,
            status="success",
            token_id=token_id,
            break_glass=token.break_glass,
            irreversible_audit_flag=token.break_glass,
        )

    @property
    def break_glass_records(self) -> list[BreakGlassRecord]:
        """Return immutable copy of break-glass activation records."""
        return list(self._break_glass_records)


class PrivilegedSessionRecorder:
    """In-memory privileged session recording with integrity audit output."""

    def __init__(self) -> None:
        self._events: list[SessionRecordingEvent] = []
        self._active_sessions: set[str] = set()

    def start_session(
        self,
        *,
        principal_id: str,
        role: str,
        reason: str,
        break_glass: bool = False,
    ) -> str:
        if not principal_id.strip():
            raise PrivilegedSessionError("principal_id is required")
        if not role.strip():
            raise PrivilegedSessionError("role is required")
        if not reason.strip():
            raise PrivilegedSessionError("reason is required")

        session_id = secrets.token_hex(12)
        self._active_sessions.add(session_id)
        self._record(
            event_type="session_start",
            session_id=session_id,
            principal_id=principal_id,
            role=role,
            payload={
                "reason": reason,
                "break_glass": break_glass,
                "irreversible_audit_flag": break_glass,
            },
        )
        return session_id

    def record_command(
        self,
        *,
        session_id: str,
        principal_id: str,
        role: str,
        command: str,
        result: str,
    ) -> None:
        if session_id not in self._active_sessions:
            raise PrivilegedSessionError("session is not active")
        self._record(
            event_type="command",
            session_id=session_id,
            principal_id=principal_id,
            role=role,
            payload={"command": command, "result": result},
        )

    def end_session(
        self,
        *,
        session_id: str,
        principal_id: str,
        role: str,
        status: str,
    ) -> None:
        if session_id not in self._active_sessions:
            raise PrivilegedSessionError("session is not active")
        self._active_sessions.remove(session_id)
        self._record(
            event_type="session_end",
            session_id=session_id,
            principal_id=principal_id,
            role=role,
            payload={"status": status},
        )

    def _record(
        self,
        *,
        event_type: str,
        session_id: str,
        principal_id: str,
        role: str,
        payload: dict[str, Any],
    ) -> None:
        event = SessionRecordingEvent(
            timestamp=datetime.now(UTC).isoformat(),
            event_type=event_type,
            session_id=session_id,
            principal_id=principal_id,
            role=role,
            payload=payload,
        )
        self._events.append(event)
        emit_integrity_audit_event(
            action=f"privileged_session_{event_type}",
            actor=principal_id,
            target=role,
            status="success",
            session_id=session_id,
            event_payload=payload,
        )

    @property
    def events(self) -> list[SessionRecordingEvent]:
        """Return privileged session recording events."""
        return list(self._events)
