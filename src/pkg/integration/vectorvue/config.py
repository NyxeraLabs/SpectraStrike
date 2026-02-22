"""Configuration model for VectorVue integration client."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

from pkg.integration.vectorvue.exceptions import VectorVueConfigError


@dataclass(slots=True)
class VectorVueConfig:
    """Runtime configuration for VectorVue client."""

    base_url: str = "https://127.0.0.1"
    username: str | None = None
    password: str | None = None
    tenant_id: str | None = None
    token: str | None = None
    timeout_seconds: float = 10.0
    verify_tls: bool = True
    max_retries: int = 3
    backoff_seconds: float = 0.5
    max_batch_size: int = 100
    signature_secret: str | None = None
    require_https: bool = True

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        parsed = urlparse(self.base_url)
        if not parsed.scheme or not parsed.netloc:
            raise VectorVueConfigError("base_url must be an absolute URL")

        if self.require_https and parsed.scheme.lower() != "https":
            raise VectorVueConfigError("base_url must use https when require_https is enabled")

        if self.timeout_seconds <= 0:
            raise VectorVueConfigError("timeout_seconds must be greater than zero")

        if self.max_retries < 0:
            raise VectorVueConfigError("max_retries must be zero or greater")

        if self.backoff_seconds < 0:
            raise VectorVueConfigError("backoff_seconds must be zero or greater")

        if self.max_batch_size <= 0:
            raise VectorVueConfigError("max_batch_size must be greater than zero")

        if self.token:
            return

        if not (self.username and self.password and self.tenant_id):
            raise VectorVueConfigError(
                "token or login credentials (username, password, tenant_id) must be set"
            )
