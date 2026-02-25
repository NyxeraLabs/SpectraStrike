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

"""Universal Edge Runner for signed BYOT manifest execution."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import Callable

from pkg.armory.service import ArmoryService, ArmoryTool
from pkg.orchestrator.manifest import ExecutionManifest
from pkg.runner.cloudevents import CloudEventEnvelope, map_execution_to_cloudevent
from pkg.runner.jws_verify import RunnerJWSVerifier


class RunnerExecutionError(RuntimeError):
    """Raised when runner retrieval/verification/execution fails."""


@dataclass(slots=True, frozen=True)
class RunnerSandboxProfile:
    """Sandbox profile abstraction: gVisor preferred, AppArmor fallback."""

    runtime: str = "runsc"
    apparmor_profile: str = "spectrastrike-default"
    network_mode: str = "none"


@dataclass(slots=True)
class RunnerExecutionResult:
    """Execution outcome and mapped CloudEvent payload."""

    exit_code: int
    stdout: str
    stderr: str
    event: CloudEventEnvelope


class UniversalEdgeRunner:
    """Signed-manifest BYOT runner with strict digest and sandbox controls."""

    def __init__(
        self,
        *,
        armory: ArmoryService,
        jws_verifier: RunnerJWSVerifier | None = None,
        sandbox: RunnerSandboxProfile | None = None,
        command_runner: (
            Callable[[list[str]], subprocess.CompletedProcess[str]] | None
        ) = None,
    ) -> None:
        self._armory = armory
        self._jws_verifier = jws_verifier or RunnerJWSVerifier()
        self._sandbox = sandbox or RunnerSandboxProfile()
        self._command_runner = command_runner or self._default_command_runner

    def verify_manifest_jws(
        self,
        *,
        compact_jws: str,
        hmac_secret: str | None = None,
        public_key_pem: str | None = None,
    ) -> dict[str, object]:
        """Verify manifest JWS before execution approval."""
        payload = self._jws_verifier.verify(
            compact_jws=compact_jws,
            hmac_secret=hmac_secret,
            public_key_pem=public_key_pem,
        )
        return payload

    def resolve_signed_tool(self, manifest: ExecutionManifest) -> ArmoryTool:
        """Fetch authorized signed tool and enforce exact digest matching."""
        try:
            tool = self._armory.get_authorized_tool(tool_sha256=manifest.tool_sha256)
        except KeyError as exc:
            raise RunnerExecutionError(
                "authorized tool digest not found in Armory"
            ) from exc

        if tool.tool_sha256 != manifest.tool_sha256:
            raise RunnerExecutionError("tool digest mismatch with signed manifest")
        return tool

    def build_sandbox_command(
        self,
        *,
        tool: ArmoryTool,
        manifest: ExecutionManifest,
    ) -> list[str]:
        """Build strict container execution command with isolation controls."""
        return [
            "docker",
            "run",
            "--rm",
            "--read-only",
            "--cap-drop=ALL",
            f"--runtime={self._sandbox.runtime}",
            f"--security-opt=apparmor={self._sandbox.apparmor_profile}",
            f"--network={self._sandbox.network_mode}",
            "-e",
            f"SPECTRA_TASK_ID={manifest.task_context.task_id}",
            "-e",
            f"SPECTRA_TARGET_URN={manifest.target_urn}",
            tool.image_ref,
        ]

    def execute(
        self,
        *,
        manifest: ExecutionManifest,
        manifest_jws: str,
        command: list[str],
    ) -> RunnerExecutionResult:
        """Execute isolated command and map output contract to CloudEvents."""
        completed = self._command_runner(command)
        event = map_execution_to_cloudevent(
            task_id=manifest.task_context.task_id,
            tenant_id=manifest.task_context.tenant_id,
            tool_sha256=manifest.tool_sha256,
            target_urn=manifest.target_urn,
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            manifest_jws=manifest_jws,
        )
        return RunnerExecutionResult(
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            event=event,
        )

    @staticmethod
    def _default_command_runner(command: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(command, text=True, capture_output=True, check=False)
