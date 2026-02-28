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
-->

# SpectraStrike UI Architecture and API Contracts (Sprint 9.6 Step 1)
![SpectraStrike Logo](../../ui/web/assets/images/SprectraStrike_Logo.png)


## 1. Scope

This document defines the UI baseline architecture and API contracts for Sprint 9.6 with a strict local-only, dockerized runtime model.

## 2. Dockerized UI Topology

UI components (planned for implementation in next Sprint 9.6 steps):
- `ui-web`: Next.js App Router + Tailwind CSS container.
- `ui-admin`: terminal-based admin UI container for operator workflows.

Traffic model:
1. Operator browser -> `nginx` (TLS edge).
2. `nginx` routes `/ui/*` and `/api/*` to internal services.
3. `ui-web` calls orchestrator API over internal Docker network.
4. `ui-admin` calls orchestrator API over internal Docker network.

Security model:
- No cloud dependencies.
- Internal service access over segmented Docker networks.
- UI services are not directly exposed to host unless explicitly proxied.
- Authn/authz delegated to existing AAA controls in orchestrator.

## 3. UI Service Boundaries

`ui-web` responsibilities:
- Authentication views.
- Operator dashboard shell.
- Telemetry feed visualization.
- Findings/evidence navigation.

`ui-admin` responsibilities:
- Task submission.
- Telemetry watch.
- Manual integration sync triggers.
- Session-oriented terminal operations (`health`, `login`, `demo`, `logout`, `task`, `sync`, `telemetry`, `findings`).

`app` (orchestrator/API) responsibilities:
- Authentication and session/token validation.
- Task orchestration and execution lifecycle.
- Telemetry retrieval and filtering.
- Findings/evidence retrieval.
- Audit and access-control enforcement.

## 4. API Contract Baseline

All endpoints are internal API contracts served by orchestrator and consumed by both UI clients.

### 4.1 Authentication

- `POST /api/v1/auth/login`
  - Request:
    - `username: string`
    - `password: string`
    - `mfa_code?: string`
  - Response:
    - `access_token: string`
    - `expires_at: string (ISO-8601)`
    - `roles: string[]`
    - `Set-Cookie: spectrastrike_session` (`HttpOnly`, `SameSite=Strict`, `Secure`)

- `POST /api/v1/auth/register`
  - Request:
    - `username: string`
    - `full_name: string`
    - `email: string`
    - `password: string`
    - `password_confirm: string`
    - `accepted_license: boolean`
    - `accepted_eula: boolean`
    - `accepted_security_policy: boolean`
    - `registration_token?: string` (required only if server policy enforces it)
  - Response:
    - `status: registered`
    - `user: { id, username, full_name, email, roles, created_at }`

- `POST /api/v1/auth/logout`
  - Request: bearer token
  - Response: `204 No Content`

- `POST /api/v1/auth/demo`
  - Purpose: issue a demo operator session for local development/demo flows.
  - Guard: controlled by `UI_AUTH_ENABLE_DEMO_LOGIN`.
  - Response:
    - `access_token: string`
    - `expires_at: string (ISO-8601)`
    - `roles: string[]`

### 4.2 Dashboard and Telemetry

- `GET /api/v1/dashboard/summary`
  - Response:
    - `open_findings: number`
    - `active_tasks: number`
    - `telemetry_events_24h: number`
    - `last_sync_at: string|null`

- `GET /api/v1/telemetry/events`
  - Query:
    - `source?: nmap|metasploit|manual`
    - `status?: success|failed`
    - `limit?: number`
    - `cursor?: string`
  - Response:
    - `items: TelemetryEvent[]`
    - `next_cursor?: string`

### 4.3 Findings and Evidence

- `GET /api/v1/findings`
  - Query:
    - `severity?: low|medium|high|critical`
    - `status?: open|accepted|resolved`
    - `limit?: number`
    - `cursor?: string`
  - Response:
    - `items: Finding[]`
    - `next_cursor?: string`

- `GET /api/v1/findings/{finding_id}/evidence`
  - Response:
    - `finding_id: string`
    - `evidence: EvidenceItem[]`

### 4.4 Operator Actions

- `POST /api/v1/tasks`
  - Request:
    - `tool: string`
    - `target: string`
    - `parameters: object`
  - Response:
    - `task_id: string`
    - `status: queued|running|completed|failed`

- `POST /api/v1/integrations/metasploit/manual-sync`
  - Request:
    - `actor?: string`
    - `checkpoint_override?: string`
  - Response:
    - `emitted_events: number`
    - `observed_sessions: number`
    - `observed_session_events: number`

## 5. Shared Schema Contracts

`TelemetryEvent`:
- `event_id: string`
- `event_type: string`
- `actor: string`
- `target: string`
- `status: string`
- `timestamp: string (ISO-8601)`
- `attributes: object`

`Finding`:
- `finding_id: string`
- `title: string`
- `severity: low|medium|high|critical`
- `status: open|accepted|resolved`
- `created_at: string (ISO-8601)`
- `updated_at: string (ISO-8601)`

`EvidenceItem`:
- `evidence_id: string`
- `type: log|artifact|command_output|screenshot`
- `content_ref: string`
- `captured_at: string (ISO-8601)`

## 6. Non-Functional Requirements

- Dockerized-only execution for UI and API runtime.
- Internal API latency target: p95 <= 300ms for list endpoints at normal load.
- Cursor-based pagination for telemetry/findings endpoints.
- Every mutation endpoint must emit an audit event.
- API responses must be deterministic and machine-parseable JSON.

## 7. Delivery Note

This is the contract and architecture baseline for Sprint 9.6 Step 1 only.
Implementation of web/admin UI containers and endpoint wiring is tracked in the next Sprint 9.6 items.

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
