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

"""Sprint 13 adversarial QA for Universal Runner execution fabric."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import subprocess
from pathlib import Path

import pytest

from pkg.armory.service import ArmoryService
from pkg.orchestrator.manifest import ExecutionManifest, ExecutionTaskContext
from pkg.runner.jws_verify import JWSVerificationError
from pkg.runner.universal import RunnerExecutionError, UniversalEdgeRunner


def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _hs256_jws(payload: dict[str, object], secret: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    header_segment = _b64(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_segment = _b64(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_segment}.{payload_segment}".encode("ascii")
    signature = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    return f"{header_segment}.{payload_segment}.{_b64(signature)}"


def _manifest(tool_sha256: str) -> ExecutionManifest:
    return ExecutionManifest(
        task_context=ExecutionTaskContext(
            task_id="task-s13-001",
            tenant_id="tenant-a",
            operator_id="operator-a",
            source="qa",
            action="execute",
        ),
        target_urn="urn:target:ip:10.0.0.5",
        tool_sha256=tool_sha256,
        parameters={"mode": "safe"},
    )


def test_forged_jws_signatures_fail_validation(tmp_path: Path) -> None:
    armory = ArmoryService(registry_path=str(tmp_path / "armory.json"))
    runner = UniversalEdgeRunner(armory=armory)
    signed = _hs256_jws({"task_id": "task-s13-001"}, "secret")
    forged = signed[:-1] + ("A" if signed[-1] != "A" else "B")

    with pytest.raises(JWSVerificationError):
        runner.verify_manifest_jws(compact_jws=forged, hmac_secret="secret")


def test_tampered_digest_fails_armory_resolution(tmp_path: Path) -> None:
    armory = ArmoryService(registry_path=str(tmp_path / "armory.json"))
    ingested = armory.ingest_tool(
        tool_name="nmap",
        image_ref="registry.internal/security/nmap:1.0.0",
        artifact=b"tool-bytes",
    )
    armory.approve_tool(tool_sha256=ingested.tool_sha256, approver="secops")
    runner = UniversalEdgeRunner(armory=armory)
    tampered_manifest = _manifest("sha256:" + ("f" * 64))

    with pytest.raises(RunnerExecutionError):
        runner.resolve_signed_tool(tampered_manifest)


def test_execution_output_maps_to_standardized_cloudevents(tmp_path: Path) -> None:
    armory = ArmoryService(registry_path=str(tmp_path / "armory.json"))
    ingested = armory.ingest_tool(
        tool_name="nmap",
        image_ref="registry.internal/security/nmap:1.0.0",
        artifact=b"tool-bytes",
    )
    armory.approve_tool(tool_sha256=ingested.tool_sha256, approver="secops")
    manifest = _manifest(ingested.tool_sha256)

    def fake_runner(command: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 0, "scan-ok", "")

    runner = UniversalEdgeRunner(armory=armory, command_runner=fake_runner)
    result = runner.execute(
        manifest=manifest,
        manifest_jws="header.payload.signature",
        command=["docker", "run", "dry"],
    )
    event = result.event.to_dict()

    assert event["specversion"] == "1.0"
    assert event["type"] == "com.nyxeralabs.spectrastrike.runner.execution.v1"
    assert event["subject"] == manifest.task_context.task_id
    assert event["data"]["stdout"] == "scan-ok"
    assert event["data"]["stderr"] == ""
    assert event["data"]["exit_code"] == 0
    assert event["data"]["status"] == "success"
    assert event["data"]["manifest_jws"] == "header.payload.signature"
