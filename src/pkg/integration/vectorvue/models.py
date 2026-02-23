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

"""Typed models for VectorVue API responses."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ResponseEnvelope:
    """Normalized response envelope for VectorVue endpoints."""

    request_id: str | None
    status: str
    data: dict[str, Any] | list[Any] | None
    errors: list[dict[str, Any]] = field(default_factory=list)
    signature: str | None = None
    http_status: int = 0
    headers: dict[str, str] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        """Return true for accepted/replayed responses without structured errors."""
        return self.status in {"accepted", "replayed"} and not self.errors
