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

"""Manual Metasploit ingestion for operator-driven execution workflows."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import requests
from requests import Response, Session
from requests.exceptions import RequestException

from pkg.logging.framework import get_logger
from pkg.orchestrator.telemetry_ingestion import TelemetryIngestionPipeline
from pkg.telemetry.sdk import build_internal_telemetry_event

logger = get_logger("spectrastrike.integration.metasploit_manual")

_RETRYABLE_STATUSES = {429, 500, 502, 503, 504}


class MetasploitManualError(RuntimeError):
    """Base error for manual Metasploit ingestion operations."""


class MetasploitManualConfigError(MetasploitManualError):
    """Raised when manual Metasploit config is invalid."""


class MetasploitManualTransportError(MetasploitManualError):
    """Raised when HTTP transport to Metasploit fails."""


class MetasploitManualAPIError(MetasploitManualError):
    """Raised when Metasploit API returns an unexpected response."""


@dataclass(slots=True)
class MetasploitManualConfig:
    """Runtime config for Metasploit manual-ingestion data API."""

    base_url: str = "https://metasploit.remote.operator:5443"
    username: str = ""
    password: str = ""
    verify_tls: bool = True
    timeout_seconds: float = 10.0
    max_retries: int = 2
    backoff_seconds: float = 0.2

    def __post_init__(self) -> None:
        parsed = urlparse(self.base_url)
        if not parsed.scheme or not parsed.netloc:
            raise MetasploitManualConfigError("base_url must be an absolute URL")
        if self.timeout_seconds <= 0:
            raise MetasploitManualConfigError(
                "timeout_seconds must be greater than zero"
            )
        if self.max_retries < 0:
            raise MetasploitManualConfigError("max_retries must be zero or greater")
        if self.backoff_seconds < 0:
            raise MetasploitManualConfigError("backoff_seconds must be zero or greater")
        if not self.username or not self.password:
            raise MetasploitManualConfigError("username and password are required")

    @classmethod
    def from_env(cls, prefix: str = "MSF_MANUAL_") -> MetasploitManualConfig:
        """Build config from environment for remote operator data API endpoints."""
        base_url = os.getenv(
            f"{prefix}BASE_URL", "https://metasploit.remote.operator:5443"
        )
        username = os.getenv(f"{prefix}USERNAME", "")
        password = os.getenv(f"{prefix}PASSWORD", "")
        verify_tls_raw = os.getenv(f"{prefix}VERIFY_TLS", "true").strip().lower()
        verify_tls = verify_tls_raw in {"1", "true", "yes", "on"}
        timeout_seconds = float(os.getenv(f"{prefix}TIMEOUT_SECONDS", "10.0"))
        max_retries = int(os.getenv(f"{prefix}MAX_RETRIES", "2"))
        backoff_seconds = float(os.getenv(f"{prefix}BACKOFF_SECONDS", "0.2"))
        return cls(
            base_url=base_url,
            username=username,
            password=password,
            verify_tls=verify_tls,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            backoff_seconds=backoff_seconds,
        )


@dataclass(slots=True)
class MetasploitSession:
    """Normalized Metasploit session row."""

    session_id: str
    session_type: str
    target_host: str
    via_exploit: str | None
    raw: dict[str, Any]


@dataclass(slots=True)
class MetasploitSessionEvent:
    """Normalized Metasploit session-event row."""

    event_id: str
    session_id: str | None
    event_type: str
    created_at: str | None
    raw: dict[str, Any]


@dataclass(slots=True)
class IngestionCheckpoint:
    """Checkpoint state used to avoid duplicate ingestion."""

    seen_session_ids: set[str] = field(default_factory=set)
    last_session_event_id: str | None = None


@dataclass(slots=True)
class IngestionResult:
    """Summary of one ingestion pass."""

    observed_sessions: int
    observed_session_events: int
    emitted_events: int
    checkpoint: IngestionCheckpoint


class MetasploitManualClient:
    """HTTP client for Metasploit webservice data APIs used for manual ingestion."""

    def __init__(
        self, config: MetasploitManualConfig, session: Session | None = None
    ) -> None:
        self._config = config
        self._session = session or requests.Session()
        self._authenticated = False

    def login(self) -> None:
        """Authenticate and keep session cookies for follow-up API calls."""
        response = self._request_raw(
            method="POST",
            path="/api/v1/auth/login",
            json_payload={
                "username": self._config.username,
                "password": self._config.password,
            },
            allow_redirects=False,
            allow_auth_retry=False,
        )
        if response.status_code not in {200, 302, 303}:
            raise MetasploitManualAPIError(
                f"login failed with status {response.status_code}"
            )
        self._authenticated = True
        logger.info("Authenticated to Metasploit webservice")

    def list_sessions(self) -> list[MetasploitSession]:
        """Fetch current Metasploit sessions."""
        payload = self._request_json("GET", "/api/v1/sessions")
        rows = self._normalize_rows(payload)
        sessions: list[MetasploitSession] = []
        for row in rows:
            session_id = str(row.get("id", row.get("session_id", ""))).strip()
            if not session_id:
                continue
            target_host = str(
                row.get("target_host")
                or row.get("host")
                or row.get("rhost")
                or row.get("tunnel_peer")
                or "unknown"
            )
            sessions.append(
                MetasploitSession(
                    session_id=session_id,
                    session_type=str(
                        row.get("session_type")
                        or row.get("stype")
                        or row.get("type")
                        or "unknown"
                    ),
                    target_host=target_host,
                    via_exploit=(
                        str(row["via_exploit"])
                        if row.get("via_exploit") not in {None, ""}
                        else None
                    ),
                    raw=row,
                )
            )
        return sessions

    def list_session_events(self) -> list[MetasploitSessionEvent]:
        """Fetch session events generated by operator activity."""
        payload = self._request_json("GET", "/api/v1/session-events")
        rows = self._normalize_rows(payload)
        events: list[MetasploitSessionEvent] = []
        for row in rows:
            event_id = str(row.get("id", row.get("event_id", ""))).strip()
            if not event_id:
                continue
            session_id_raw = row.get("session_id")
            session_id = (
                str(session_id_raw) if session_id_raw not in {None, ""} else None
            )
            events.append(
                MetasploitSessionEvent(
                    event_id=event_id,
                    session_id=session_id,
                    event_type=str(
                        row.get("etype") or row.get("event_type") or "unknown"
                    ),
                    created_at=(
                        str(row["created_at"]) if row.get("created_at") else None
                    ),
                    raw=row,
                )
            )
        return events

    def _request_json(self, method: str, path: str) -> dict[str, Any]:
        response = self._request_raw(method=method, path=path)
        if response.status_code >= 400:
            raise MetasploitManualAPIError(
                f"{path} failed with status {response.status_code}"
            )
        try:
            payload = response.json()
        except ValueError as exc:
            raise MetasploitManualAPIError(f"{path} did not return JSON") from exc
        if not isinstance(payload, dict):
            raise MetasploitManualAPIError(f"{path} returned unexpected payload shape")
        return payload

    def _request_raw(
        self,
        method: str,
        path: str,
        json_payload: dict[str, Any] | None = None,
        allow_redirects: bool = True,
        allow_auth_retry: bool = True,
    ) -> Response:
        url = urljoin(self._config.base_url.rstrip("/") + "/", path.lstrip("/"))
        attempts = self._config.max_retries + 1
        authed_retry_used = False
        last_error: Exception | None = None

        for attempt in range(1, attempts + 1):
            try:
                response = self._session.request(
                    method=method,
                    url=url,
                    json=json_payload,
                    timeout=self._config.timeout_seconds,
                    verify=self._config.verify_tls,
                    allow_redirects=allow_redirects,
                )
            except RequestException as exc:
                last_error = exc
                if attempt >= attempts:
                    raise MetasploitManualTransportError(str(exc)) from exc
                time.sleep(self._config.backoff_seconds * (2 ** (attempt - 1)))
                continue

            if (
                allow_auth_retry
                and response.status_code in {401, 403}
                and not authed_retry_used
            ):
                self.login()
                authed_retry_used = True
                continue

            if response.status_code in _RETRYABLE_STATUSES and attempt < attempts:
                time.sleep(self._config.backoff_seconds * (2 ** (attempt - 1)))
                continue

            return response

        raise MetasploitManualTransportError(
            str(last_error) if last_error else "unknown transport error"
        )

    def _normalize_rows(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        data = payload.get("data")
        if isinstance(data, list):
            return [row for row in data if isinstance(row, dict)]
        if isinstance(data, dict):
            rows: list[dict[str, Any]] = []
            for key, value in data.items():
                if isinstance(value, dict):
                    row = dict(value)
                    row.setdefault("id", key)
                    rows.append(row)
            return rows
        return []


class MetasploitManualIngestor:
    """Sync runner that converts Metasploit manual activity into telemetry events."""

    def __init__(
        self, client: MetasploitManualClient, telemetry: TelemetryIngestionPipeline
    ) -> None:
        self._client = client
        self._telemetry = telemetry

    def sync(
        self,
        tenant_id: str,
        actor: str = "red-team-operator",
        checkpoint: IngestionCheckpoint | None = None,
    ) -> IngestionResult:
        """Sync sessions/events and emit only unseen records into telemetry."""
        state = checkpoint or IngestionCheckpoint()
        self._client.login()
        sessions = self._client.list_sessions()
        session_events = self._client.list_session_events()

        emitted = 0
        for session in sessions:
            if session.session_id in state.seen_session_ids:
                continue
            self._telemetry.ingest_payload(
                build_internal_telemetry_event(
                event_type="metasploit_manual_session_observed",
                actor=actor,
                target="metasploit",
                status="success",
                tenant_id=tenant_id,
                attributes={
                    "session_id": session.session_id,
                    "session_type": session.session_type,
                    "target_host": session.target_host,
                    "via_exploit": session.via_exploit,
                    "source": "manual_metasploit",
                },
                )
            )
            state.seen_session_ids.add(session.session_id)
            emitted += 1

        for event in sorted(
            session_events, key=lambda item: self._event_sort_key(item.event_id)
        ):
            if state.last_session_event_id and self._event_sort_key(
                event.event_id
            ) <= self._event_sort_key(state.last_session_event_id):
                continue
            self._telemetry.ingest_payload(
                build_internal_telemetry_event(
                event_type="metasploit_manual_event_observed",
                actor=actor,
                target="metasploit",
                status="success",
                tenant_id=tenant_id,
                attributes={
                    "event_id": event.event_id,
                    "session_id": event.session_id,
                    "session_event_type": event.event_type,
                    "created_at": event.created_at,
                    "source": "manual_metasploit",
                },
                )
            )
            state.last_session_event_id = event.event_id
            emitted += 1

        logger.info(
            "Metasploit manual sync completed: sessions=%s events=%s emitted=%s",
            len(sessions),
            len(session_events),
            emitted,
        )
        return IngestionResult(
            observed_sessions=len(sessions),
            observed_session_events=len(session_events),
            emitted_events=emitted,
            checkpoint=state,
        )

    def _event_sort_key(self, raw_id: str) -> tuple[int, str]:
        try:
            return (0, f"{int(raw_id):020d}")
        except ValueError:
            return (1, raw_id)


class IngestionCheckpointStore:
    """File-backed checkpoint persistence for manual Metasploit ingestion."""

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)

    def load(self) -> IngestionCheckpoint:
        if not self._path.exists():
            return IngestionCheckpoint()
        payload = json.loads(self._path.read_text(encoding="utf-8"))
        seen_session_ids = payload.get("seen_session_ids", [])
        if not isinstance(seen_session_ids, list):
            seen_session_ids = []
        last_session_event_id = payload.get("last_session_event_id")
        return IngestionCheckpoint(
            seen_session_ids={str(item) for item in seen_session_ids},
            last_session_event_id=(
                str(last_session_event_id) if last_session_event_id else None
            ),
        )

    def save(self, checkpoint: IngestionCheckpoint) -> None:
        payload = {
            "seen_session_ids": sorted(checkpoint.seen_session_ids),
            "last_session_event_id": checkpoint.last_session_event_id,
        }
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
