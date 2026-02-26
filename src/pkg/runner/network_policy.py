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
import ipaddress
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

    def build_policy_document(
        self, *, task_id: str, tenant_id: str, target_urn: str
    ) -> dict[str, object]:
        """Create policy with egress allowlist restricted to manifest target IP/CIDR."""
        policy_name = self._policy_name(task_id=task_id, tenant_id=tenant_id)
        target_cidr = self._target_cidr_from_urn(target_urn)
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
                "description": "Sprint 15 dynamic isolation with target egress allowlist",
                "endpointSelector": {
                    "matchLabels": {
                        "spectrastrike.io/task-id": task_id,
                        "spectrastrike.io/tenant-id": tenant_id,
                    }
                },
                # Explicit lateral movement blocks toward cluster/node/control-plane
                # paths regardless of requested target.
                "egressDeny": [
                    {
                        "toEntities": [
                            "cluster",
                            "host",
                            "remote-node",
                        ]
                    },
                    {
                        "toCIDRSet": [
                            {"cidr": "127.0.0.0/8"},
                            {"cidr": "169.254.0.0/16"},
                            {"cidr": "::1/128"},
                            {"cidr": "fe80::/10"},
                        ]
                    },
                ],
                # Deny-by-default ingress plus explicit egress allowlist to the
                # authorized target defined in manifest target_urn.
                "ingress": [],
                "egress": [
                    {
                        "toCIDRSet": [
                            {
                                "cidr": target_cidr,
                            }
                        ]
                    }
                ],
            },
        }

    def apply_policy(
        self, *, task_id: str, tenant_id: str, target_urn: str
    ) -> RunnerNetworkPolicy:
        """Apply dynamic Cilium policy for one execution task."""
        document = self.build_policy_document(
            task_id=task_id,
            tenant_id=tenant_id,
            target_urn=target_urn,
        )
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
    def _target_cidr_from_urn(target_urn: str) -> str:
        prefix = "urn:target:ip:"
        if target_urn.startswith(prefix):
            raw = target_urn.removeprefix(prefix).strip()
            try:
                ip_obj = ipaddress.ip_address(raw)
            except ValueError as exc:
                raise RunnerNetworkPolicyError("target_urn IP is invalid") from exc
            suffix = "32" if ip_obj.version == 4 else "128"
            return f"{ip_obj.compressed}/{suffix}"

        cidr_prefix = "urn:target:cidr:"
        if target_urn.startswith(cidr_prefix):
            raw = target_urn.removeprefix(cidr_prefix).strip()
            try:
                network = ipaddress.ip_network(raw, strict=False)
            except ValueError as exc:
                raise RunnerNetworkPolicyError("target_urn CIDR is invalid") from exc
            return str(network)

        raise RunnerNetworkPolicyError(
            "target_urn must use urn:target:ip:<addr> or urn:target:cidr:<cidr>"
        )

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
