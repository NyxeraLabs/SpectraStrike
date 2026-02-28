<!-- NYXERA_BRANDING_HEADER_START -->
<p align="center">
  <img src="https://spectrastrike.nyxera.cloud/branding/spectrastrike-logo.png" alt="SpectraStrike" width="220" />
</p>

<p align="center">
  <a href="https://docs.spectrastrike.nyxera.cloud">Docs</a> |
  <a href="https://spectrastrike.nyxera.cloud">SpectraStrike</a> |
  <a href="https://nexus.nyxera.cloud">Nexus</a> |
  <a href="https://nyxera.cloud">Nyxera Labs</a>
</p>
<!-- NYXERA_BRANDING_HEADER_END -->

<!--
Copyright (c) 2026 NyxeraLabs
Author: José María Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0

You may:
Study
Modify
Use for internal security testing

You may NOT:
Offer as a commercial service
Sell derived competing products
-->

# VectorVue API Client Design (Sprint 4)
![SpectraStrike Logo](../../ui/web/assets/images/SprectraStrike_Logo.png)


## Goal
Define a secure, testable, and extensible Python API client for delivering SpectraStrike telemetry and findings to VectorVue client and integration APIs.

## Scope (Roadmap Alignment)
This design maps to `docs/ROADMAP.md` Phase 3:
- Sprint 4:
  - Implement encrypted data transfer (TLS)
  - Implement retries/backoff
  - Implement event batching
  - Implement message signing for integrity
- Sprint 5:
  - QA test API endpoints
  - Validate encrypted communication
  - Confirm telemetry reaches VectorVue

## API Surface (VectorVue)
Base URL (local default): `https://127.0.0.1`

Authentication:
- `POST /api/v1/client/auth/login`
- Bearer token required on all follow-up calls
- JWT must include `tenant_id`

Primary integration endpoints:
- `POST /api/v1/integrations/spectrastrike/events`
- `POST /api/v1/integrations/spectrastrike/events/batch`
- `POST /api/v1/integrations/spectrastrike/findings`
- `POST /api/v1/integrations/spectrastrike/findings/batch`
- `GET /api/v1/integrations/spectrastrike/ingest/status/{request_id}`

Optional client telemetry endpoint:
- `POST /api/v1/client/events`

## Response Contract
All SpectraStrike integration endpoints return an envelope with:
- `request_id`
- `status` (`accepted | partial | failed | replayed`)
- `data`
- `errors[]`
- optional `signature`

## Proposed Package Layout
- `src/pkg/integration/vectorvue/__init__.py`
- `src/pkg/integration/vectorvue/client.py`
- `src/pkg/integration/vectorvue/config.py`
- `src/pkg/integration/vectorvue/models.py`
- `src/pkg/integration/vectorvue/exceptions.py`

## Primary Interfaces
1. `VectorVueConfig`
- `base_url: str = "https://127.0.0.1"`
- `username: str | None`
- `password: str | None`
- `tenant_id: str | None`
- `token: str | None` (optional pre-provisioned token)
- `timeout_seconds: float = 10.0`
- `verify_tls: bool = True`
- `max_retries: int = 3`
- `backoff_seconds: float = 0.5`
- `max_batch_size: int = 100`
- `signature_secret: str | None`
- `require_https: bool = True`

2. `VectorVueClient`
- `login() -> str`
- `send_event(event: dict[str, Any], idempotency_key: str | None = None) -> ResponseEnvelope`
- `send_events_batch(events: list[dict[str, Any]]) -> ResponseEnvelope`
- `send_finding(finding: dict[str, Any]) -> ResponseEnvelope`
- `send_findings_batch(findings: list[dict[str, Any]]) -> ResponseEnvelope`
- `get_ingest_status(request_id: str) -> ResponseEnvelope`

3. `ResponseEnvelope`
- `request_id: str | None`
- `status: str`
- `data: dict[str, Any] | list[Any] | None`
- `errors: list[dict[str, Any]]`
- `signature: str | None`
- `http_status: int`
- `headers: dict[str, str]`

## Security and Integrity Requirements
1. Enforce HTTPS base URL when `require_https=True`.
2. Use Bearer JWT for all integration/status calls.
3. Support optional HMAC request signing when `signature_secret` is configured:
- `X-Timestamp`
- `X-Signature`
4. Redact credentials/tokens/signatures in logs.
5. Preserve tenant isolation guarantees (treat `404` on status lookup as possible cross-tenant protection behavior).

## Idempotency and Replay Handling
For `POST /events`:
- Include `Idempotency-Key` when provided by caller.
- Same key + same payload: handle replay response (`status=replayed` or header `X-Idempotent-Replay: true`).
- Same key + different payload: map `409` to typed `idempotency_conflict` error.

## Transport and Retry Model
- Use `requests.Session` for connection pooling.
- Retry with bounded exponential backoff for transient failures:
  - connection errors
  - timeouts
  - HTTP `429`, `502`, `503`, `504`
- Do not retry hard validation/auth errors (`400`, `401`, `403`, `404`, `409`, `422`).

## Validation Model
Client-side validation before submit:
- Ensure batch size <= `max_batch_size`.
- Ensure payload JSON-serializable.
- Preserve endpoint-specific required fields as pass-through (server remains source of truth).

Server error model expected:
- `validation_failed`
- `batch_too_large`
- `idempotency_conflict`
- auth guard errors (`401`)

## Logging and Observability
Emit local logs for each outbound request with:
- endpoint
- request_id (when available)
- tenant_id (if configured)
- outcome status
- retry count

Never log raw token, password, or signature material.

## Test Strategy
1. Unit tests:
- config validation (`https`, auth inputs)
- signing header generation
- response envelope parsing
- retry/non-retry matrix
- idempotency replay/conflict behavior
- batch-size guard

2. Integration-style tests (mock transport):
- success for each endpoint
- partial failure batch handling
- ingest status polling parse
- auth failure and validation failure mapping

3. QA hooks (Roadmap Sprint 5):
- smoke script for login + single event + single finding + status poll
- TLS verification mode test (`verify=True` / controlled local cert mode)

Implemented QA hooks:
- Live smoke module: `src/pkg/integration/vectorvue/qa_smoke.py`
- QA test suite entry: `tests/qa/test_vectorvue_api_qa.py`
- Live mode toggle: `VECTORVUE_QA_LIVE=1`

## Compatibility
- Python 3.12+
- `requests`-based sync client initially
- interface keeps room for async transport later

<!-- NYXERA_BRANDING_FOOTER_START -->

---

<p align="center">
  <img src="https://spectrastrike.nyxera.cloud/branding/nyxera-logo.png" alt="Nyxera Labs" width="110" />
</p>

<p align="center">
  2026 SpectraStrike by Nyxera Labs. All rights reserved.
</p>

<p align="center">
  <a href="https://docs.spectrastrike.nyxera.cloud">Docs</a> |
  <a href="https://spectrastrike.nyxera.cloud">SpectraStrike</a> |
  <a href="https://nexus.nyxera.cloud">Nexus</a> |
  <a href="https://nyxera.cloud">Nyxera Labs</a>
</p>
<!-- NYXERA_BRANDING_FOOTER_END -->
