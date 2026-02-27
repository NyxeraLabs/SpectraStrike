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
from pkg.runner.attestation import (
    EphemeralKeyDeriver,
    MutualAttestationService,
    TPMIdentityProvider,
)
from pkg.runner.cloudevents import CloudEventEnvelope, map_execution_to_cloudevent
from pkg.runner.firecracker import (
    FirecrackerIsolationError,
    FirecrackerMicroVMProfile,
    FirecrackerMicroVMRunner,
    RuntimeAttestationReport,
)
from pkg.runner.jws_verify import RunnerJWSVerifier
from pkg.runner.network_policy import CiliumPolicyManager, RunnerNetworkPolicy


class RunnerExecutionError(RuntimeError):
    """Raised when runner retrieval/verification/execution fails."""


@dataclass(slots=True, frozen=True)
class RunnerSandboxProfile:
    """Sandbox profile abstraction: gVisor preferred, AppArmor fallback."""

    backend: str = "docker"
    runtime: str = "runsc"
    apparmor_profile: str = "spectrastrike-default"
    network_mode: str = "none"
    firecracker_profile: FirecrackerMicroVMProfile | None = None


@dataclass(slots=True)
class RunnerExecutionResult:
    """Execution outcome and mapped CloudEvent payload."""

    exit_code: int
    stdout: str
    stderr: str
    event: CloudEventEnvelope
    attestation_report: RuntimeAttestationReport | None = None


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
        policy_manager: CiliumPolicyManager | None = None,
        firecracker_runner: FirecrackerMicroVMRunner | None = None,
        tpm_identity_provider: TPMIdentityProvider | None = None,
        key_deriver: EphemeralKeyDeriver | None = None,
        mutual_attestation_service: MutualAttestationService | None = None,
    ) -> None:
        self._armory = armory
        self._jws_verifier = jws_verifier or RunnerJWSVerifier()
        self._sandbox = sandbox or RunnerSandboxProfile()
        self._command_runner = command_runner or self._default_command_runner
        self._policy_manager = policy_manager
        self._firecracker_runner = firecracker_runner or FirecrackerMicroVMRunner(
            profile=self._sandbox.firecracker_profile
            or FirecrackerMicroVMProfile(launch_mode="simulate")
        )
        self._tpm_identity_provider = tpm_identity_provider or TPMIdentityProvider(
            mode="simulate"
        )
        self._key_deriver = key_deriver or EphemeralKeyDeriver()
        self._mutual_attestation_service = (
            mutual_attestation_service or MutualAttestationService()
        )

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
        if self._sandbox.backend == "firecracker":
            return self._firecracker_runner.build_microvm_command(
                manifest=manifest, tool=tool
            )
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
        attestation_report: RuntimeAttestationReport | None = None
        execution_metadata: dict[str, object] | None = None
        if self._sandbox.backend == "firecracker":
            if self._firecracker_runner.simulate_breakout_attempt(command):
                raise RunnerExecutionError("microvm breakout attempt detected")
            try:
                isolation_checks = (
                    self._firecracker_runner.verify_hardware_isolation_boundary()
                )
            except FirecrackerIsolationError as exc:
                raise RunnerExecutionError(str(exc)) from exc
            execution_fingerprint = manifest.deterministic_hash()
            tpm_identity = self._tpm_identity_provider.issue_identity_evidence(
                quote_nonce=manifest.nonce,
                tenant_id=manifest.task_context.tenant_id,
                operator_id=manifest.task_context.operator_id,
            )
            ephemeral_key = self._key_deriver.derive_execution_key(
                execution_fingerprint=execution_fingerprint,
                tenant_id=manifest.task_context.tenant_id,
                operator_id=manifest.task_context.operator_id,
            )
            mutual_attestation = self._mutual_attestation_service.attest(
                quote_nonce=manifest.nonce,
                tenant_id=manifest.task_context.tenant_id,
                operator_id=manifest.task_context.operator_id,
                tpm_evidence=tpm_identity,
                ephemeral_key=ephemeral_key,
            )
            if not mutual_attestation.approved:
                raise RunnerExecutionError(
                    f"runner-control-plane mutual attestation failed: {mutual_attestation.reason}"
                )
            attestation_report = self._firecracker_runner.build_runtime_attestation_report(
                manifest=manifest,
                tool=self.resolve_signed_tool(manifest),
                execution_command=command,
                isolation_checks=isolation_checks,
            )
            execution_metadata = {
                "runtime": "firecracker",
                "attestation": attestation_report.to_dict(),
                "tpm_identity": tpm_identity.to_dict(),
                "ephemeral_key": ephemeral_key.to_dict(),
                "mutual_attestation": mutual_attestation.to_dict(),
            }

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
            execution_metadata=execution_metadata,
        )
        return RunnerExecutionResult(
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            event=event,
            attestation_report=attestation_report,
        )

    def apply_dynamic_network_policy(
        self, *, manifest: ExecutionManifest
    ) -> RunnerNetworkPolicy:
        """Apply per-task dynamic Cilium policy for runner isolation."""
        if self._policy_manager is None:
            raise RunnerExecutionError("dynamic network policy manager is not configured")
        return self._policy_manager.apply_policy(
            task_id=manifest.task_context.task_id,
            tenant_id=manifest.task_context.tenant_id,
            target_urn=manifest.target_urn,
        )

    def remove_dynamic_network_policy(self, policy: RunnerNetworkPolicy) -> None:
        """Remove one previously applied dynamic Cilium policy."""
        if self._policy_manager is None:
            raise RunnerExecutionError("dynamic network policy manager is not configured")
        self._policy_manager.remove_policy(policy)

    @staticmethod
    def _default_command_runner(command: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(command, text=True, capture_output=True, check=False)
