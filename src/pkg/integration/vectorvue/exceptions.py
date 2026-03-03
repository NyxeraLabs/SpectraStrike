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

"""Custom exceptions for VectorVue integration client."""

from __future__ import annotations


class VectorVueError(Exception):
    """Base error for VectorVue client operations."""


class VectorVueConfigError(VectorVueError):
    """Raised when VectorVue client configuration is invalid."""


class VectorVueTransportError(VectorVueError):
    """Raised when transport-level failures occur during API calls."""

    def __init__(self, message: str, attempts_used: int | None = None) -> None:
        super().__init__(message)
        self.attempts_used = attempts_used


class VectorVueAPIError(VectorVueError):
    """Raised when API call returns an error response."""

    def __init__(
        self,
        message: str,
        status_code: int,
        error_code: str | None = None,
        request_id: str | None = None,
        retry_count: int = 0,
        signature_verification_state: str = "unknown",
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code
        self.request_id = request_id
        self.retry_count = retry_count
        self.signature_verification_state = signature_verification_state


class VectorVueSerializationError(VectorVueError):
    """Raised when request payload cannot be serialized."""
