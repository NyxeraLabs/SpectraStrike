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

"""Unit tests for manual Metasploit ingestion flow."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest

from pkg.integration.metasploit_manual import (
    IngestionCheckpoint,
    IngestionCheckpointStore,
    MetasploitManualConfigError,
    MetasploitManualClient,
    MetasploitManualConfig,
    MetasploitManualIngestor,
)
from pkg.orchestrator.telemetry_ingestion import TelemetryIngestionPipeline


@dataclass
class FakeResponse:
    status_code: int
    payload: dict[str, Any] = field(default_factory=dict)

    def json(self) -> dict[str, Any]:
        return self.payload


class FakeSession:
    def __init__(self, queued: list[FakeResponse]) -> None:
        self._queued = list(queued)
        self.calls: list[dict[str, Any]] = []

    def request(self, **kwargs: Any) -> FakeResponse:
        self.calls.append(kwargs)
        if not self._queued:
            raise AssertionError("no queued fake responses")
        return self._queued.pop(0)


def _config() -> MetasploitManualConfig:
    return MetasploitManualConfig(
        base_url="https://localhost:5443",
        username="operator",
        password="secret",
        verify_tls=False,
        max_retries=0,
        backoff_seconds=0,
    )


def test_client_login_accepts_redirect_status() -> None:
    session = FakeSession([FakeResponse(303, {})])
    client = MetasploitManualClient(_config(), session=session)

    client.login()

    assert session.calls[0]["method"] == "POST"
    assert session.calls[0]["url"].endswith("/api/v1/auth/login")


def test_list_sessions_and_events_parse_data_rows() -> None:
    session = FakeSession(
        [
            FakeResponse(303, {}),
            FakeResponse(
                200,
                {
                    "data": [
                        {
                            "id": 1,
                            "stype": "meterpreter",
                            "target_host": "10.0.0.5",
                            "via_exploit": "unix/ftp/sample",
                        }
                    ]
                },
            ),
            FakeResponse(
                200,
                {"data": [{"id": 9, "session_id": 1, "etype": "command", "created_at": "now"}]},
            ),
        ]
    )
    client = MetasploitManualClient(_config(), session=session)
    client.login()

    sessions = client.list_sessions()
    events = client.list_session_events()

    assert len(sessions) == 1
    assert sessions[0].session_id == "1"
    assert sessions[0].session_type == "meterpreter"
    assert sessions[0].via_exploit == "unix/ftp/sample"

    assert len(events) == 1
    assert events[0].event_id == "9"
    assert events[0].session_id == "1"
    assert events[0].event_type == "command"


def test_ingestor_sync_emits_only_unseen_records() -> None:
    session = FakeSession(
        [
            FakeResponse(303, {}),
            FakeResponse(
                200,
                {
                    "data": [
                        {"id": 1, "stype": "shell", "target_host": "10.0.0.7"},
                        {"id": 2, "stype": "meterpreter", "target_host": "10.0.0.8"},
                    ]
                },
            ),
            FakeResponse(
                200,
                {
                    "data": [
                        {"id": 10, "session_id": 1, "etype": "open"},
                        {"id": 11, "session_id": 2, "etype": "command"},
                    ]
                },
            ),
        ]
    )
    client = MetasploitManualClient(_config(), session=session)
    telemetry = TelemetryIngestionPipeline(batch_size=10)
    ingestor = MetasploitManualIngestor(client, telemetry)
    checkpoint = IngestionCheckpoint(seen_session_ids={"1"}, last_session_event_id="10")

    result = ingestor.sync(actor="qa-user", checkpoint=checkpoint)
    flushed = telemetry.flush_all()

    assert result.observed_sessions == 2
    assert result.observed_session_events == 2
    assert result.emitted_events == 2
    assert result.checkpoint.seen_session_ids == {"1", "2"}
    assert result.checkpoint.last_session_event_id == "11"

    event_types = [event.event_type for event in flushed]
    assert event_types == [
        "metasploit_manual_session_observed",
        "metasploit_manual_event_observed",
    ]


def test_checkpoint_store_roundtrip(tmp_path: Path) -> None:
    store = IngestionCheckpointStore(tmp_path / "checkpoint.json")
    checkpoint = IngestionCheckpoint(seen_session_ids={"1", "7"}, last_session_event_id="55")

    store.save(checkpoint)
    loaded = store.load()

    assert loaded.seen_session_ids == {"1", "7"}
    assert loaded.last_session_event_id == "55"

    payload = json.loads((tmp_path / "checkpoint.json").read_text(encoding="utf-8"))
    assert payload["last_session_event_id"] == "55"


def test_missing_credentials_fails_config_validation() -> None:
    with pytest.raises(MetasploitManualConfigError):
        MetasploitManualConfig(base_url="https://localhost:5443", username="", password="")
