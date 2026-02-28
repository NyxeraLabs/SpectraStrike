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

"""Unit tests for Impacket secretsdump wrapper standardized SDK contract."""

from __future__ import annotations

import base64
from typing import Any

import pytest

from pkg.orchestrator.telemetry_ingestion import TelemetryIngestionPipeline
from pkg.wrappers.impacket_secretsdump import (
    ImpacketSecretsdumpError,
    ImpacketSecretsdumpRequest,
    ImpacketSecretsdumpWrapper,
)


def test_build_command_includes_identity_and_auth_flags() -> None:
    wrapper = ImpacketSecretsdumpWrapper(
        binary="secretsdump.py",
        signer=lambda _payload: "sig",
    )
    request = ImpacketSecretsdumpRequest(
        target="10.0.0.62",
        username="administrator",
        domain="ACME",
        password="pass123",
        command="-just-dc-user administrator",
        hashes="aad3b435b51404eeaad3b435b51404ee:11111111111111111111111111111111",
        extra_args=["-codec", "utf-8"],
    )

    command = wrapper.build_command(request)

    assert command[0] == "secretsdump.py"
    assert command[1].startswith("ACME/administrator:pass123@10.0.0.62")
    assert "-just-dc-user" in command
    assert "-hashes" in command
    assert "-codec" in command


def test_detect_version_parses_impacket_banner() -> None:
    def fake_runner(command: list[str], _timeout: float):
        _ = command

        class _R:
            returncode = 0
            stdout = "Impacket v0.13.0 - Copyright 2026"
            stderr = ""

        return _R()

    wrapper = ImpacketSecretsdumpWrapper(
        runner=fake_runner,  # type: ignore[arg-type]
        signer=lambda _payload: "sig",
    )

    assert wrapper.detect_version() == "0.13.0"


def test_execute_builds_fingerprint_attestation_and_signature() -> None:
    def fake_runner(command: list[str], _timeout: float):
        if "-h" in command or "--version" in command or "-version" in command:

            class _V:
                returncode = 0
                stdout = "Impacket v0.13.0"
                stderr = ""

            return _V()

        class _R:
            returncode = 0
            stdout = "administrator:500:aad3..."
            stderr = ""

        return _R()

    def fake_signer(payload: bytes) -> str:
        return base64.b64encode(payload).decode("utf-8")

    wrapper = ImpacketSecretsdumpWrapper(
        runner=fake_runner,  # type: ignore[arg-type]
        signer=fake_signer,
    )
    request = ImpacketSecretsdumpRequest(
        target="10.10.10.22",
        username="administrator",
        password="secret",
        command="-just-dc-user administrator",
    )

    result = wrapper.execute(
        request,
        tenant_id="tenant-a",
        operator_id="operator-1",
    )

    assert result.status == "success"
    assert result.return_code == 0
    assert result.execution_fingerprint
    assert len(result.execution_fingerprint) == 64
    assert len(result.attestation_measurement_hash) == 64
    assert result.payload_signature
    assert result.payload_signature_algorithm == "Ed25519"


def test_send_to_orchestrator_emits_validated_payload() -> None:
    def fake_runner(command: list[str], _timeout: float):
        if "-h" in command or "--version" in command or "-version" in command:

            class _V:
                returncode = 0
                stdout = "Impacket v0.13.0"
                stderr = ""

            return _V()

        class _R:
            returncode = 0
            stdout = "ok"
            stderr = ""

        return _R()

    wrapper = ImpacketSecretsdumpWrapper(
        runner=fake_runner,  # type: ignore[arg-type]
        signer=lambda _payload: "sig-ed25519",
    )
    telemetry = TelemetryIngestionPipeline(batch_size=1)
    request = ImpacketSecretsdumpRequest(
        target="10.10.10.23",
        username="operator",
        no_pass=True,
        command="-just-dc-user operator",
    )
    result = wrapper.execute(
        request,
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

    assert event.event_type == "impacket_secretsdump_completed"
    assert event.actor == "qa-bot"
    assert event.attributes["payload_signature_algorithm"] == "Ed25519"
    assert event.attributes["execution_fingerprint"] == result.execution_fingerprint
    assert event.attributes["attestation_measurement_hash"] == (
        result.attestation_measurement_hash
    )


def test_execute_raises_on_non_zero_status() -> None:
    def fake_runner(command: list[str], _timeout: float):
        if "--version" in command or "-version" in command or "-h" in command:

            class _V:
                returncode = 0
                stdout = "Impacket v0.13.0"
                stderr = ""

            return _V()

        class _R:
            returncode = 1
            stdout = ""
            stderr = "SMB SessionError"

        return _R()

    wrapper = ImpacketSecretsdumpWrapper(
        runner=fake_runner,  # type: ignore[arg-type]
        signer=lambda _payload: "sig",
    )
    with pytest.raises(ImpacketSecretsdumpError, match="SMB SessionError"):
        wrapper.execute(
            ImpacketSecretsdumpRequest(
                target="10.10.10.1",
                username="administrator",
                password="x",
                command="-just-dc-user administrator",
            ),
            tenant_id="tenant-a",
            operator_id="operator-a",
        )


def test_request_requires_auth_mode() -> None:
    with pytest.raises(ValueError, match="one auth mode is required"):
        ImpacketSecretsdumpRequest(
            target="10.10.10.1",
            username="administrator",
            command="-just-dc-user administrator",
        )


def test_send_to_orchestrator_supports_ingest_payload_compatible_sink() -> None:
    class BrokenTelemetry:
        def ingest_payload(self, payload: dict[str, Any]) -> object:
            return payload

    wrapper = ImpacketSecretsdumpWrapper(
        signer=lambda _payload: "sig",
        runner=lambda _cmd, _timeout: type(
            "R", (), {"returncode": 0, "stdout": "Impacket v0.13.0", "stderr": ""}
        )(),  # type: ignore[arg-type]
    )
    result = wrapper.execute(
        ImpacketSecretsdumpRequest(
            target="10.10.10.12",
            username="administrator",
            no_pass=True,
            extra_args=["--dry-run"],
        ),
        tenant_id="tenant-a",
        operator_id="operator-a",
    )
    # type ignored here to force contract check path.
    event = wrapper.send_to_orchestrator(  # type: ignore[arg-type]
        result,
        telemetry=BrokenTelemetry(),
        tenant_id="tenant-a",
        operator_id="operator-a",
    )
    assert event["event_type"] == "impacket_secretsdump_completed"
