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

"""VectorVue HTTP client for SpectraStrike integration endpoints."""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Any
from urllib.parse import urljoin

import requests
from requests import Response, Session
from requests.exceptions import RequestException, Timeout

from pkg.integration.vectorvue.config import VectorVueConfig
from pkg.integration.vectorvue.exceptions import (
    VectorVueAPIError,
    VectorVueSerializationError,
    VectorVueTransportError,
)
from pkg.integration.vectorvue.models import ResponseEnvelope
from pkg.logging.framework import emit_audit_event, get_logger

_RETRYABLE_STATUSES = {429, 502, 503, 504}
_NON_RETRYABLE_ERROR_STATUSES = {400, 401, 403, 404, 409, 422}

logger = get_logger("spectrastrike.integration.vectorvue")


class VectorVueClient:
    """Synchronous client for VectorVue client and integration APIs."""

    def __init__(self, config: VectorVueConfig, session: Session | None = None) -> None:
        self._config = config
        self._session = session or requests.Session()
        self._token = config.token

    def login(self) -> str:
        """Authenticate with VectorVue and cache bearer token."""
        if self._token:
            return self._token

        payload = {
            "username": self._config.username,
            "password": self._config.password,
            "tenant_id": self._config.tenant_id,
        }

        response = self._request(
            method="POST",
            path="/api/v1/client/auth/login",
            json_payload=payload,
            include_auth=False,
            raise_api_error=True,
        )

        token = (response.data or {}).get("access_token")
        if not token and isinstance(response.data, dict):
            token = response.data.get("token")
        if not token:
            raise VectorVueAPIError(
                "login response missing access_token", response.http_status
            )

        self._token = token
        return token

    def send_event(
        self, event: dict[str, Any], idempotency_key: str | None = None
    ) -> ResponseEnvelope:
        """Send one SpectraStrike telemetry event."""
        headers = {}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        return self._request(
            method="POST",
            path="/api/v1/integrations/spectrastrike/events",
            json_payload=event,
            extra_headers=headers,
            raise_api_error=True,
        )

    def send_federated_telemetry(
        self,
        telemetry: dict[str, Any],
        idempotency_key: str | None = None,
    ) -> ResponseEnvelope:
        """Send federated telemetry bundle to the internal gateway endpoint."""
        headers = {}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        return self._request(
            method="POST",
            path="/internal/v1/telemetry",
            json_payload=telemetry,
            extra_headers=headers,
            raise_api_error=True,
        )

    def send_events_batch(self, events: list[dict[str, Any]]) -> ResponseEnvelope:
        """Send a batch of telemetry events."""
        self._validate_batch_size(len(events))
        return self._request(
            method="POST",
            path="/api/v1/integrations/spectrastrike/events/batch",
            json_payload=events,
            raise_api_error=True,
        )

    def send_finding(self, finding: dict[str, Any]) -> ResponseEnvelope:
        """Send one SpectraStrike finding."""
        return self._request(
            method="POST",
            path="/api/v1/integrations/spectrastrike/findings",
            json_payload=finding,
            raise_api_error=True,
        )

    def send_client_event(self, event: dict[str, Any]) -> ResponseEnvelope:
        """Send one client telemetry event to VectorVue client API."""
        return self._request(
            method="POST",
            path="/api/v1/client/events",
            json_payload=event,
            raise_api_error=True,
        )

    def send_findings_batch(self, findings: list[dict[str, Any]]) -> ResponseEnvelope:
        """Send a batch of SpectraStrike findings."""
        self._validate_batch_size(len(findings))
        return self._request(
            method="POST",
            path="/api/v1/integrations/spectrastrike/findings/batch",
            json_payload=findings,
            raise_api_error=True,
        )

    def get_ingest_status(self, request_id: str) -> ResponseEnvelope:
        """Fetch ingest processing status for a prior request."""
        return self._request(
            method="GET",
            path=f"/api/v1/integrations/spectrastrike/ingest/status/{request_id}",
            raise_api_error=True,
        )

    def _validate_batch_size(self, size: int) -> None:
        if size > self._config.max_batch_size:
            raise VectorVueSerializationError(
                f"batch size {size} exceeds max_batch_size "
                f"{self._config.max_batch_size}"
            )

    def _serialize_payload(
        self, json_payload: Any | None
    ) -> tuple[str | None, bytes | None]:
        if json_payload is None:
            return None, None
        try:
            payload_text = json.dumps(
                json_payload, sort_keys=True, separators=(",", ":")
            )
            return payload_text, payload_text.encode("utf-8")
        except (TypeError, ValueError) as exc:
            raise VectorVueSerializationError(
                "payload is not JSON serializable"
            ) from exc

    def _request(
        self,
        method: str,
        path: str,
        json_payload: Any | None = None,
        include_auth: bool = True,
        extra_headers: dict[str, str] | None = None,
        raise_api_error: bool = False,
    ) -> ResponseEnvelope:
        payload_text, body = self._serialize_payload(json_payload)

        headers = {"Content-Type": "application/json"}
        if extra_headers:
            headers.update(extra_headers)

        if include_auth:
            token = self._token or self.login()
            headers["Authorization"] = f"Bearer {token}"

        if self._config.signature_secret and body is not None:
            headers.update(self._build_signature_headers(body))

        url = urljoin(self._config.base_url.rstrip("/") + "/", path.lstrip("/"))

        attempts = self._config.max_retries + 1
        backoff = self._config.backoff_seconds
        last_error: Exception | None = None

        for attempt in range(1, attempts + 1):
            try:
                response = self._session.request(
                    method=method,
                    url=url,
                    data=payload_text,
                    headers=headers,
                    timeout=self._config.timeout_seconds,
                    verify=self._config.verify_tls,
                )
                self._enforce_tls_pin(response)
            except (Timeout, RequestException) as exc:
                last_error = exc
                if attempt >= attempts:
                    raise VectorVueTransportError(
                        f"request failed after {attempts} attempts: {exc}"
                    ) from exc
                time.sleep(backoff * (2 ** (attempt - 1)))
                continue

            envelope = self._parse_response(response)
            self._log_outbound_result(path=path, envelope=envelope, attempt=attempt)

            if response.status_code in _RETRYABLE_STATUSES and attempt < attempts:
                time.sleep(backoff * (2 ** (attempt - 1)))
                continue

            if raise_api_error and response.status_code >= 400:
                error_code = self._extract_error_code(envelope)
                message = self._extract_error_message(envelope)
                raise VectorVueAPIError(
                    message=message,
                    status_code=response.status_code,
                    error_code=error_code,
                )

            return envelope

        if last_error:
            raise VectorVueTransportError(str(last_error)) from last_error

        raise VectorVueTransportError("request failed without specific error")

    def _enforce_tls_pin(self, response: Response) -> None:
        pinned = self._config.tls_pinned_cert_sha256
        if not pinned:
            return

        peer_cert = self._extract_peer_cert(response)
        if peer_cert is None:
            raise VectorVueTransportError(
                "tls pinning enabled but peer certificate is unavailable"
            )

        actual = hashlib.sha256(peer_cert).hexdigest().lower()
        expected = pinned.replace(":", "").lower()
        if actual != expected:
            raise VectorVueTransportError("tls pinning validation failed")

    def _extract_peer_cert(self, response: Response) -> bytes | None:
        raw = getattr(response, "raw", None)
        connection = getattr(raw, "connection", None) if raw is not None else None
        sock = getattr(connection, "sock", None) if connection is not None else None
        if sock is None:
            return None
        get_peer_cert = getattr(sock, "getpeercert", None)
        if not callable(get_peer_cert):
            return None
        try:
            cert = get_peer_cert(binary_form=True)
        except Exception:
            return None
        return cert if isinstance(cert, (bytes, bytearray)) else None

    def _build_signature_headers(self, body: bytes) -> dict[str, str]:
        timestamp = str(int(time.time()))
        mac = hmac.new(
            key=self._config.signature_secret.encode("utf-8"),
            msg=(timestamp + ".").encode("utf-8") + body,
            digestmod=hashlib.sha256,
        ).hexdigest()
        return {
            "X-Timestamp": timestamp,
            "X-Signature": mac,
        }

    def _parse_response(self, response: Response) -> ResponseEnvelope:
        payload: dict[str, Any]
        try:
            payload = response.json()
            if not isinstance(payload, dict):
                payload = {}
        except ValueError:
            payload = {}

        envelope_keys = {"request_id", "status", "data", "errors", "signature"}
        if payload and not any(key in payload for key in envelope_keys):
            parsed_data: dict[str, Any] | list[Any] | None = payload
        else:
            parsed_data = payload.get("data")

        return ResponseEnvelope(
            request_id=payload.get("request_id"),
            status=payload.get(
                "status", "failed" if response.status_code >= 400 else "accepted"
            ),
            data=parsed_data,
            errors=self._coerce_errors(payload.get("errors")),
            signature=payload.get("signature"),
            http_status=response.status_code,
            headers={k: v for k, v in response.headers.items()},
        )

    def _coerce_errors(self, errors: Any) -> list[dict[str, Any]]:
        if not isinstance(errors, list):
            return []
        normalized: list[dict[str, Any]] = []
        for err in errors:
            if isinstance(err, dict):
                normalized.append(err)
            else:
                normalized.append({"message": str(err)})
        return normalized

    def _extract_error_code(self, envelope: ResponseEnvelope) -> str | None:
        if not envelope.errors:
            return None
        first_error = envelope.errors[0]
        error_code = first_error.get("error_code") or first_error.get("code")
        return str(error_code) if error_code else None

    def _extract_error_message(self, envelope: ResponseEnvelope) -> str:
        if envelope.errors:
            first_error = envelope.errors[0]
            if first_error.get("error_message"):
                return str(first_error["error_message"])
            if first_error.get("message"):
                return str(first_error["message"])

        if envelope.http_status in _NON_RETRYABLE_ERROR_STATUSES:
            return f"VectorVue API request failed with status {envelope.http_status}"
        return f"VectorVue API request error status {envelope.http_status}"

    def _log_outbound_result(
        self, path: str, envelope: ResponseEnvelope, attempt: int
    ) -> None:
        request_id = envelope.request_id or "unknown"
        tenant = self._config.tenant_id or "unknown"
        logger.info(
            "VectorVue request %s status=%s request_id=%s attempt=%s",
            path,
            envelope.status,
            request_id,
            attempt,
        )
        emit_audit_event(
            action="vectorvue_request",
            actor="spectrastrike",
            target=path,
            status=envelope.status,
            request_id=request_id,
            tenant_id=tenant,
            http_status=envelope.http_status,
            attempt=attempt,
        )
