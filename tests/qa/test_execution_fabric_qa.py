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

import base64
import hashlib
import hmac
import json
from pathlib import Path

import pytest

from pkg.armory.service import ArmoryService
from pkg.orchestrator.manifest import ExecutionManifest, ExecutionTaskContext
from pkg.runner.jws_verify import JWSVerificationError, RunnerJWSVerifier
from pkg.runner.universal import RunnerExecutionError, UniversalEdgeRunner


def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _hs256(payload: dict[str, object], secret: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    hseg = _b64(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    pseg = _b64(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{hseg}.{pseg}".encode("ascii")
    sig = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    return f"{hseg}.{pseg}.{_b64(sig)}"


def _manifest(tool_sha256: str) -> ExecutionManifest:
    return ExecutionManifest(
        task_context=ExecutionTaskContext(
            task_id="task-s13-001",
            tenant_id="tenant-a",
            operator_id="operator-a",
            source="qa",
            action="execute",
        ),
        target_urn="urn:target:ip:10.10.10.10",
        tool_sha256=tool_sha256,
        parameters={"safe": True},
    )


def test_qa_forged_jws_signature_is_rejected() -> None:
    verifier = RunnerJWSVerifier()
    valid = _hs256({"task_id": "task-s13-001"}, "secret")
    forged = valid[:-1] + ("A" if valid[-1] != "A" else "B")

    with pytest.raises(JWSVerificationError):
        verifier.verify(compact_jws=forged, hmac_secret="secret")


def test_qa_tampered_tool_digest_is_rejected(tmp_path: Path) -> None:
    armory = ArmoryService(registry_path=str(tmp_path / "armory.json"))
    ingested = armory.ingest_tool(
        tool_name="scanner",
        image_ref="registry.internal/security/scanner:1.0.0",
        artifact=b"immutable-binary",
    )
    armory.approve_tool(tool_sha256=ingested.tool_sha256, approver="qa")

    tampered = _manifest("sha256:" + "0" * 64)
    runner = UniversalEdgeRunner(armory=armory)

    with pytest.raises(RunnerExecutionError):
        runner.resolve_signed_tool(tampered)


def test_qa_stdout_stderr_map_to_cloudevents(tmp_path: Path) -> None:
    armory = ArmoryService(registry_path=str(tmp_path / "armory.json"))
    ingested = armory.ingest_tool(
        tool_name="scanner",
        image_ref="registry.internal/security/scanner:1.0.0",
        artifact=b"immutable-binary",
    )
    armory.approve_tool(tool_sha256=ingested.tool_sha256, approver="qa")

    manifest = _manifest(ingested.tool_sha256)
    runner = UniversalEdgeRunner(
        armory=armory,
        command_runner=lambda cmd: __import__("subprocess").CompletedProcess(
            cmd,
            2,
            "stdout-lines",
            "stderr-lines",
        ),
    )
    tool = runner.resolve_signed_tool(manifest)
    command = runner.build_sandbox_command(tool=tool, manifest=manifest)
    result = runner.execute(manifest=manifest, manifest_jws="a.b.c", command=command)

    event = result.event.to_dict()
    assert event["specversion"] == "1.0"
    assert event["data"]["stdout"] == "stdout-lines"
    assert event["data"]["stderr"] == "stderr-lines"
    assert event["data"]["status"] == "failed"
