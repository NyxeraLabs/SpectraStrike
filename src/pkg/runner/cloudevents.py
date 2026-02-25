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

"""CloudEvents mapping for universal runner execution output."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


@dataclass(slots=True)
class CloudEventEnvelope:
    """Minimal CloudEvents envelope carrying execution contract payload."""

    source: str
    type: str
    subject: str
    data: dict[str, Any]
    id: str = field(default_factory=lambda: str(uuid4()))
    time: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    specversion: str = "1.0"

    def to_dict(self) -> dict[str, Any]:
        """Return event payload as serialized mapping."""
        return {
            "id": self.id,
            "specversion": self.specversion,
            "source": self.source,
            "type": self.type,
            "subject": self.subject,
            "time": self.time,
            "data": dict(self.data),
        }


def map_execution_to_cloudevent(
    *,
    task_id: str,
    tenant_id: str,
    tool_sha256: str,
    target_urn: str,
    exit_code: int,
    stdout: str,
    stderr: str,
    manifest_jws: str,
) -> CloudEventEnvelope:
    """Build CloudEvents-compliant result with stdout/stderr execution contract."""
    status = "success" if exit_code == 0 else "failed"
    return CloudEventEnvelope(
        source="urn:spectrastrike:runner",
        type="com.nyxeralabs.spectrastrike.runner.execution.v1",
        subject=task_id,
        data={
            "task_id": task_id,
            "tenant_id": tenant_id,
            "tool_sha256": tool_sha256,
            "target_urn": target_urn,
            "status": status,
            "exit_code": exit_code,
            "stdout": stdout,
            "stderr": stderr,
            "manifest_jws": manifest_jws,
        },
    )
