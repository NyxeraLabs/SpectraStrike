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

"""Unit tests for sqlmap wrapper standardized SDK contract."""

from __future__ import annotations

import base64
from typing import Any

import pytest

from pkg.orchestrator.telemetry_ingestion import TelemetryIngestionPipeline
from pkg.wrappers.sqlmap import (
    SqlmapExecutionError,
    SqlmapRequest,
    SqlmapWrapper,
)


def test_build_command_contains_target_and_batch_mode() -> None:
    wrapper = SqlmapWrapper(binary="sqlmap", signer=lambda _payload: "sig")
    request = SqlmapRequest(
        target="http://127.0.0.1/vuln.php?id=1",
        command="-u http://127.0.0.1/vuln.php?id=1 --batch --risk=1",
        extra_args=["--timeout=5"],
    )
    command = wrapper.build_command(request)
    assert command[0] == "sqlmap"
    assert "-u" in command
    assert "http://127.0.0.1/vuln.php?id=1" in command
    assert "--batch" in command
    assert "--timeout=5" in command


def test_detect_version_parses_banner() -> None:
    def fake_runner(command: list[str], _timeout: float):
        _ = command

        class _R:
            returncode = 0
            stdout = "1.8.2#stable"
            stderr = ""

        return _R()

    wrapper = SqlmapWrapper(runner=fake_runner, signer=lambda _payload: "sig")  # type: ignore[arg-type]
    assert wrapper.detect_version() == "1.8.2"


def test_execute_builds_contract_fields() -> None:
    def fake_runner(command: list[str], _timeout: float):
        if "--version" in command or "-h" in command or "--help" in command:

            class _V:
                returncode = 0
                stdout = "1.8.2#stable"
                stderr = ""

            return _V()

        class _R:
            returncode = 0
            stdout = "[INFO] all tested parameters do not appear to be injectable."
            stderr = ""

        return _R()

    def fake_signer(payload: bytes) -> str:
        return base64.b64encode(payload).decode("utf-8")

    wrapper = SqlmapWrapper(runner=fake_runner, signer=fake_signer)  # type: ignore[arg-type]
    result = wrapper.execute(
        SqlmapRequest(
            target="http://127.0.0.1/vuln.php?id=1",
            command="-u http://127.0.0.1/vuln.php?id=1 --batch --risk=1",
        ),
        tenant_id="tenant-a",
        operator_id="operator-a",
    )
    assert result.status == "success"
    assert result.return_code == 0
    assert len(result.execution_fingerprint) == 64
    assert len(result.attestation_measurement_hash) == 64
    assert result.payload_signature_algorithm == "Ed25519"


def test_send_to_orchestrator_emits_validated_payload() -> None:
    def fake_runner(command: list[str], _timeout: float):
        if "--version" in command or "-h" in command or "--help" in command:

            class _V:
                returncode = 0
                stdout = "1.8.2#stable"
                stderr = ""

            return _V()

        class _R:
            returncode = 0
            stdout = "ok"
            stderr = ""

        return _R()

    wrapper = SqlmapWrapper(runner=fake_runner, signer=lambda _payload: "sig-ed25519")  # type: ignore[arg-type]
    telemetry = TelemetryIngestionPipeline(batch_size=1)
    result = wrapper.execute(
        SqlmapRequest(
            target="http://127.0.0.1/vuln.php?id=1",
            command="-u http://127.0.0.1/vuln.php?id=1 --batch --risk=1",
        ),
        tenant_id="tenant-a",
        operator_id="operator-a",
    )
    event = wrapper.send_to_orchestrator(
        result,
        telemetry=telemetry,
        tenant_id="tenant-a",
        operator_id="operator-a",
        actor="qa-bot",
    )
    assert event.event_type == "sqlmap_scan_completed"
    assert event.attributes["payload_signature_algorithm"] == "Ed25519"
    assert event.attributes["execution_fingerprint"] == result.execution_fingerprint


def test_execute_raises_on_failure() -> None:
    def fake_runner(command: list[str], _timeout: float):
        if "--version" in command or "-h" in command or "--help" in command:

            class _V:
                returncode = 0
                stdout = "1.8.2#stable"
                stderr = ""

            return _V()

        class _R:
            returncode = 1
            stdout = ""
            stderr = "target URL is invalid"

        return _R()

    wrapper = SqlmapWrapper(runner=fake_runner, signer=lambda _payload: "sig")  # type: ignore[arg-type]
    with pytest.raises(SqlmapExecutionError, match="target URL is invalid"):
        wrapper.execute(
            SqlmapRequest(target="bad", command="-u bad --batch"),
            tenant_id="tenant-a",
            operator_id="operator-a",
        )


def test_send_to_orchestrator_supports_ingest_payload_compatible_sink() -> None:
    class BrokenTelemetry:
        def ingest_payload(self, payload: dict[str, Any]) -> object:
            return payload

    wrapper = SqlmapWrapper(
        signer=lambda _payload: "sig",
        runner=lambda _cmd, _timeout: type(
            "R", (), {"returncode": 0, "stdout": "1.8.2#stable", "stderr": ""}
        )(),  # type: ignore[arg-type]
    )
    result = wrapper.execute(
        SqlmapRequest(target="http://127.0.0.1/vuln.php?id=1", extra_args=["--dry-run"]),
        tenant_id="tenant-a",
        operator_id="operator-a",
    )
    event = wrapper.send_to_orchestrator(  # type: ignore[arg-type]
        result,
        telemetry=BrokenTelemetry(),
        tenant_id="tenant-a",
        operator_id="operator-a",
    )
    assert event["event_type"] == "sqlmap_scan_completed"
