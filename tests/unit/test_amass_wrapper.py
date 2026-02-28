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

"""Unit tests for amass wrapper standardized SDK contract."""

from __future__ import annotations

import base64
from typing import Any

import pytest

from pkg.orchestrator.telemetry_ingestion import TelemetryIngestionPipeline
from pkg.wrappers.amass import (
    AmassExecutionError,
    AmassRequest,
    AmassWrapper,
)


def test_build_command_contains_enum_domain() -> None:
    wrapper = AmassWrapper(binary="amass", signer=lambda _payload: "sig")
    request = AmassRequest(
        target="example.com",
        command="enum -passive -d example.com",
        extra_args=["-norecursive"],
    )
    command = wrapper.build_command(request)
    assert command[0] == "amass"
    assert "enum" in command
    assert "-d" in command and "example.com" in command
    assert "-norecursive" in command


def test_detect_version_parses_banner() -> None:
    def fake_runner(command: list[str], _timeout: float):
        _ = command

        class _R:
            returncode = 0
            stdout = "amass v4.2.0"
            stderr = ""

        return _R()

    wrapper = AmassWrapper(runner=fake_runner, signer=lambda _payload: "sig")  # type: ignore[arg-type]
    assert wrapper.detect_version() == "4.2.0"


def test_execute_builds_contract_fields() -> None:
    def fake_runner(command: list[str], _timeout: float):
        if "version" in command or "-version" in command or "-h" in command:

            class _V:
                returncode = 0
                stdout = "amass v4.2.0"
                stderr = ""

            return _V()

        class _R:
            returncode = 0
            stdout = "www.example.com"
            stderr = ""

        return _R()

    def fake_signer(payload: bytes) -> str:
        return base64.b64encode(payload).decode("utf-8")

    wrapper = AmassWrapper(runner=fake_runner, signer=fake_signer)  # type: ignore[arg-type]
    result = wrapper.execute(
        AmassRequest(target="example.com", command="enum -passive -d example.com"),
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
        if "version" in command or "-version" in command or "-h" in command:

            class _V:
                returncode = 0
                stdout = "amass v4.2.0"
                stderr = ""

            return _V()

        class _R:
            returncode = 0
            stdout = "ok"
            stderr = ""

        return _R()

    wrapper = AmassWrapper(runner=fake_runner, signer=lambda _payload: "sig-ed25519")  # type: ignore[arg-type]
    telemetry = TelemetryIngestionPipeline(batch_size=1)
    result = wrapper.execute(
        AmassRequest(target="example.com", command="enum -passive -d example.com"),
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
    assert event.event_type == "amass_enum_completed"
    assert event.attributes["payload_signature_algorithm"] == "Ed25519"
    assert event.attributes["execution_fingerprint"] == result.execution_fingerprint


def test_execute_raises_on_failure() -> None:
    def fake_runner(command: list[str], _timeout: float):
        if "version" in command or "-version" in command or "-h" in command:

            class _V:
                returncode = 0
                stdout = "amass v4.2.0"
                stderr = ""

            return _V()

        class _R:
            returncode = 1
            stdout = ""
            stderr = "invalid enum options"

        return _R()

    wrapper = AmassWrapper(runner=fake_runner, signer=lambda _payload: "sig")  # type: ignore[arg-type]
    with pytest.raises(AmassExecutionError, match="invalid enum options"):
        wrapper.execute(
            AmassRequest(target="example.com", command="enum --bad-flag"),
            tenant_id="tenant-a",
            operator_id="operator-a",
        )


def test_send_to_orchestrator_supports_ingest_payload_compatible_sink() -> None:
    class BrokenTelemetry:
        def ingest_payload(self, payload: dict[str, Any]) -> object:
            return payload

    wrapper = AmassWrapper(
        signer=lambda _payload: "sig",
        runner=lambda _cmd, _timeout: type(
            "R", (), {"returncode": 0, "stdout": "amass v4.2.0", "stderr": ""}
        )(),  # type: ignore[arg-type]
    )
    result = wrapper.execute(
        AmassRequest(target="example.com", extra_args=["--dry-run"]),
        tenant_id="tenant-a",
        operator_id="operator-a",
    )
    event = wrapper.send_to_orchestrator(  # type: ignore[arg-type]
        result,
        telemetry=BrokenTelemetry(),
        tenant_id="tenant-a",
        operator_id="operator-a",
    )
    assert event["event_type"] == "amass_enum_completed"
