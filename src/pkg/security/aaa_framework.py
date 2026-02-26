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

import hmac
import time
from dataclasses import dataclass, field
from typing import Any, Protocol

from pkg.logging.framework import emit_audit_event


class AAAError(Exception):
    """Base exception for AAA failures."""


class AuthenticationError(AAAError):
    """Raised when a subject cannot be authenticated."""


class AuthorizationError(AAAError):
    """Raised when a subject is not allowed to perform an action."""


class MFAError(AAAError):
    """Raised when MFA validation fails for a principal."""


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


class PolicyAuthorizer(Protocol):
    """External policy engine adapter for complex execution checks."""

    def authorize_execution(
        self,
        *,
        principal: Principal,
        action: str,
        target: str,
        context: dict[str, Any],
    ) -> None:
        """Raise PermissionError when policy denies execution."""


class AAAService:
    """In-memory AAA service with structured audit logging."""

    def __init__(
        self,
        users: dict[str, str],
        role_bindings: dict[str, set[str]],
        mfa_secrets: dict[str, str] | None = None,
        policy_authorizer: PolicyAuthorizer | None = None,
        max_failed_attempts: int = 5,
        lockout_seconds: int = 300,
    ) -> None:
        self._users = users
        self._role_bindings = role_bindings
        self._mfa_secrets = mfa_secrets or {}
        self._policy_authorizer = policy_authorizer
        self._max_failed_attempts = max_failed_attempts
        self._lockout_seconds = lockout_seconds
        self._failed_attempts: dict[str, int] = {}
        self._locked_until: dict[str, float] = {}
        self._records: list[AccountingRecord] = []

    def authenticate(
        self, principal_id: str, secret: str, mfa_code: str | None = None
    ) -> Principal:
        """Authenticate principal credentials and return principal context."""
        if self._is_locked(principal_id):
            emit_audit_event(
                action="authenticate",
                actor=principal_id,
                target="aaa",
                status="denied",
                reason="account_locked",
            )
            raise AuthenticationError("Account is temporarily locked")

        expected_secret = self._users.get(principal_id)
        if expected_secret is None or not hmac.compare_digest(expected_secret, secret):
            self._record_failed_attempt(principal_id)
            emit_audit_event(
                action="authenticate",
                actor=principal_id,
                target="aaa",
                status="denied",
                reason="invalid_credentials",
            )
            raise AuthenticationError("Invalid credentials")

        if principal_id in self._mfa_secrets:
            expected_mfa = self.generate_mfa_code(principal_id)
            if not mfa_code or not hmac.compare_digest(expected_mfa, mfa_code):
                self._record_failed_attempt(principal_id)
                emit_audit_event(
                    action="authenticate",
                    actor=principal_id,
                    target="aaa",
                    status="denied",
                    reason="invalid_mfa",
                )
                raise MFAError("Invalid MFA code")

        self._failed_attempts.pop(principal_id, None)
        self._locked_until.pop(principal_id, None)
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

    def generate_mfa_code(self, principal_id: str, timestamp: int | None = None) -> str:
        """Generate time-windowed MFA code for local/offline operation."""
        secret = self._mfa_secrets.get(principal_id)
        if not secret:
            raise MFAError("MFA is not configured for principal")
        if timestamp is None:
            timestamp = int(time.time())
        step = timestamp // 30
        digest = hmac.new(
            key=secret.encode("utf-8"),
            msg=str(step).encode("utf-8"),
            digestmod="sha256",
        ).hexdigest()
        return digest[-6:]

    def _is_locked(self, principal_id: str) -> bool:
        locked_until = self._locked_until.get(principal_id)
        if locked_until is None:
            return False
        return time.time() < locked_until

    def _record_failed_attempt(self, principal_id: str) -> None:
        current = self._failed_attempts.get(principal_id, 0) + 1
        self._failed_attempts[principal_id] = current
        if current >= self._max_failed_attempts:
            self._locked_until[principal_id] = time.time() + self._lockout_seconds
            self._failed_attempts[principal_id] = 0

    def authorize(
        self,
        principal: Principal,
        required_role: str,
        action: str,
        target: str,
        policy_context: dict[str, Any] | None = None,
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

        if self._policy_authorizer is not None and policy_context is not None:
            try:
                self._policy_authorizer.authorize_execution(
                    principal=principal,
                    action=action,
                    target=target,
                    context=policy_context,
                )
            except PermissionError as exc:
                emit_audit_event(
                    action="authorize",
                    actor=principal.principal_id,
                    target=target,
                    status="denied",
                    required_role=required_role,
                    attempted_action=action,
                    reason="policy_denied",
                )
                raise AuthorizationError("Policy denied execution") from exc

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
