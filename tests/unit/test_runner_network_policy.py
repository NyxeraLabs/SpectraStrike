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

from __future__ import annotations

import subprocess

import pytest

from pkg.runner.network_policy import (
    CiliumPolicyManager,
    RunnerNetworkPolicy,
    RunnerNetworkPolicyError,
)


def test_build_policy_document_contains_dynamic_task_and_tenant_labels() -> None:
    manager = CiliumPolicyManager(namespace="spectra")

    doc = manager.build_policy_document(task_id="task-123", tenant_id="tenant-a")

    assert doc["kind"] == "CiliumNetworkPolicy"
    assert doc["metadata"]["namespace"] == "spectra"
    selector = doc["spec"]["endpointSelector"]["matchLabels"]
    assert selector["spectrastrike.io/task-id"] == "task-123"
    assert selector["spectrastrike.io/tenant-id"] == "tenant-a"


def test_apply_policy_runs_kubectl_apply_with_payload() -> None:
    calls: list[tuple[list[str], str | None]] = []

    def fake_runner(
        command: list[str], stdin_payload: str | None
    ) -> subprocess.CompletedProcess[str]:
        calls.append((command, stdin_payload))
        return subprocess.CompletedProcess(command, 0, "", "")

    manager = CiliumPolicyManager(command_runner=fake_runner)
    policy = manager.apply_policy(task_id="task-1", tenant_id="tenant-a")

    assert isinstance(policy, RunnerNetworkPolicy)
    assert calls[0][0] == ["kubectl", "apply", "-f", "-"]
    assert calls[0][1] is not None
    assert '"kind": "CiliumNetworkPolicy"' in (calls[0][1] or "")


def test_remove_policy_runs_kubectl_delete() -> None:
    calls: list[tuple[list[str], str | None]] = []

    def fake_runner(
        command: list[str], stdin_payload: str | None
    ) -> subprocess.CompletedProcess[str]:
        calls.append((command, stdin_payload))
        return subprocess.CompletedProcess(command, 0, "", "")

    manager = CiliumPolicyManager(command_runner=fake_runner)
    manager.remove_policy(
        RunnerNetworkPolicy(
            name="ss-runner-tenant-a-task-1",
            namespace="default",
            task_id="task-1",
            tenant_id="tenant-a",
        )
    )

    assert calls[0][0][0:3] == ["kubectl", "delete", "ciliumnetworkpolicy"]
    assert "--ignore-not-found=true" in calls[0][0]


def test_apply_policy_raises_on_kubectl_error() -> None:
    def fake_runner(
        command: list[str], stdin_payload: str | None
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 1, "", "error")

    manager = CiliumPolicyManager(command_runner=fake_runner)
    with pytest.raises(RunnerNetworkPolicyError):
        manager.apply_policy(task_id="task-1", tenant_id="tenant-a")
