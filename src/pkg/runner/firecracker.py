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

"""Firecracker microVM runtime helpers for Phase 10 Sprint 34."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable

from pkg.armory.service import ArmoryTool
from pkg.orchestrator.manifest import ExecutionManifest


class FirecrackerIsolationError(RuntimeError):
    """Raised when microVM isolation preconditions are not satisfied."""


@dataclass(slots=True, frozen=True)
class FirecrackerMicroVMProfile:
    """MicroVM runtime profile for firecracker-backed execution."""

    launch_mode: str = "simulate"
    firecracker_bin: str = "firecracker"
    jailer_bin: str = "jailer"
    api_socket_dir: str = "/tmp"
    seccomp_level: int = 2
    enable_jailer: bool = True
    require_kvm: bool = False
    boot_timeout_ms: int = 1200
    snapshot_resume: bool = True

    def __post_init__(self) -> None:
        if self.launch_mode not in {"simulate", "native"}:
            raise FirecrackerIsolationError("launch_mode must be simulate or native")
        if self.seccomp_level < 2:
            raise FirecrackerIsolationError("seccomp_level must be >= 2")
        if self.boot_timeout_ms <= 0:
            raise FirecrackerIsolationError("boot_timeout_ms must be greater than zero")


@dataclass(slots=True, frozen=True)
class RuntimeAttestationReport:
    """Runtime attestation payload emitted for microVM execution."""

    runtime: str
    task_id: str
    tenant_id: str
    operator_id: str
    tool_sha256: str
    target_urn: str
    measurement_hash: str
    boot_mode: str
    isolation_checks: dict[str, bool]
    generated_at: str

    def to_dict(self) -> dict[str, object]:
        return {
            "runtime": self.runtime,
            "task_id": self.task_id,
            "tenant_id": self.tenant_id,
            "operator_id": self.operator_id,
            "tool_sha256": self.tool_sha256,
            "target_urn": self.target_urn,
            "measurement_hash": self.measurement_hash,
            "boot_mode": self.boot_mode,
            "isolation_checks": dict(self.isolation_checks),
            "generated_at": self.generated_at,
        }


class FirecrackerMicroVMRunner:
    """Build and validate firecracker microVM execution launch contracts."""

    def __init__(
        self,
        *,
        profile: FirecrackerMicroVMProfile | None = None,
        command_runner: (
            Callable[[list[str]], subprocess.CompletedProcess[str]] | None
        ) = None,
    ) -> None:
        self._profile = profile or FirecrackerMicroVMProfile()
        self._command_runner = command_runner or self._default_command_runner

    @staticmethod
    def _default_command_runner(command: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(command, text=True, capture_output=True, check=False)

    @staticmethod
    def _vm_id(task_id: str) -> str:
        normalized = re.sub(r"[^a-zA-Z0-9-]", "-", task_id).strip("-").lower()
        return (normalized or "task")[:63]

    def verify_hardware_isolation_boundary(self) -> dict[str, bool]:
        """Validate minimum hardware isolation constraints before launch."""
        firecracker_available = shutil.which(self._profile.firecracker_bin) is not None
        jailer_available = (
            shutil.which(self._profile.jailer_bin) is not None
            if self._profile.enable_jailer
            else True
        )
        kvm_available = Path("/dev/kvm").exists() if self._profile.require_kvm else True
        seccomp_hardened = self._profile.seccomp_level >= 2
        checks = {
            "firecracker_binary_available": firecracker_available,
            "jailer_binary_available": jailer_available,
            "kvm_device_available": kvm_available,
            "seccomp_hardened": seccomp_hardened,
            "jailer_enabled": self._profile.enable_jailer,
        }
        required_checks = {
            "firecracker_binary_available": firecracker_available,
            "jailer_binary_available": jailer_available,
            "kvm_device_available": kvm_available,
            "seccomp_hardened": seccomp_hardened,
        }
        if self._profile.launch_mode == "native" and not all(required_checks.values()):
            raise FirecrackerIsolationError("firecracker isolation boundary checks failed")
        if not seccomp_hardened:
            raise FirecrackerIsolationError("seccomp hardening is required")
        return checks

    def simulate_breakout_attempt(self, command: list[str]) -> bool:
        """Return True when command includes clear sandbox-breakout indicators."""
        joined = " ".join(command).lower()
        indicators = (
            "--privileged",
            "--network=host",
            "--cap-add=sys_admin",
            "--device=/dev/mem",
            "--pid=host",
        )
        return any(token in joined for token in indicators)

    def build_microvm_command(
        self,
        *,
        manifest: ExecutionManifest,
        tool: ArmoryTool,
    ) -> list[str]:
        """Build firecracker launch command (simulate/native modes)."""
        vm_id = self._vm_id(manifest.task_context.task_id)
        if self._profile.launch_mode == "simulate":
            return [
                "echo",
                f"firecracker_simulated:{vm_id}:{tool.tool_sha256[:16]}",
            ]

        socket_path = f"{self._profile.api_socket_dir.rstrip('/')}/spectra-fc-{vm_id}.sock"
        firecracker_cmd = [
            self._profile.firecracker_bin,
            "--api-sock",
            socket_path,
            "--seccomp-level",
            str(self._profile.seccomp_level),
        ]
        if self._profile.enable_jailer:
            return [
                self._profile.jailer_bin,
                "--id",
                vm_id,
                "--exec-file",
                self._profile.firecracker_bin,
                "--",
                *firecracker_cmd[1:],
            ]
        return firecracker_cmd

    def launch_microvm(
        self,
        *,
        manifest: ExecutionManifest,
        tool: ArmoryTool,
    ) -> subprocess.CompletedProcess[str]:
        """Launch one microVM instance using configured mode."""
        command = self.build_microvm_command(manifest=manifest, tool=tool)
        return self._command_runner(command)

    def build_runtime_attestation_report(
        self,
        *,
        manifest: ExecutionManifest,
        tool: ArmoryTool,
        execution_command: list[str],
        isolation_checks: dict[str, bool],
    ) -> RuntimeAttestationReport:
        """Build deterministic runtime attestation record for one execution."""
        measurement_input = json.dumps(
            {
                "task_id": manifest.task_context.task_id,
                "tenant_id": manifest.task_context.tenant_id,
                "operator_id": manifest.task_context.operator_id,
                "tool_sha256": tool.tool_sha256,
                "target_urn": manifest.target_urn,
                "execution_command": execution_command,
                "launch_mode": self._profile.launch_mode,
                "snapshot_resume": self._profile.snapshot_resume,
                "boot_timeout_ms": self._profile.boot_timeout_ms,
                "isolation_checks": isolation_checks,
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )
        measurement_hash = hashlib.sha256(measurement_input.encode("utf-8")).hexdigest()
        boot_mode = "snapshot-resume" if self._profile.snapshot_resume else "cold-boot"
        return RuntimeAttestationReport(
            runtime="firecracker",
            task_id=manifest.task_context.task_id,
            tenant_id=manifest.task_context.tenant_id,
            operator_id=manifest.task_context.operator_id,
            tool_sha256=tool.tool_sha256,
            target_urn=manifest.target_urn,
            measurement_hash=measurement_hash,
            boot_mode=boot_mode,
            isolation_checks=isolation_checks,
            generated_at=datetime.now(UTC).isoformat(),
        )
