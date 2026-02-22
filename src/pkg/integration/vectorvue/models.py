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
