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

"""Metasploit RPC wrapper for exploit execution and session capture."""

from __future__ import annotations

import hashlib
import os
import time
from dataclasses import dataclass, field
from typing import Any, Callable

import requests

from pkg.logging.framework import get_logger
from pkg.orchestrator.telemetry_ingestion import TelemetryEvent, TelemetryIngestionPipeline

logger = get_logger("spectrastrike.wrappers.metasploit")


class MetasploitRPCError(RuntimeError):
    """Raised when Metasploit RPC interactions fail."""


class MetasploitTransportError(MetasploitRPCError):
    """Raised on transport-level failures."""


@dataclass(slots=True)
class MetasploitConfig:
    """Runtime config for Metasploit RPC transport."""

    host: str = "metasploit.remote.operator"
    port: int = 55553
    ssl: bool = True
    uri: str = "/api/1.0"
    username: str = "msf"
    password: str = "msf"
    timeout_seconds: float = 10.0
    max_retries: int = 2
    backoff_seconds: float = 0.2
    tls_pinned_cert_sha256: str | None = None

    @property
    def endpoint(self) -> str:
        scheme = "https" if self.ssl else "http"
        return f"{scheme}://{self.host}:{self.port}{self.uri}"

    @classmethod
    def from_env(cls, prefix: str = "MSF_RPC_") -> MetasploitConfig:
        """Build config from environment variables for remote operator endpoints."""
        host = os.getenv(f"{prefix}HOST", "metasploit.remote.operator")
        port = int(os.getenv(f"{prefix}PORT", "55553"))
        ssl_raw = os.getenv(f"{prefix}SSL", "true").strip().lower()
        ssl = ssl_raw in {"1", "true", "yes", "on"}
        uri = os.getenv(f"{prefix}URI", "/api/1.0")
        username = os.getenv(f"{prefix}USERNAME", "msf")
        password = os.getenv(f"{prefix}PASSWORD", "msf")
        timeout_seconds = float(os.getenv(f"{prefix}TIMEOUT_SECONDS", "10.0"))
        max_retries = int(os.getenv(f"{prefix}MAX_RETRIES", "2"))
        backoff_seconds = float(os.getenv(f"{prefix}BACKOFF_SECONDS", "0.2"))
        tls_pinned_cert_sha256 = os.getenv(f"{prefix}TLS_PINNED_CERT_SHA256")
        return cls(
            host=host,
            port=port,
            ssl=ssl,
            uri=uri,
            username=username,
            password=password,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            backoff_seconds=backoff_seconds,
            tls_pinned_cert_sha256=tls_pinned_cert_sha256,
        )


@dataclass(slots=True)
class ExploitRequest:
    """Input payload for one Metasploit exploit run."""

    module_type: str
    module_name: str
    target_host: str
    target_port: int | None = None
    payload: str | None = None
    options: dict[str, Any] = field(default_factory=dict)

    def rpc_options(self) -> dict[str, Any]:
        resolved = dict(self.options)
        resolved["RHOSTS"] = self.target_host
        if self.target_port is not None:
            resolved["RPORT"] = self.target_port
        if self.payload:
            resolved["PAYLOAD"] = self.payload
        return resolved


@dataclass(slots=True)
class SessionTranscript:
    """Normalized captured output for one session."""

    session_id: str
    session_type: str
    output: str


@dataclass(slots=True)
class MetasploitExploitResult:
    """Normalized exploit execution outcome."""

    module_type: str
    module_name: str
    target_host: str
    job_id: str | None
    uuid: str | None
    sessions: list[SessionTranscript]
    raw_execute_response: dict[str, Any]

    @property
    def status(self) -> str:
        return "success" if self.job_id or self.uuid else "failed"


RPCTransport = Callable[[str, list[Any], MetasploitConfig], dict[str, Any]]


def default_rpc_transport(method: str, params: list[Any], config: MetasploitConfig) -> dict[str, Any]:
    """Default HTTP transport for Metasploit JSON-RPC."""
    payload = {"method": method, "params": params}
    try:
        response = requests.post(
            config.endpoint,
            json=payload,
            timeout=config.timeout_seconds,
            verify=config.ssl,
        )
        _enforce_tls_pin(response, config.tls_pinned_cert_sha256)
    except requests.RequestException as exc:
        raise MetasploitTransportError(str(exc)) from exc

    if response.status_code >= 400:
        raise MetasploitTransportError(f"Metasploit RPC HTTP {response.status_code}")

    try:
        data = response.json()
    except ValueError as exc:
        raise MetasploitTransportError("invalid JSON response from Metasploit RPC") from exc

    if not isinstance(data, dict):
        raise MetasploitTransportError("invalid RPC payload shape")
    return data


