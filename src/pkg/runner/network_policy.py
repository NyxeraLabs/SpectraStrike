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

"""Dynamic runner network fencing primitives using Cilium policies."""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from typing import Callable


class RunnerNetworkPolicyError(RuntimeError):
    """Raised when dynamic policy generation or lifecycle operations fail."""


@dataclass(slots=True, frozen=True)
class RunnerNetworkPolicy:
    """Metadata handle for one applied dynamic runner network policy."""

    name: str
    namespace: str
    task_id: str
    tenant_id: str


def _sanitize(value: str) -> str:
    lowered = value.lower()
    normalized = re.sub(r"[^a-z0-9-]", "-", lowered).strip("-")
    return normalized[:40] or "task"


class CiliumPolicyManager:
    """Build/apply/remove per-task Cilium policies for runner isolation."""

    def __init__(
        self,
        *,
        namespace: str = "default",
        command_runner: (
            Callable[[list[str], str | None], subprocess.CompletedProcess[str]] | None
        ) = None,
    ) -> None:
        self._namespace = namespace
        self._command_runner = command_runner or self._default_command_runner

    def build_policy_document(self, *, task_id: str, tenant_id: str) -> dict[str, object]:
        """Create deny-by-default CiliumNetworkPolicy scoped to runner task labels."""
        policy_name = self._policy_name(task_id=task_id, tenant_id=tenant_id)
        return {
            "apiVersion": "cilium.io/v2",
            "kind": "CiliumNetworkPolicy",
            "metadata": {
                "name": policy_name,
                "namespace": self._namespace,
                "labels": {
                    "app.kubernetes.io/name": "spectrastrike-runner",
                    "spectrastrike.io/task-id": task_id,
                    "spectrastrike.io/tenant-id": tenant_id,
                },
            },
            "spec": {
                "description": "Sprint 15 dynamic isolation baseline (deny-by-default)",
                "endpointSelector": {
                    "matchLabels": {
                        "spectrastrike.io/task-id": task_id,
                        "spectrastrike.io/tenant-id": tenant_id,
                    }
                },
                # Empty ingress/egress lists establish a baseline fence for selected
                # runner endpoints. Task 2 will add authorized target allowlisting.
                "ingress": [],
                "egress": [],
            },
        }

    def apply_policy(self, *, task_id: str, tenant_id: str) -> RunnerNetworkPolicy:
        """Apply dynamic Cilium policy for one execution task."""
        document = self.build_policy_document(task_id=task_id, tenant_id=tenant_id)
        payload = json.dumps(document, ensure_ascii=True, sort_keys=True)
        result = self._command_runner(["kubectl", "apply", "-f", "-"], payload)
        if result.returncode != 0:
            raise RunnerNetworkPolicyError("failed to apply Cilium network policy")
        return RunnerNetworkPolicy(
            name=str(document["metadata"]["name"]),
            namespace=self._namespace,
            task_id=task_id,
            tenant_id=tenant_id,
        )

    def remove_policy(self, policy: RunnerNetworkPolicy) -> None:
        """Delete a previously applied dynamic policy."""
        result = self._command_runner(
            [
                "kubectl",
                "delete",
                "ciliumnetworkpolicy",
                policy.name,
                "-n",
                policy.namespace,
                "--ignore-not-found=true",
            ],
            None,
        )
        if result.returncode != 0:
            raise RunnerNetworkPolicyError("failed to delete Cilium network policy")

    def _policy_name(self, *, task_id: str, tenant_id: str) -> str:
        return f"ss-runner-{_sanitize(tenant_id)}-{_sanitize(task_id)}"

    @staticmethod
    def _default_command_runner(
        command: list[str],
        stdin_payload: str | None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            command,
            input=stdin_payload,
            text=True,
            capture_output=True,
            check=False,
        )
