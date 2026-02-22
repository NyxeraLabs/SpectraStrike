"""Custom exceptions for VectorVue integration client."""

from __future__ import annotations


class VectorVueError(Exception):
    """Base error for VectorVue client operations."""


class VectorVueConfigError(VectorVueError):
    """Raised when VectorVue client configuration is invalid."""


class VectorVueTransportError(VectorVueError):
    """Raised when transport-level failures occur during API calls."""


class VectorVueAPIError(VectorVueError):
    """Raised when API call returns an error response."""

    def __init__(self, message: str, status_code: int, error_code: str | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code


class VectorVueSerializationError(VectorVueError):
    """Raised when request payload cannot be serialized."""
