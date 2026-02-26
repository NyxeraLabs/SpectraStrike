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

import subprocess
from pathlib import Path

import pytest

from pkg.armory.service import ArmoryService
from pkg.orchestrator.manifest import ExecutionManifest, ExecutionTaskContext
from pkg.runner.network_policy import CiliumPolicyManager
from pkg.runner.universal import RunnerExecutionError, UniversalEdgeRunner


def _manifest(tool_sha256: str) -> ExecutionManifest:
    return ExecutionManifest(
        task_context=ExecutionTaskContext(
            task_id="task-s12-001",
            tenant_id="tenant-a",
            operator_id="operator-a",
            source="ui-admin",
            action="execute",
        ),
        target_urn="urn:target:ip:10.10.10.10",
        tool_sha256=tool_sha256,
        parameters={"mode": "safe"},
    )


def test_resolve_signed_tool_requires_authorized_digest(tmp_path: Path) -> None:
    armory = ArmoryService(registry_path=str(tmp_path / "armory.json"))
    ingested = armory.ingest_tool(
        tool_name="nmap",
        image_ref="registry.internal/security/nmap:1.0.0",
        artifact=b"tool-bytes",
    )
    manifest = _manifest(ingested.tool_sha256)
    runner = UniversalEdgeRunner(armory=armory)

    with pytest.raises(RunnerExecutionError):
        runner.resolve_signed_tool(manifest)


def test_build_and_execute_maps_cloudevent_contract(tmp_path: Path) -> None:
    armory = ArmoryService(registry_path=str(tmp_path / "armory.json"))
    ingested = armory.ingest_tool(
        tool_name="nmap",
        image_ref="registry.internal/security/nmap:1.0.0",
        artifact=b"tool-bytes",
    )
    armory.approve_tool(tool_sha256=ingested.tool_sha256, approver="secops")
    manifest = _manifest(ingested.tool_sha256)

    def fake_runner(command: list[str]) -> subprocess.CompletedProcess[str]:
        assert "--runtime=runsc" in command
        return subprocess.CompletedProcess(command, 0, "ok", "")

    runner = UniversalEdgeRunner(armory=armory, command_runner=fake_runner)
    tool = runner.resolve_signed_tool(manifest)
    command = runner.build_sandbox_command(tool=tool, manifest=manifest)
    result = runner.execute(
        manifest=manifest, manifest_jws="abc.def.sig", command=command
    )

    assert result.exit_code == 0
    payload = result.event.to_dict()["data"]
    assert payload["stdout"] == "ok"
    assert payload["stderr"] == ""
    assert payload["status"] == "success"


def test_runner_applies_and_removes_dynamic_network_policy(tmp_path: Path) -> None:
    armory = ArmoryService(registry_path=str(tmp_path / "armory.json"))
    ingested = armory.ingest_tool(
        tool_name="nmap",
        image_ref="registry.internal/security/nmap:1.0.0",
        artifact=b"tool-bytes",
    )
    manifest = _manifest(ingested.tool_sha256)
    calls: list[tuple[list[str], str | None]] = []

    def fake_policy_runner(
        command: list[str], stdin_payload: str | None
    ) -> subprocess.CompletedProcess[str]:
        calls.append((command, stdin_payload))
        return subprocess.CompletedProcess(command, 0, "", "")

    policy_manager = CiliumPolicyManager(command_runner=fake_policy_runner)
    runner = UniversalEdgeRunner(armory=armory, policy_manager=policy_manager)
    policy = runner.apply_dynamic_network_policy(manifest=manifest)
    runner.remove_dynamic_network_policy(policy)

    assert calls[0][0] == ["kubectl", "apply", "-f", "-"]
    assert '"cidr": "10.10.10.10/32"' in (calls[0][1] or "")
    assert calls[1][0][0:3] == ["kubectl", "delete", "ciliumnetworkpolicy"]
