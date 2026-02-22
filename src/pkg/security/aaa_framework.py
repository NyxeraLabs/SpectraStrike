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

"""Core AAA framework components for authentication, authorization, and accounting."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pkg.logging.framework import emit_audit_event


class AAAError(Exception):
    """Base exception for AAA failures."""


class AuthenticationError(AAAError):
    """Raised when a subject cannot be authenticated."""


class AuthorizationError(AAAError):
    """Raised when a subject is not allowed to perform an action."""


@dataclass(slots=True)
class Principal:
    """Authenticated subject information."""

    principal_id: str
    roles: set[str] = field(default_factory=set)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AccountingRecord:
    """Accounting record for audited operations."""

    principal_id: str
    action: str
    target: str
    status: str
    details: dict[str, Any] = field(default_factory=dict)


class AAAService:
    """In-memory AAA service with structured audit logging."""

    def __init__(
        self, users: dict[str, str], role_bindings: dict[str, set[str]]
    ) -> None:
        self._users = users
        self._role_bindings = role_bindings
        self._records: list[AccountingRecord] = []

    def authenticate(self, principal_id: str, secret: str) -> Principal:
        """Authenticate principal credentials and return principal context."""
        expected_secret = self._users.get(principal_id)
        if expected_secret is None or expected_secret != secret:
            emit_audit_event(
                action="authenticate",
                actor=principal_id,
                target="aaa",
                status="denied",
                reason="invalid_credentials",
            )
            raise AuthenticationError("Invalid credentials")

        principal = Principal(
            principal_id=principal_id,
            roles=set(self._role_bindings.get(principal_id, set())),
        )
        emit_audit_event(
            action="authenticate",
            actor=principal_id,
            target="aaa",
            status="success",
            roles=sorted(principal.roles),
        )
        return principal

    def authorize(
        self, principal: Principal, required_role: str, action: str, target: str
    ) -> None:
        """Authorize a principal for an action based on required role."""
        if required_role not in principal.roles:
            emit_audit_event(
                action="authorize",
                actor=principal.principal_id,
                target=target,
                status="denied",
                required_role=required_role,
                attempted_action=action,
            )
            raise AuthorizationError("Insufficient role")

        emit_audit_event(
            action="authorize",
            actor=principal.principal_id,
            target=target,
            status="success",
            required_role=required_role,
            attempted_action=action,
        )

    def account(
        self,
        principal: Principal,
        action: str,
        target: str,
        status: str,
        **details: Any,
    ) -> AccountingRecord:
        """Create and persist accounting records for privileged operations."""
        record = AccountingRecord(
            principal_id=principal.principal_id,
            action=action,
            target=target,
            status=status,
            details=details,
        )
        self._records.append(record)
        emit_audit_event(
            action="account",
            actor=principal.principal_id,
            target=target,
            status=status,
            operation=action,
            details=details,
        )
        return record

    @property
    def records(self) -> list[AccountingRecord]:
        """Return accounting records."""
        return list(self._records)
