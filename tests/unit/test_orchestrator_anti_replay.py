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

"""Unit tests for anti-replay nonce and timestamp validation."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from pkg.orchestrator.anti_replay import (
    AntiReplayConfig,
    AntiReplayGuard,
    AntiReplayValidationError,
)
from pkg.orchestrator.manifest import ExecutionManifest, ExecutionTaskContext


def _manifest(
    *,
    nonce: str = "nonce-0001",
    tenant_id: str = "tenant-a",
    issued_at: str = "2026-02-25T00:00:00+00:00",
) -> ExecutionManifest:
    return ExecutionManifest(
        task_context=ExecutionTaskContext(
            task_id="task-001",
            tenant_id=tenant_id,
            operator_id="alice",
            source="api",
            action="run",
            requested_at="2026-02-25T00:00:00+00:00",
            correlation_id="9fe7adbc-58f0-42ab-a5f6-c77cab89f2f7",
        ),
        target_urn="urn:target:ip:10.0.0.5",
        tool_sha256="sha256:" + ("a" * 64),
        nonce=nonce,
        parameters={"ports": [443]},
        issued_at=issued_at,
    )


def test_guard_accepts_fresh_nonce() -> None:
    guard = AntiReplayGuard(
        AntiReplayConfig(
            max_age_seconds=300,
            max_future_skew_seconds=30,
            nonce_retention_seconds=900,
        )
    )
    now = datetime(2026, 2, 25, 0, 1, 0, tzinfo=UTC)

    guard.validate_manifest(
        _manifest(nonce="nonce-a1", issued_at="2026-02-25T00:00:30+00:00"),
        now=now,
    )


def test_guard_rejects_replayed_nonce_for_same_tenant() -> None:
    guard = AntiReplayGuard()
    now = datetime(2026, 2, 25, 0, 1, 0, tzinfo=UTC)
    manifest = _manifest(nonce="nonce-replay", issued_at="2026-02-25T00:00:30+00:00")

    guard.validate_manifest(manifest, now=now)
    with pytest.raises(AntiReplayValidationError, match="replayed nonce"):
        guard.validate_manifest(manifest, now=now + timedelta(seconds=1))


def test_guard_allows_same_nonce_across_tenants() -> None:
    guard = AntiReplayGuard()
    now = datetime(2026, 2, 25, 0, 1, 0, tzinfo=UTC)

    guard.validate_manifest(
        _manifest(
            nonce="nonce-cross-tenant",
            tenant_id="tenant-a",
            issued_at="2026-02-25T00:00:30+00:00",
        ),
        now=now,
    )
    guard.validate_manifest(
        _manifest(
            nonce="nonce-cross-tenant",
            tenant_id="tenant-b",
            issued_at="2026-02-25T00:00:30+00:00",
        ),
        now=now + timedelta(seconds=1),
    )


def test_guard_rejects_stale_timestamp() -> None:
    guard = AntiReplayGuard(AntiReplayConfig(max_age_seconds=60))
    now = datetime(2026, 2, 25, 0, 2, 0, tzinfo=UTC)

    with pytest.raises(AntiReplayValidationError, match="max age"):
        guard.validate_manifest(
            _manifest(nonce="nonce-old", issued_at="2026-02-25T00:00:30+00:00"),
            now=now,
        )


def test_guard_rejects_future_timestamp_beyond_skew() -> None:
    guard = AntiReplayGuard(AntiReplayConfig(max_future_skew_seconds=5))
    now = datetime(2026, 2, 25, 0, 1, 0, tzinfo=UTC)

    with pytest.raises(AntiReplayValidationError, match="future clock skew"):
        guard.validate_manifest(
            _manifest(nonce="nonce-future", issued_at="2026-02-25T00:01:10+00:00"),
            now=now,
        )
