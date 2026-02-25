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

import pytest

from pkg.armory.service import ArmoryService


def test_ingest_pipeline_persists_registry_entry(tmp_path: Path) -> None:
    service = ArmoryService(registry_path=str(tmp_path / "armory.json"))

    result = service.ingest_tool(
        tool_name="nmap-secure",
        image_ref="registry.internal/security/nmap:1.0.0",
        artifact=b"container-bytes",
    )

    assert result.status == "accepted"
    tools = service.list_tools()
    assert len(tools) == 1
    assert tools[0].tool_sha256 == result.tool_sha256
    assert tools[0].signature_bundle["type"] == "cosign-simulated"


def test_approve_tool_marks_authorized(tmp_path: Path) -> None:
    service = ArmoryService(registry_path=str(tmp_path / "armory.json"))
    result = service.ingest_tool(
        tool_name="scanner",
        image_ref="registry.internal/tools/scanner:2.0.0",
        artifact=b"artifact",
    )

    approved = service.approve_tool(tool_sha256=result.tool_sha256, approver="secops")

    assert approved.authorized is True
    assert approved.approved_by == "secops"
    assert len(service.list_tools(authorized_only=True)) == 1


def test_get_authorized_tool_rejects_unapproved_digest(tmp_path: Path) -> None:
    service = ArmoryService(registry_path=str(tmp_path / "armory.json"))
    result = service.ingest_tool(
        tool_name="scanner",
        image_ref="registry.internal/tools/scanner:2.0.0",
        artifact=b"artifact",
    )

    with pytest.raises(KeyError):
        service.get_authorized_tool(tool_sha256=result.tool_sha256)
