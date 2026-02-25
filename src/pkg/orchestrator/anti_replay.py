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

"""Anti-replay protections for signed execution manifest dispatch."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from threading import Lock

from pkg.orchestrator.manifest import ExecutionManifest


class AntiReplayValidationError(ValueError):
    """Raised when manifest timestamp/nonce replay checks fail."""


@dataclass(slots=True, frozen=True)
class AntiReplayConfig:
    """Policy settings for nonce and timestamp replay protection."""

    max_age_seconds: int = 300
    max_future_skew_seconds: int = 30
    nonce_retention_seconds: int = 900

    def __post_init__(self) -> None:
        if self.max_age_seconds <= 0:
            raise ValueError("max_age_seconds must be greater than zero")
        if self.max_future_skew_seconds < 0:
            raise ValueError("max_future_skew_seconds must be zero or greater")
        if self.nonce_retention_seconds <= 0:
            raise ValueError("nonce_retention_seconds must be greater than zero")


class AntiReplayGuard:
    """In-memory replay guard using tenant-scoped nonce tracking."""

    def __init__(self, config: AntiReplayConfig | None = None) -> None:
        self._config = config or AntiReplayConfig()
        self._seen_nonces: dict[str, datetime] = {}
        self._lock = Lock()

    def validate_manifest(
        self,
        manifest: ExecutionManifest,
        *,
        now: datetime | None = None,
    ) -> None:
        """Validate timestamp window and reject replayed nonces."""
        current = now or datetime.now(UTC)
        issued_at = self._parse_timestamp(manifest.issued_at)
        self._validate_timestamp(issued_at=issued_at, now=current)
        self._check_and_store_nonce(
            tenant_id=manifest.task_context.tenant_id,
            nonce=manifest.nonce,
            now=current,
        )

    def _validate_timestamp(self, *, issued_at: datetime, now: datetime) -> None:
        age = (now - issued_at).total_seconds()
        if age > self._config.max_age_seconds:
            raise AntiReplayValidationError("manifest timestamp exceeds max age window")

        if issued_at > now + timedelta(seconds=self._config.max_future_skew_seconds):
            raise AntiReplayValidationError(
                "manifest timestamp exceeds allowed future clock skew"
            )

    def _check_and_store_nonce(
        self, *, tenant_id: str, nonce: str, now: datetime
    ) -> None:
        key = f"{tenant_id}:{nonce}"
        expiry = now + timedelta(seconds=self._config.nonce_retention_seconds)

        with self._lock:
            self._evict_expired(now)
            if key in self._seen_nonces:
                raise AntiReplayValidationError("replayed nonce detected")
            self._seen_nonces[key] = expiry

    def _evict_expired(self, now: datetime) -> None:
        expired = [key for key, expiry in self._seen_nonces.items() if expiry <= now]
        for key in expired:
            del self._seen_nonces[key]

    @staticmethod
    def _parse_timestamp(raw: str) -> datetime:
        try:
            parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError as exc:
            raise AntiReplayValidationError(
                "manifest issued_at must be ISO-8601 compatible"
            ) from exc

        if parsed.tzinfo is None:
            raise AntiReplayValidationError(
                "manifest issued_at must include timezone information"
            )
        return parsed.astimezone(UTC)
