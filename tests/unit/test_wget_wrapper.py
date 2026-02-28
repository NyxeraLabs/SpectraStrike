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

"""Unit tests for wget wrapper standardized SDK contract."""

from __future__ import annotations

import base64
from typing import Any

import pytest

from pkg.orchestrator.telemetry_ingestion import TelemetryIngestionPipeline
from pkg.wrappers.wget import (
    WgetExecutionError,
    WgetRequest,
    WgetWrapper,
)


def test_build_command_contains_url_and_output_flag() -> None:
    wrapper = WgetWrapper(binary="wget", signer=lambda _payload: "sig")
    request = WgetRequest(
        target="http://127.0.0.1",
        command="http://127.0.0.1 -O /tmp/out --timeout=3",
        extra_args=["--no-check-certificate"],
    )
    command = wrapper.build_command(request)
    assert command[0] == "wget"
    assert "http://127.0.0.1" in command
    assert "-O" in command
    assert "/tmp/out" in command
    assert "--no-check-certificate" in command


def test_detect_version_parses_banner() -> None:
    def fake_runner(command: list[str], _timeout: float):
        _ = command

        class _R:
            returncode = 0
            stdout = "GNU Wget 1.21.4 built on linux-gnu."
            stderr = ""

        return _R()

    wrapper = WgetWrapper(runner=fake_runner, signer=lambda _payload: "sig")  # type: ignore[arg-type]
    assert wrapper.detect_version() == "1.21.4"


def test_execute_builds_contract_fields() -> None:
    def fake_runner(command: list[str], _timeout: float):
        if "--version" in command or "-V" in command or "--help" in command:

            class _V:
                returncode = 0
                stdout = "GNU Wget 1.21.4 built on linux-gnu."
                stderr = ""

            return _V()

        class _R:
            returncode = 0
            stdout = "saved [123/123]"
            stderr = ""

        return _R()

    def fake_signer(payload: bytes) -> str:
        return base64.b64encode(payload).decode("utf-8")

    wrapper = WgetWrapper(runner=fake_runner, signer=fake_signer)  # type: ignore[arg-type]
    result = wrapper.execute(
        WgetRequest(target="http://127.0.0.1", command="http://127.0.0.1 -O /tmp/out"),
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
        if "--version" in command or "-V" in command or "--help" in command:

            class _V:
                returncode = 0
                stdout = "GNU Wget 1.21.4 built on linux-gnu."
                stderr = ""

            return _V()

        class _R:
            returncode = 0
            stdout = "ok"
            stderr = ""

        return _R()

    wrapper = WgetWrapper(runner=fake_runner, signer=lambda _payload: "sig-ed25519")  # type: ignore[arg-type]
    telemetry = TelemetryIngestionPipeline(batch_size=1)
    result = wrapper.execute(
        WgetRequest(target="http://127.0.0.1", command="http://127.0.0.1 -O /tmp/out"),
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
    assert event.event_type == "wget_session_completed"
    assert event.attributes["payload_signature_algorithm"] == "Ed25519"
    assert event.attributes["execution_fingerprint"] == result.execution_fingerprint


def test_execute_raises_on_failure() -> None:
    def fake_runner(command: list[str], _timeout: float):
        if "--version" in command or "-V" in command or "--help" in command:

            class _V:
                returncode = 0
                stdout = "GNU Wget 1.21.4 built on linux-gnu."
                stderr = ""

            return _V()

        class _R:
            returncode = 1
            stdout = ""
            stderr = "unable to resolve host"

        return _R()

    wrapper = WgetWrapper(runner=fake_runner, signer=lambda _payload: "sig")  # type: ignore[arg-type]
    with pytest.raises(WgetExecutionError, match="unable to resolve host"):
        wrapper.execute(
            WgetRequest(target="bad.invalid", command="http://bad.invalid -O /tmp/out"),
            tenant_id="tenant-a",
            operator_id="operator-a",
        )


def test_send_to_orchestrator_supports_ingest_payload_compatible_sink() -> None:
    class BrokenTelemetry:
        def ingest_payload(self, payload: dict[str, Any]) -> object:
            return payload

    wrapper = WgetWrapper(
        signer=lambda _payload: "sig",
        runner=lambda _cmd, _timeout: type(
            "R", (), {"returncode": 0, "stdout": "GNU Wget 1.21.4 built on linux-gnu.", "stderr": ""}
        )(),  # type: ignore[arg-type]
    )
    result = wrapper.execute(
        WgetRequest(target="http://127.0.0.1", extra_args=["--dry-run"]),
        tenant_id="tenant-a",
        operator_id="operator-a",
    )
    event = wrapper.send_to_orchestrator(  # type: ignore[arg-type]
        result,
        telemetry=BrokenTelemetry(),
        tenant_id="tenant-a",
        operator_id="operator-a",
    )
    assert event["event_type"] == "wget_session_completed"
