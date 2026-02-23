<!--
Copyright (c) 2026 NyxeraLabs
Author: José María Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# SpectraStrike
![SpectraStrike Logo](ui/web/assets/images/SprectraStrike_Logo.png)

SpectraStrike is an enterprise-grade offensive telemetry intelligence and orchestration platform for authorized security validation programs.

## Executive Summary

SpectraStrike is engineered as a production-capable control plane for:
- autonomous and operator-assisted detection workflows
- real-time telemetry ingestion and normalization
- threat-correlation and evidence navigation
- hardened orchestration and auditability
- compliance-ready export pathways, including VectorVue interoperability

## Current Delivery Status

- Phase 1 completed: repository, CI baseline, local runtime setup.
- Phase 2 completed: orchestrator core, scheduling, telemetry ingestion, AAA enforcement.
- Phase 3 completed through Sprint 9.8:
  - Sprint 9.5 messaging backbone (RabbitMQ, retry, DLQ, idempotency)
  - Sprint 9.6 web UI + admin TUI foundation and command workflows
  - Sprint 9.7 security and container hardening baseline
  - Sprint 9.8 cross-sprint QA consolidation and docs QA automation
- Phase 4+ pending: Cobalt Strike and subsequent wrapper/integration roadmap.

Known open QA blocker (tracked in roadmap/kanban):
- Web UI dependency bootstrap may fail in restricted environments with DNS resolution error to npm registry (`EAI_AGAIN`), which blocks `vitest`/`playwright` execution.

## Platform Architecture

### Control Plane
- `src/pkg/orchestrator/engine.py`
- `src/pkg/orchestrator/task_scheduler.py`
- `src/pkg/orchestrator/event_loop.py`
- `src/pkg/security/aaa_framework.py`
- `src/pkg/orchestrator/audit_trail.py`

### Telemetry and Messaging Plane
- `src/pkg/orchestrator/telemetry_ingestion.py`
- `src/pkg/orchestrator/messaging.py`
- RabbitMQ TLS transport with retry, idempotency, and dead-letter routing.

### Integration Plane
- Nmap and Metasploit wrappers
- Manual Metasploit ingestion connector
- VectorVue client abstraction with security controls and QA hooks

### Operator Experience Plane
- Web console (`ui/web`) with auth, dashboard, telemetry, findings, and evidence navigation
- Admin TUI (`src/pkg/ui_admin`) with task submission, telemetry watch, and integration sync

### Security and Runtime Plane
- Hardened Docker stack (`docker-compose.dev.yml`, `docker-compose.prod.yml`)
- Nginx TLS edge with optional mTLS
- Internal mTLS between application and broker/data services
- Host firewall and egress-allowlist scripts
- Supply-chain controls (SBOM, CVE scan, signature verification)

## Quickstart

```bash
cp .env.example .env
make secrets-init
make tls-dev-cert
make pki-internal
make up
```

UI endpoints:
- `https://localhost:${HOST_PROXY_TLS_PORT:-18443}/ui`
- `https://localhost:${HOST_PROXY_TLS_PORT:-18443}/ui/login`
- `https://localhost:${HOST_PROXY_TLS_PORT:-18443}/ui/dashboard`

Admin TUI:

```bash
make ui-admin-shell
```

## Legal & Governance

- `docs/DISCLAIMER.md`: legal boundaries and operational liability framing.
- `docs/EULA.md`: software license usage terms and constraints.
- `docs/ACCEPTABLE_USE_POLICY.md`: authorized and prohibited security-testing behavior.
- `docs/PRIVACY_POLICY.md`: data handling model across self-hosted and future SaaS.
- `docs/USER_REGISTRATION_POLICY.md`: operator-account policy and registration controls.
- `docs/SECURITY_POLICY.md`: internal security control expectations for platform operations.
- `docs/THREAT_MODEL.md`: threat surfaces, mitigations, and residual-risk posture.
- `docs/ARCHITECTURE_SECURITY_OVERVIEW.md`: layered architecture security controls.
- `docs/COMPLIANCE_STATEMENT.md`: compliance-enablement posture and control boundaries.
- `SECURITY.md`: vulnerability reporting process and security disclosure policy.

## QA and Security Gates

Primary QA execution:

```bash
make test
make test-unit
make test-integration
make test-docker
./.venv/bin/pytest -q tests/qa/test_docs_qa.py
```

Security and policy gates:

```bash
make policy-check
make security-check
make security-gate
make full-regression
```

Web UI QA (dependency-ready environments):

```bash
npm --prefix ui/web install --no-audit --no-fund
npm --prefix ui/web run test:unit
npm --prefix ui/web run test:e2e
```

## Documentation

- Roadmap: `docs/ROADMAP.md`
- Kanban board: `docs/kanban-board.csv`
- Manuals index: `docs/manuals/INDEX.md`
- Sprint engineering logs: `docs/dev-logs/INDEX.md`

## License

Business Source License 1.1 (BSL 1.1). See `LICENSE`.
