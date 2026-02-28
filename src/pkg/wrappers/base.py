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

"""Standardized base contracts for wrapper SDK integrations."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from pkg.orchestrator.execution_fingerprint import (
    ExecutionFingerprintInput,
    generate_execution_fingerprint,
)
from pkg.orchestrator.telemetry_ingestion import TelemetryEvent, TelemetryIngestionPipeline
from pkg.specs.validation_sdk import validate_telemetry_extension_v1
from pkg.telemetry.sdk import build_internal_telemetry_event


class WrapperContractError(RuntimeError):
    """Raised when standardized wrapper contract checks fail."""


@dataclass(slots=True, frozen=True)
class WrapperCommandResult:
    """Minimal command execution result for wrapper runners."""

    returncode: int
    stdout: str
    stderr: str


Runner = Callable[[list[str], float], WrapperCommandResult]
Signer = Callable[[bytes], str]


def default_command_runner(command: list[str], timeout_seconds: float) -> WrapperCommandResult:
    """Run command with subprocess and return normalized process output."""
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        check=False,
    )
    return WrapperCommandResult(
        returncode=completed.returncode,
        stdout=completed.stdout or "",
        stderr=completed.stderr or "",
    )


def canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    """Return canonical payload bytes for deterministic hashing/signing."""
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


def _default_ed25519_signer(
    payload: bytes,
    *,
    key_path: str,
) -> str:
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    except ImportError as exc:
        raise WrapperContractError(
            "cryptography dependency is required for Ed25519 wrapper signing"
        ) from exc

    try:
        key_bytes = Path(key_path).read_bytes()
    except OSError as exc:
        raise WrapperContractError(f"unable to read signing key: {key_path}") from exc

    private_key: Any
    if len(key_bytes) == 32:
        private_key = Ed25519PrivateKey.from_private_bytes(key_bytes)
    else:
        try:
            private_key = serialization.load_pem_private_key(
                key_bytes,
                password=None,
            )
        except ValueError:
            private_key = serialization.load_ssh_private_key(
                key_bytes,
                password=None,
            )
    signature = private_key.sign(payload)
    return base64.b64encode(signature).decode("utf-8")


class BaseWrapper:
    """Reusable wrapper contract helper for telemetry-safe tool integrations."""

    def __init__(
        self,
        *,
        tool_name: str,
        tool_binary: str,
        timeout_seconds: float = 20.0,
        runner: Runner | None = None,
        signer: Signer | None = None,
        signing_key_env: str = "SPECTRASTRIKE_WRAPPER_SIGNING_KEY_PATH",
    ) -> None:
        self._tool_name = tool_name
        self._tool_binary = tool_binary
        self._timeout_seconds = timeout_seconds
        self._runner = runner or default_command_runner
        self._signing_key_env = signing_key_env
        self._signer = signer
        self._version_cache: str | None = None

    def detect_tool_version(self, detection_args: list[list[str]]) -> str:
        """Detect and cache tool version from command output."""
        if self._version_cache:
            return self._version_cache
        for args in detection_args:
            command = [self._tool_binary, *args]
            try:
                result = self._runner(command, self._timeout_seconds)
            except Exception:
                continue
            text = f"{result.stdout}\n{result.stderr}".strip()
            parsed = self._parse_version_from_text(text)
            if parsed:
                self._version_cache = parsed
                return parsed
        self._version_cache = "unknown"
        return self._version_cache

    @staticmethod
    def _parse_version_from_text(text: str) -> str | None:
        pattern = re.compile(r"(?:impacket\s+)?v?(\d+\.\d+(?:\.\d+)*)", re.I)
        match = pattern.search(text)
        if match:
            return match.group(1)
        cleaned = text.splitlines()[0].strip() if text.strip() else ""
        return cleaned or None

    def _tool_sha256(self) -> str:
        binary_path = Path(self._tool_binary)
        if binary_path.exists() and binary_path.is_file():
            data = binary_path.read_bytes()
            return hashlib.sha256(data).hexdigest()
        return hashlib.sha256(self._tool_binary.encode("utf-8")).hexdigest()

    @staticmethod
    def _hash_text(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def build_execution_context(
        self,
        *,
        command: list[str],
        tenant_id: str,
        operator_id: str,
        target: str,
        policy_decision_hash: str,
        version: str,
    ) -> dict[str, str]:
        """Build standardized execution fingerprint + attestation fields."""
        timestamp = datetime.now(UTC).isoformat()
        command_json = json.dumps(command, ensure_ascii=True)
        manifest_hash = self._hash_text(
            f"{self._tool_name}|{target}|{command_json}|{version}"
        )
        attestation_hash = self._hash_text(
            f"{self._tool_name}|{version}|{tenant_id}|{operator_id}|{target}|{command_json}"
        )
        tool_hash = self._tool_sha256()
        fingerprint = generate_execution_fingerprint(
            ExecutionFingerprintInput(
                manifest_hash=manifest_hash,
                tool_hash=tool_hash,
                operator_id=operator_id,
                tenant_id=tenant_id,
                policy_decision_hash=policy_decision_hash,
                attestation_measurement_hash=attestation_hash,
                timestamp=timestamp,
            )
        )
        return {
            "timestamp": timestamp,
            "manifest_hash": manifest_hash,
            "tool_sha256": tool_hash,
            "attestation_measurement_hash": attestation_hash,
            "execution_fingerprint": fingerprint,
        }

    def sign_payload(self, payload: dict[str, Any]) -> str:
        """Sign canonical payload bytes using Ed25519 only."""
        canonical = canonical_json_bytes(payload)
        if self._signer is not None:
            return self._signer(canonical)

        key_path = os.getenv(self._signing_key_env, "").strip()
        if not key_path:
            raise WrapperContractError(
                f"{self._signing_key_env} is required for wrapper payload signing"
            )
        return _default_ed25519_signer(canonical, key_path=key_path)

    def emit_validated_telemetry(
        self,
        *,
        telemetry: TelemetryIngestionPipeline,
        event_type: str,
        actor: str,
        status: str,
        target: str,
        tenant_id: str,
        attributes: dict[str, Any],
    ) -> TelemetryEvent:
        """Build, validate, and ingest canonical wrapper telemetry payload."""
        payload = build_internal_telemetry_event(
            event_type=event_type,
            actor=actor,
            target=target,
            status=status,
            tenant_id=tenant_id,
            attributes=attributes,
        )
        validation = validate_telemetry_extension_v1(payload)
        if not validation.ok:
            raise WrapperContractError(
                "telemetry schema validation failed: " + "; ".join(validation.errors)
            )
        return telemetry.ingest_payload(payload)
