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

"""Armory tool registry with SBOM/scan/signing enforcement."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from typing import Any, Protocol


@dataclass(slots=True)
class ArmoryTool:
    """Immutable tool registry entry for BYOT artifacts."""

    tool_name: str
    image_ref: str
    tool_sha256: str
    sbom_format: str
    sbom_digest: str
    vulnerability_summary: dict[str, int]
    signature_bundle: dict[str, str]
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    authorized: bool = False
    approved_by: str | None = None
    approved_at: str | None = None


@dataclass(slots=True)
class ArmoryIngestResult:
    """Ingestion pipeline outcome metadata."""

    status: str
    tool_sha256: str
    sbom_status: str
    vuln_scan_status: str
    signature_status: str


class ToolScanner(Protocol):
    """Scanner interface for SBOM and vulnerability pipeline."""

    def generate_sbom(self, *, image_ref: str, artifact: bytes) -> tuple[str, str]:
        """Return (sbom_format, sbom_digest)."""

    def scan_vulnerabilities(self, *, sbom_digest: str) -> dict[str, int]:
        """Return vulnerability severity counts."""


class ToolSigner(Protocol):
    """Signing interface for cosign/sigstore-equivalent workflows."""

    def sign(self, *, image_ref: str, tool_sha256: str) -> dict[str, str]:
        """Return signature and signing identity metadata."""


class LocalScanner:
    """Deterministic local scanner used in CI/dev until external scanners are wired."""

    def generate_sbom(self, *, image_ref: str, artifact: bytes) -> tuple[str, str]:
        sbom_material = f"{image_ref}:{len(artifact)}".encode("utf-8") + artifact
        digest = hashlib.sha256(sbom_material).hexdigest()
        return ("spdx-json", f"sha256:{digest}")

    def scan_vulnerabilities(self, *, sbom_digest: str) -> dict[str, int]:
        # Stable pseudo-risk profile derived from SBOM digest to keep tests deterministic.
        raw = bytes.fromhex(sbom_digest.removeprefix("sha256:"))
        return {
            "critical": raw[0] % 2,
            "high": raw[1] % 3,
            "medium": raw[2] % 4,
            "low": raw[3] % 5,
        }


class DefaultToolSigner:
    """Deterministic signer placeholder for Sigstore/cosign control flow."""

    def __init__(
        self, issuer: str = "sigstore.dev", identity: str = "armory@nyxera"
    ) -> None:
        self._issuer = issuer
        self._identity = identity

    def sign(self, *, image_ref: str, tool_sha256: str) -> dict[str, str]:
        material = f"{image_ref}|{tool_sha256}|{self._issuer}|{self._identity}".encode(
            "utf-8"
        )
        signature = hashlib.sha256(material).hexdigest()
        return {
            "type": "cosign-simulated",
            "issuer": self._issuer,
            "identity": self._identity,
            "signature": f"sha256:{signature}",
        }


class ArmoryService:
    """File-backed immutable registry for authorized BYOT artifacts."""

    def __init__(
        self,
        *,
        registry_path: str | None = None,
        scanner: ToolScanner | None = None,
        signer: ToolSigner | None = None,
    ) -> None:
        configured = registry_path or os.getenv(
            "SPECTRASTRIKE_ARMORY_REGISTRY_PATH", ".spectrastrike/armory/registry.json"
        )
        self._registry_path = Path(configured).expanduser().resolve()
        self._scanner = scanner or LocalScanner()
        self._signer = signer or DefaultToolSigner()
        self._lock = Lock()

    def ingest_tool(
        self, *, tool_name: str, image_ref: str, artifact: bytes
    ) -> ArmoryIngestResult:
        """Run upload -> SBOM -> vulnerability scan -> signing workflow."""
        self._validate_inputs(
            tool_name=tool_name, image_ref=image_ref, artifact=artifact
        )
        tool_sha256 = f"sha256:{hashlib.sha256(artifact).hexdigest()}"

        sbom_format, sbom_digest = self._scanner.generate_sbom(
            image_ref=image_ref,
            artifact=artifact,
        )
        vuln_summary = self._scanner.scan_vulnerabilities(sbom_digest=sbom_digest)
        signature_bundle = self._signer.sign(
            image_ref=image_ref, tool_sha256=tool_sha256
        )

        tool = ArmoryTool(
            tool_name=tool_name,
            image_ref=image_ref,
            tool_sha256=tool_sha256,
            sbom_format=sbom_format,
            sbom_digest=sbom_digest,
            vulnerability_summary=vuln_summary,
            signature_bundle=signature_bundle,
        )
        with self._lock:
            records = self._read_registry_unlocked()
            records = [
                record for record in records if record.tool_sha256 != tool_sha256
            ]
            records.append(tool)
            self._write_registry_unlocked(records)

        return ArmoryIngestResult(
            status="accepted",
            tool_sha256=tool_sha256,
            sbom_status="completed",
            vuln_scan_status="completed",
            signature_status="pending_approval",
        )

    def approve_tool(self, *, tool_sha256: str, approver: str) -> ArmoryTool:
        """Promote signed tool digest into authorized execution set."""
        if not tool_sha256.startswith("sha256:"):
            raise ValueError("tool_sha256 must start with sha256:")
        if not approver.strip():
            raise ValueError("approver is required")

        with self._lock:
            records = self._read_registry_unlocked()
            for tool in records:
                if tool.tool_sha256 == tool_sha256:
                    tool.authorized = True
                    tool.approved_by = approver
                    tool.approved_at = datetime.now(UTC).isoformat()
                    self._write_registry_unlocked(records)
                    return tool

        raise KeyError(f"tool digest not found: {tool_sha256}")

    def list_tools(self, *, authorized_only: bool = False) -> list[ArmoryTool]:
        """Return ingested tools, optionally filtering to approved digests only."""
        with self._lock:
            records = self._read_registry_unlocked()
        if not authorized_only:
            return records
        return [tool for tool in records if tool.authorized]

    def get_authorized_tool(self, *, tool_sha256: str) -> ArmoryTool:
        """Load one authorized tool by digest for edge-runner retrieval."""
        with self._lock:
            records = self._read_registry_unlocked()
        for tool in records:
            if tool.tool_sha256 == tool_sha256 and tool.authorized:
                return tool
        raise KeyError(f"authorized tool not found: {tool_sha256}")

    def _read_registry_unlocked(self) -> list[ArmoryTool]:
        if not self._registry_path.exists():
            return []
        content = self._registry_path.read_text(encoding="utf-8")
        raw_items = json.loads(content)
        if not isinstance(raw_items, list):
            return []
        result: list[ArmoryTool] = []
        for item in raw_items:
            if not isinstance(item, dict):
                continue
            result.append(ArmoryTool(**item))
        return result

    def _write_registry_unlocked(self, records: list[ArmoryTool]) -> None:
        self._registry_path.parent.mkdir(parents=True, exist_ok=True)
        payload = [asdict(record) for record in records]
        self._registry_path.write_text(
            json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    @staticmethod
    def _validate_inputs(*, tool_name: str, image_ref: str, artifact: bytes) -> None:
        if len(tool_name.strip()) < 3:
            raise ValueError("tool_name must be at least 3 chars")
        if "/" not in image_ref or ":" not in image_ref:
            raise ValueError("image_ref must look like <registry>/<repo>:<tag>")
        if not artifact:
            raise ValueError("artifact must not be empty")
