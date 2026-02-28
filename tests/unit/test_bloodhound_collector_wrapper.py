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

"""Unit tests for BloodHound collector wrapper standardized SDK contract."""

from __future__ import annotations

import base64
from typing import Any

import pytest

from pkg.orchestrator.telemetry_ingestion import TelemetryIngestionPipeline
from pkg.wrappers.bloodhound_collector import (
    BloodhoundCollectorError,
    BloodhoundCollectorRequest,
    BloodhoundCollectorWrapper,
)


def test_build_command_includes_identity_and_auth_flags() -> None:
    wrapper = BloodhoundCollectorWrapper(
        binary="bloodhound-python",
        signer=lambda _payload: "sig",
    )
    request = BloodhoundCollectorRequest(
        target="10.0.0.64",
        username="administrator",
        domain="ACME.LOCAL",
        password="pass123",
        command="-c All",
        extra_args=["--zip"],
    )

    command = wrapper.build_command(request)

    assert command[0] == "bloodhound-python"
    assert "-ns" in command and "10.0.0.64" in command
    assert "-u" in command and "administrator" in command
    assert "-d" in command and "ACME.LOCAL" in command
    assert "-p" in command and "pass123" in command
    assert "--zip" in command


def test_detect_version_parses_banner() -> None:
    def fake_runner(command: list[str], _timeout: float):
        _ = command

        class _R:
            returncode = 0
            stdout = "bloodhound-python 1.8.0"
            stderr = ""

        return _R()

    wrapper = BloodhoundCollectorWrapper(
        runner=fake_runner,  # type: ignore[arg-type]
        signer=lambda _payload: "sig",
    )
    assert wrapper.detect_version() == "1.8.0"


def test_execute_builds_fingerprint_attestation_and_signature() -> None:
    def fake_runner(command: list[str], _timeout: float):
        if "-h" in command or "--version" in command:

            class _V:
                returncode = 0
                stdout = "bloodhound-python 1.8.0"
                stderr = ""

            return _V()

        class _R:
            returncode = 0
            stdout = "Done in 2M 5S"
            stderr = ""

        return _R()

    def fake_signer(payload: bytes) -> str:
        return base64.b64encode(payload).decode("utf-8")

    wrapper = BloodhoundCollectorWrapper(
        runner=fake_runner,  # type: ignore[arg-type]
        signer=fake_signer,
    )
    result = wrapper.execute(
        BloodhoundCollectorRequest(
            target="10.10.10.30",
            username="administrator",
            password="secret",
            command="-c All",
        ),
        tenant_id="tenant-a",
        operator_id="operator-1",
    )

    assert result.status == "success"
    assert result.return_code == 0
    assert len(result.execution_fingerprint) == 64
    assert len(result.attestation_measurement_hash) == 64
    assert result.payload_signature
    assert result.payload_signature_algorithm == "Ed25519"


def test_send_to_orchestrator_emits_validated_payload() -> None:
    def fake_runner(command: list[str], _timeout: float):
        if "-h" in command or "--version" in command:

            class _V:
                returncode = 0
                stdout = "bloodhound-python 1.8.0"
                stderr = ""

            return _V()

        class _R:
            returncode = 0
            stdout = "ok"
            stderr = ""

        return _R()

    wrapper = BloodhoundCollectorWrapper(
        runner=fake_runner,  # type: ignore[arg-type]
        signer=lambda _payload: "sig-ed25519",
    )
    telemetry = TelemetryIngestionPipeline(batch_size=1)
    result = wrapper.execute(
        BloodhoundCollectorRequest(
            target="10.10.10.31",
            username="operator",
            no_pass=True,
            command="-c Session",
        ),
        tenant_id="tenant-a",
        operator_id="op-a",
    )
    event = wrapper.send_to_orchestrator(
        result,
        telemetry=telemetry,
        tenant_id="tenant-a",
        operator_id="op-a",
        actor="qa-bot",
    )

    assert event.event_type == "bloodhound_collector_completed"
    assert event.actor == "qa-bot"
    assert event.attributes["payload_signature_algorithm"] == "Ed25519"
    assert event.attributes["execution_fingerprint"] == result.execution_fingerprint


def test_execute_raises_on_non_zero_status() -> None:
    def fake_runner(command: list[str], _timeout: float):
        if "--version" in command or "-h" in command:

            class _V:
                returncode = 0
                stdout = "bloodhound-python 1.8.0"
                stderr = ""

            return _V()

        class _R:
            returncode = 1
            stdout = ""
            stderr = "LDAP bind failed"

        return _R()

    wrapper = BloodhoundCollectorWrapper(
        runner=fake_runner,  # type: ignore[arg-type]
        signer=lambda _payload: "sig",
    )
    with pytest.raises(BloodhoundCollectorError, match="LDAP bind failed"):
        wrapper.execute(
            BloodhoundCollectorRequest(
                target="10.10.10.1",
                username="administrator",
                password="x",
                command="-c All",
            ),
            tenant_id="tenant-a",
            operator_id="operator-a",
        )


def test_request_requires_auth_mode() -> None:
    with pytest.raises(ValueError, match="one auth mode is required"):
        BloodhoundCollectorRequest(
            target="10.10.10.1",
            username="administrator",
            command="-c All",
        )


def test_send_to_orchestrator_supports_ingest_payload_compatible_sink() -> None:
    class BrokenTelemetry:
        def ingest_payload(self, payload: dict[str, Any]) -> object:
            return payload

    wrapper = BloodhoundCollectorWrapper(
        signer=lambda _payload: "sig",
        runner=lambda _cmd, _timeout: type(
            "R", (), {"returncode": 0, "stdout": "bloodhound-python 1.8.0", "stderr": ""}
        )(),  # type: ignore[arg-type]
    )
    result = wrapper.execute(
        BloodhoundCollectorRequest(
            target="10.10.10.12",
            username="administrator",
            no_pass=True,
            extra_args=["--dry-run"],
        ),
        tenant_id="tenant-a",
        operator_id="operator-a",
    )
    event = wrapper.send_to_orchestrator(  # type: ignore[arg-type]
        result,
        telemetry=BrokenTelemetry(),
        tenant_id="tenant-a",
        operator_id="operator-a",
    )
    assert event["event_type"] == "bloodhound_collector_completed"