def _enforce_tls_pin(response: requests.Response, pinned_sha256: str | None) -> None:
    if not pinned_sha256:
        return
    cert = _extract_peer_cert(response)
    if cert is None:
        raise MetasploitTransportError(
            "tls pinning enabled but peer certificate is unavailable"
        )
    actual = hashlib.sha256(cert).hexdigest().lower()
    expected = pinned_sha256.replace(":", "").lower()
    if actual != expected:
        raise MetasploitTransportError("tls pinning validation failed")


def _extract_peer_cert(response: requests.Response) -> bytes | None:
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


class MetasploitWrapper:
    """Wrapper around Metasploit RPC auth/module execution/session APIs."""

    def __init__(
        self,
        config: MetasploitConfig | None = None,
        transport: RPCTransport | None = None,
    ) -> None:
        self._config = config or MetasploitConfig()
        self._transport = transport or default_rpc_transport
        self._token: str | None = None

    def connect(self) -> str:
        """Authenticate against Metasploit RPC and cache token."""
        if self._token:
            return self._token

        response = self._rpc_call_with_retry(
            "auth.login",
            [self._config.username, self._config.password],
            include_token=False,
        )
        token = response.get("token")
        if not token:
            raise MetasploitRPCError("metasploit auth.login response missing token")
        self._token = str(token)
        logger.info("Metasploit RPC authenticated")
        return self._token

    def load_module(self, module_type: str, module_name: str) -> dict[str, Any]:
        """Load module metadata from Metasploit RPC."""
        response = self._rpc_call_with_retry("module.info", [module_type, module_name])
        logger.info("Metasploit module loaded: %s/%s", module_type, module_name)
        return response

    def execute_exploit(self, request: ExploitRequest) -> MetasploitExploitResult:
        """Execute exploit module and capture sessions."""
        self.load_module(request.module_type, request.module_name)
        execute_response = self._rpc_call_with_retry(
            "module.execute",
            [request.module_type, request.module_name, request.rpc_options()],
        )

        job_id = execute_response.get("job_id")
        uuid = execute_response.get("uuid")
        sessions = self.capture_session_output()
        logger.info(
            "Metasploit exploit executed: module=%s target=%s job_id=%s",
            request.module_name,
            request.target_host,
            job_id,
        )
        return MetasploitExploitResult(
            module_type=request.module_type,
            module_name=request.module_name,
            target_host=request.target_host,
            job_id=str(job_id) if job_id is not None else None,
            uuid=str(uuid) if uuid is not None else None,
            sessions=sessions,
            raw_execute_response=execute_response,
        )

    def capture_session_output(self) -> list[SessionTranscript]:
        """Capture available output from active sessions."""
        session_listing = self._rpc_call_with_retry("session.list", [])
        sessions: list[SessionTranscript] = []
        for session_id, session_meta in session_listing.items():
            if not isinstance(session_meta, dict):
                continue
            session_type = str(session_meta.get("type", "shell"))
            method = "session.meterpreter_read" if session_type == "meterpreter" else "session.shell_read"
            output_response = self._rpc_call_with_retry(method, [session_id])
            output = str(output_response.get("data") or output_response.get("output") or "")
            sessions.append(
                SessionTranscript(
                    session_id=str(session_id),
                    session_type=session_type,
                    output=output,
                )
            )
        return sessions

    def send_to_orchestrator(
        self,
        result: MetasploitExploitResult,
        telemetry: TelemetryIngestionPipeline,
        actor: str = "metasploit-wrapper",
    ) -> TelemetryEvent:
        """Emit exploit outcome to orchestrator telemetry pipeline."""
        return telemetry.ingest(
            event_type="metasploit_exploit_completed",
            actor=actor,
            target="orchestrator",
            status=result.status,
            module_type=result.module_type,
            module_name=result.module_name,
            target_host=result.target_host,
            job_id=result.job_id,
            uuid=result.uuid,
            session_count=len(result.sessions),
            sessions=[
                {
                    "session_id": s.session_id,
                    "session_type": s.session_type,
                    "output": s.output,
                }
                for s in result.sessions
            ],
        )

    def _rpc_call_with_retry(
        self,
        method: str,
        params: list[Any],
        include_token: bool = True,
    ) -> dict[str, Any]:
        attempts = self._config.max_retries + 1
        token = self.connect() if include_token else None
        final_params = [token, *params] if include_token and token else params

        last_error: Exception | None = None
        for attempt in range(1, attempts + 1):
            try:
                response = self._transport(method, final_params, self._config)
                if "error" in response and response["error"]:
                    raise MetasploitRPCError(str(response["error"]))
                return response
            except (MetasploitTransportError, MetasploitRPCError) as exc:
                last_error = exc
                if attempt >= attempts:
                    raise MetasploitRPCError(
                        f"metasploit rpc call failed for {method} after {attempts} attempts: {exc}"
                    ) from exc
                time.sleep(self._config.backoff_seconds * (2 ** (attempt - 1)))

        raise MetasploitRPCError(str(last_error) if last_error else "unknown metasploit rpc error")
