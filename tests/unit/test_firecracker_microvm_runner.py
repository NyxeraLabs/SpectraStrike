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

from __future__ import annotations

from pathlib import Path

from pkg.armory.service import ArmoryService
from pkg.orchestrator.manifest import ExecutionManifest, ExecutionTaskContext
from pkg.runner.firecracker import FirecrackerMicroVMProfile, FirecrackerMicroVMRunner


def _manifest(tool_sha256: str) -> ExecutionManifest:
    return ExecutionManifest(
        task_context=ExecutionTaskContext(
            task_id="task-s34-001",
            tenant_id="tenant-a",
            operator_id="op-001",
            source="ui-admin",
            action="execute",
        ),
        target_urn="urn:target:ip:10.10.10.10",
        tool_sha256=tool_sha256,
        parameters={"mode": "safe"},
    )


def test_build_microvm_command_simulation_mode(tmp_path: Path) -> None:
    runner = FirecrackerMicroVMRunner(profile=FirecrackerMicroVMProfile(launch_mode="simulate"))
    armory = ArmoryService(registry_path=str(tmp_path / "armory.json"))
    ingested = armory.ingest_tool(
        tool_name="nmap",
        image_ref="registry.internal/security/nmap:1.0.0",
        artifact=b"tool-bytes",
    )
    manifest = _manifest(ingested.tool_sha256)

    command = runner.build_microvm_command(manifest=manifest, tool=ingested)

    assert command[0] == "echo"
    assert "firecracker_simulated" in command[1]


def test_verify_hardware_isolation_boundary_in_simulation_mode() -> None:
    runner = FirecrackerMicroVMRunner(profile=FirecrackerMicroVMProfile(launch_mode="simulate"))

    checks = runner.verify_hardware_isolation_boundary()

    assert checks["seccomp_hardened"] is True
    assert checks["jailer_enabled"] is True


def test_build_runtime_attestation_report_is_deterministic_shape(tmp_path: Path) -> None:
    armory = ArmoryService(registry_path=str(tmp_path / "armory.json"))
    ingested = armory.ingest_tool(
        tool_name="nmap",
        image_ref="registry.internal/security/nmap:1.0.0",
        artifact=b"tool-bytes",
    )
    manifest = _manifest(ingested.tool_sha256)
    runner = FirecrackerMicroVMRunner(profile=FirecrackerMicroVMProfile(launch_mode="simulate"))

    report = runner.build_runtime_attestation_report(
        manifest=manifest,
        tool=ingested,
        execution_command=["echo", "firecracker_simulated"],
        isolation_checks={"seccomp_hardened": True, "jailer_enabled": True},
    )

    payload = report.to_dict()
    assert payload["runtime"] == "firecracker"
    assert payload["boot_mode"] == "snapshot-resume"
    assert len(str(payload["measurement_hash"])) == 64


def test_simulate_breakout_attempt_detection() -> None:
    runner = FirecrackerMicroVMRunner(profile=FirecrackerMicroVMProfile(launch_mode="simulate"))

    assert runner.simulate_breakout_attempt(["docker", "run", "--privileged", "busybox"]) is True
    assert runner.simulate_breakout_attempt(["echo", "safe"]) is False
