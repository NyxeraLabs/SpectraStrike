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

"""sqlmap wrapper with standardized SDK telemetry contracts."""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass, field
from typing import Any

from pkg.orchestrator.telemetry_ingestion import TelemetryEvent, TelemetryIngestionPipeline
from pkg.wrappers.base import BaseWrapper, Runner, Signer, WrapperContractError


class SqlmapExecutionError(RuntimeError):
    """Raised when sqlmap execution fails."""


@dataclass(slots=True, frozen=True)
class SqlmapRequest:
    """sqlmap normalized request model."""

    target: str
    command: str = "-u http://127.0.0.1/vuln.php?id=1 --batch --level=1 --risk=1"
    extra_args: list[str] = field(default_factory=list)
    policy_decision_hash: str = "policy-allow-smoke"

    def __post_init__(self) -> None:
        if not self.target.strip():
            raise ValueError("target is required")
        if not self.command.strip():
            raise ValueError("command is required")
        if not self.policy_decision_hash.strip():
            raise ValueError("policy_decision_hash is required")


@dataclass(slots=True, frozen=True)
class SqlmapResult:
    """Normalized sqlmap execution output."""

    target: str
    command: str
    status: str
    output: str
    return_code: int
    tool_version: str
    execution_fingerprint: str
    attestation_measurement_hash: str
    payload_signature: str
    payload_signature_algorithm: str = "Ed25519"
    raw: dict[str, Any] = field(default_factory=dict)


class SqlmapWrapper(BaseWrapper):
    """Wrapper around sqlmap with SDK telemetry contract enforcement."""

    def __init__(
        self,
        *,
        binary: str | None = None,
        timeout_seconds: float = 30.0,
        runner: Runner | None = None,
        signer: Signer | None = None,
    ) -> None:
        self._binary = binary or os.getenv("SQLMAP_BINARY", "sqlmap")
        super().__init__(
            tool_name="sqlmap",
            tool_binary=self._binary,
            timeout_seconds=timeout_seconds,
            runner=runner,
            signer=signer,
        )

    def detect_version(self) -> str:
        """Detect sqlmap version."""
        return self.detect_tool_version([["--version"], ["-h"], ["--help"]])

    @staticmethod
    def _is_dry_run(request: SqlmapRequest) -> bool:
        return any(arg.strip().lower() == "--dry-run" for arg in request.extra_args)

    def build_command(self, request: SqlmapRequest) -> list[str]:
        """Build deterministic sqlmap command."""
        return [self._binary, *request.command.split(), *request.extra_args]

    def execute(
        self,
        request: SqlmapRequest,
        *,
        tenant_id: str,
        operator_id: str,
    ) -> SqlmapResult:
        """Execute sqlmap and produce signed normalized output contract."""
        version = self.detect_version()
        command = self.build_command(request)
        context = self.build_execution_context(
            command=command,
            tenant_id=tenant_id,
            operator_id=operator_id,
            target=request.target,
            policy_decision_hash=request.policy_decision_hash,
            version=version,
        )

        if self._is_dry_run(request):
            result_output = (
                f"dry-run compatible target={request.target} command={request.command}"
            )
            return_code = 0
            status = "success"
            raw_payload = {
                "mode": "dry-run",
                "started_at_epoch": int(time.time()),
                "output": result_output,
            }
        else:
            completed = self._runner(command, self._timeout_seconds)
            result_output = (completed.stdout or completed.stderr).strip()
            return_code = completed.returncode
            status = "success" if completed.returncode == 0 else "failed"
            raw_payload = {
                "mode": "live",
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            }
            if completed.returncode != 0:
                raise SqlmapExecutionError(result_output or "sqlmap command failed")

        signature_payload = {
            "tool": "sqlmap",
            "version": version,
            "target": request.target,
            "operator_id": operator_id,
            "tenant_id": tenant_id,
            "command": request.command,
            "status": status,
            "return_code": return_code,
            "execution_fingerprint": context["execution_fingerprint"],
            "attestation_measurement_hash": context["attestation_measurement_hash"],
        }
        payload_signature = self.sign_payload(signature_payload)
        return SqlmapResult(
            target=request.target,
            command=request.command,
            status=status,
            output=result_output,
            return_code=return_code,
            tool_version=version,
            execution_fingerprint=context["execution_fingerprint"],
            attestation_measurement_hash=context["attestation_measurement_hash"],
            payload_signature=payload_signature,
            raw=raw_payload,
        )

    def send_to_orchestrator(
        self,
        result: SqlmapResult,
        *,
        telemetry: TelemetryIngestionPipeline,
        tenant_id: str,
        operator_id: str,
        actor: str = "sqlmap-wrapper",
    ) -> TelemetryEvent:
        """Emit schema-validated canonical telemetry payload."""
        signature_input_hash = hashlib.sha256(
            json.dumps(
                {
                    "execution_fingerprint": result.execution_fingerprint,
                    "attestation_measurement_hash": result.attestation_measurement_hash,
                    "status": result.status,
                    "return_code": result.return_code,
                },
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            ).encode("utf-8")
        ).hexdigest()
        attributes = {
            "schema_version": "telemetry.ext.v1",
            "adapter": "sqlmap",
            "module": "scanner",
            "target": result.target,
            "command": result.command,
            "output": result.output,
            "return_code": result.return_code,
            "tool_version": result.tool_version,
            "operator_id": operator_id,
            "tenant_id": tenant_id,
            "execution_fingerprint": result.execution_fingerprint,
            "attestation_measurement_hash": result.attestation_measurement_hash,
            "payload_signature": result.payload_signature,
            "payload_signature_algorithm": result.payload_signature_algorithm,
            "signature_input_hash": signature_input_hash,
            "tool_sha256": self._tool_sha256(),
        }
        try:
            return self.emit_validated_telemetry(
                telemetry=telemetry,
                event_type="sqlmap_scan_completed",
                actor=actor,
                status=result.status,
                target="orchestrator",
                tenant_id=tenant_id,
                attributes=attributes,
            )
        except WrapperContractError as exc:
            raise SqlmapExecutionError(str(exc)) from exc
