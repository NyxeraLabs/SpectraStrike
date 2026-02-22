# VectorVue API Client Design (Sprint 4)

## Goal
Define a secure, testable, and extensible Python API client for delivering SpectraStrike orchestrator telemetry and findings to VectorVue.

## Client Responsibilities
1. Manage authenticated HTTP communication to VectorVue.
2. Normalize orchestrator outputs into VectorVue payload schemas.
3. Provide resilient delivery primitives (retry, batching, integrity hooks).
4. Emit local logs/audit events for outbound operations.

## Proposed Package Layout
- `src/pkg/integration/vectorvue/client.py`
- `src/pkg/integration/vectorvue/models.py`
- `src/pkg/integration/vectorvue/config.py`
- `src/pkg/integration/vectorvue/exceptions.py`

## Primary Interfaces
1. `VectorVueClient`
- `health_check() -> bool`
- `send_event(event: dict[str, Any]) -> ResponseEnvelope`
- `send_batch(events: list[dict[str, Any]]) -> ResponseEnvelope`

2. `VectorVueConfig`
- `base_url: str`
- `api_key_env: str`
- `timeout_seconds: float`
- `verify_tls: bool = True`
- `max_retries: int`
- `batch_size: int`

3. `ResponseEnvelope`
- `success: bool`
- `status_code: int`
- `request_id: str | None`
- `error: str | None`

## Request Flow
1. Validate config and required credential source.
2. Build request headers (`Authorization`, `Content-Type`, optional signature headers).
3. Serialize payload deterministically.
4. Send over HTTPS with timeout.
5. Parse response and map into `ResponseEnvelope`.
6. Log and audit success/failure metadata.

## Security Requirements
1. Enforce HTTPS-only base URL.
2. Never hardcode API keys; load from environment/secret provider.
3. Redact secrets in logs and errors.
4. Support request integrity extension point (HMAC/signature hook).

## Error Handling Model
- `VectorVueConfigError`: invalid/missing configuration.
- `VectorVueTransportError`: connection/timeout/TLS failure.
- `VectorVueAPIError`: non-2xx API responses.
- `VectorVueSerializationError`: invalid payload encoding.

## Test Strategy
1. Unit test config validation and HTTPS enforcement.
2. Unit test response mapping and exception paths.
3. Unit test retry/backoff decision behavior.
4. Contract test payload schemas against fixture samples.

## Compatibility Notes
- Python 3.12+
- `requests` session-based client initially; can upgrade to async client later.
