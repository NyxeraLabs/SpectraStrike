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

# Sprint 9.9 Engineering Log

## Program Context

- Phase: Phase 3
- Sprint: Sprint 9.9
- Status: Completed
- Primary Architecture Layers: Reporting / Compliance, Orchestration Pipeline, Detection Engine Access Control

## Architectural Objective

Implement a unified legal acknowledgment and governance enforcement subsystem that works consistently across self-hosted, enterprise on-prem, and SaaS-target design paths, while preserving offline capability and low-coupling integration boundaries.

## Implementation Scope

### Governance Core

- Added legal enforcement service and hooks:
  - `core/governance/legal-enforcement.service.ts`
- Added centralized legal version config:
  - `config/legal.config.ts`
- Implemented environment-aware legal evaluation:
  - `self-hosted` (default)
  - `enterprise`
  - `saas`

### Self-Hosted Persistence Model

- Self-hosted acceptance persisted to:
  - `.spectrastrike/legal/acceptance.json` (local/default execution paths)
- Dockerized runtime persistence hardened to writable path:
  - `/var/lib/spectrastrike/legal/acceptance.json`
  - volume-backed for read-only container compatibility

### Authentication and Access Gating

- Legal gate integrated into auth flow before protected access and demo token issuance.
- Enforced failure model:
  - `LEGAL_ACCEPTANCE_REQUIRED`
- Added legal acceptance write path:
  - `/ui/api/v1/auth/legal/accept`
- Web UI legal acceptance workflow integrated with re-acceptance path.
- Admin TUI/CLI startup flow aligned to legal enforcement status.

### Enterprise and SaaS Readiness

- Enterprise installation-level acceptance schema draft delivered.
- SaaS user-level acceptance schema draft delivered.
- Re-acceptance logic implemented through version comparison against active legal version config.

## QA and Runtime Validation

- Validated legal acceptance endpoint behavior in dockerized runtime.
- Validated persistence behavior under read-only filesystem constraints.
- Hardened legal endpoint error handling with structured failure responses.
- Stabilized `ui-web` healthcheck behavior for `make up` startup sequence.
- Resolved infra startup regressions caused by non-executable mounted scripts in:
  - `rabbitmq`
  - `postgres`
  - `redis`

## Security and Compliance Posture

- Legal acceptance is now an explicit governance control gate in authentication lifecycle.
- Version mismatch invalidates stale acceptance and requires explicit re-acknowledgment.
- Governance subsystem remains local-first, offline-capable, and deployable in air-gapped environments.
- Documentation and governance index updated for auditability and release traceability.

## Documentation Delta

- Updated:
  - `docs/ROADMAP.md`
  - `docs/kanban-board.csv`
  - `README.md`
  - `docs/manuals/QA_RUNBOOK.md`
  - `docs/manuals/USER_GUIDE.md`
  - `docs/dev-logs/INDEX.md`

## Risk and Follow-Up

- Web UI dependency bootstrap constraints from Sprint 9.8 remain environment-dependent and should continue to be tracked until dependency mirror or connected CI lane is available.
- Next sprint should focus on release hardening burn-in for governance + auth integration under expanded regression coverage.


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
