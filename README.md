<!--
Copyright (c) 2026 NyxeraLabs
Author: José María Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# SpectraStrike
![SpectraStrike Logo](ui/web/assets/images/SprectraStrike_Logo.png)


SpectraStrike is a security orchestration platform for controlled offensive-security operations, with AAA enforcement, auditability, and a hardened local Docker runtime.

## Product Positioning

SpectraStrike is designed for boutique security teams that require:
- deterministic operations
- strict access controls
- auditable automation pipelines
- local-first deployment without cloud dependencies

## Current Implemented Scope (as of Sprint 9.7 + Sprint 9.6 Step 2)

- Orchestrator core: scheduler, async runtime, telemetry ingestion, audit trail
- AAA framework: authentication, authorization, accounting
- Tool integrations: Nmap wrapper, Metasploit RPC wrapper, manual Metasploit ingestion
- Messaging backbone: RabbitMQ-first publisher abstraction, retry, DLQ, idempotency
- UI foundation: dockerized Next.js App Router + Tailwind web console (`/ui`)
- Auth + shell views: operator login (`/ui/login`) and dashboard shell (`/ui/dashboard`)
- Telemetry feed view: `/ui/dashboard/telemetry` for Nmap/Metasploit/manual streams
- Findings + evidence navigation: `/ui/dashboard/findings`, `/ui/dashboard/findings/{id}`, `/ui/dashboard/findings/{id}/evidence`
- Web UI action wiring: secure BFF endpoints for tasks/manual sync/telemetry with local fallback
- Responsive UX baseline: mobile-first layouts for login, dashboard, telemetry, findings, and evidence screens
- Hardened Docker stack: app, nginx, rabbitmq, postgres, redis, loki, vector
- Security controls:
  - TLS edge with optional mTLS client verification
  - internal mTLS for app-to-rabbitmq, app-to-postgres, and app-to-redis transport
  - certificate pinning checks (Metasploit + VectorVue clients)
  - host ingress firewall baseline + Docker egress allowlist scripts
  - tamper-evident audit hash chain
  - local supply-chain gate (SBOM, CVE scan, image signing)

## Architecture Summary

- Control Plane: `OrchestratorEngine` + `TaskScheduler` + AAA + audit
- Telemetry Plane: `TelemetryIngestionPipeline` -> `TelemetryPublisher`
- Broker: RabbitMQ (mTLS-enforced)
- Data Services: PostgreSQL + Redis (TLS-only with client certificate verification)
- Edge: Nginx (HTTPS-first)
- Observability: Vector -> Loki
- UI: `ui-web` (Next.js) routed through Nginx at `/ui`

Primary docs:
- `docs/manuals/ORCHESTRATOR_ARCHITECTURE.md`
- `docs/manuals/USER_GUIDE.md`

## Local Deployment (Dockerized)

### 1. Prerequisites

- Docker Engine 24+
- Docker Compose v2
- GNU Make
- OpenSSL (for local cert generation)
- Python 3.12+ (for local test execution)

### 2. Initialize Local Security Material

```bash
cp .env.example .env
make tls-dev-cert
make pki-internal
```

Then replace credential placeholders in:
- `docker/secrets/rabbitmq_password.txt`
- `docker/secrets/postgres_password.txt`

### 3. Start Runtime

```bash
make up
```

Optional tooling profile:

```bash
make up-all
```

### 4. Exposed Host Ports (customizable via `.env`)

- Proxy HTTP redirect: `HOST_PROXY_HTTP_PORT` (default `18080`)
- Proxy HTTPS: `HOST_PROXY_TLS_PORT` (default `18443`)
- PostgreSQL: `HOST_DB_PORT` (default `15432`)
- RabbitMQ management: `HOST_RABBITMQ_MGMT_PORT` (default `15672`)

Only these ports are intentionally exposed from the container network.

## Web Auth

- Login endpoint: `POST /api/v1/auth/login`
- Register endpoint: `POST /api/v1/auth/register`
- Demo endpoint: `POST /api/v1/auth/demo`
- Logout endpoint: `POST /api/v1/auth/logout`
- Protected routes: `/dashboard/*` and UI BFF API endpoints require a valid session.

Default bootstrap user (override via `.env`):
- username: `operator`
- password: `Operator!ChangeMe123`

Registration security:
- Password policy enforced (12+ chars with upper/lowercase, number, symbol).
- License + EULA + Security Policy acceptance is mandatory before registration.
- Optional registration gate token via `UI_AUTH_REGISTRATION_TOKEN`.
- Session cookie security defaults to TLS-only; for plain-http local testing set `UI_AUTH_COOKIE_SECURE=false`.
- Demo shell can be enabled/disabled with `UI_AUTH_ENABLE_DEMO_LOGIN` (default `true` in local dev template).

## Security Operations Commands

```bash
make security-check          # compose validation + pytest
make policy-check            # compose hardening policy checks
make full-regression         # complete QA + security regression gate
make sbom                    # dockerized syft
make vuln-scan               # dockerized grype
make sign-image              # dockerized cosign signing
make verify-sign             # dockerized cosign verify
make backup-all              # postgres + redis backups
```

Host firewall helpers (root required):

```bash
sudo make firewall-apply
sudo make firewall-egress-apply
```

## Remote Integration Defaults

The platform is configured remote-operator-first (not localhost-coupled):
- `MSF_RPC_*`
- `MSF_MANUAL_*`
- `RABBITMQ_*`
- optional pinning: `MSF_RPC_TLS_PINNED_CERT_SHA256`, `VECTORVUE_TLS_PINNED_CERT_SHA256`

See `.env.example` for full variable list.

## Test and QA

```bash
make test
make test-unit
make test-integration
make test-docker
make test-ui
make test-ui-e2e
```

Admin TUI:

```bash
make ui-admin-shell
```

## Pre-commit License Header Enforcement

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

Manual check:

```bash
make license-check
```

## Documentation

- Roadmap: `docs/ROADMAP.md`
- Kanban snapshot: `docs/kanban-board.csv`
- User Guide: `docs/manuals/USER_GUIDE.md`
- Security Policy: `SECURITY.md`

## License

Business Source License 1.1 (BSL 1.1). See `LICENSE`.
