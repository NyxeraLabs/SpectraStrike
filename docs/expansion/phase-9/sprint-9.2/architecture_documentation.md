# Architecture Documentation - Phase 9 Sprint 9.2

## 1. Platform Context
- **SpectraStrike**: execution control plane for campaign orchestration, workflow/ASM graphing, and signed execution telemetry.
- **VectorVue**: tenant-safe intelligence and assurance platform for ATT&CK coverage, detection validation, analytics, and compliance outputs.
- **Nexus mode**: cross-product context/deep-link layer that binds campaign, finding, role, and tenant state across both products.

## 2. Runtime Topology
1. Operator accesses SpectraStrike UI (`/ui/dashboard/*`) and executes campaign workflows.
2. SpectraStrike APIs enforce auth, legal policy, and RBAC for control actions.
3. Telemetry and execution outcomes are normalized for downstream ingestion.
4. VectorVue client APIs expose tenant-safe intelligence and assurance views (`/api/v1/client/*`, `/ml/client/*`, `/compliance/*`).
5. Portal UI renders analytics, risk, remediation, and Nexus cross-product drill-down.

## 3. Security Architecture
- Session-token auth with role-aware authorization at sensitive SpectraStrike API routes.
- Legal acceptance enforcement in auth middleware.
- Structured audit logs on privileged actions in SpectraStrike.
- Tenant claim isolation and signed compliance envelope behavior in VectorVue.
- Request-level observability in VectorVue (`x-request-id`, response-time headers).

## 4. Data Flow Domains
- **Execution domain**: campaigns, workflow nodes/edges, run outcomes.
- **Exposure domain**: ASM assets, exposures, pivot paths.
- **Detection domain**: findings, evidence, confidence, latency, false-negative indicators.
- **Assurance domain**: remediation status, SOC metrics, compliance scoring and reports.

## 5. Hardening and Reliability
- Table reflection cache in VectorVue client API to reduce repeated metadata load overhead.
- Guarded DB index migration for key client endpoint query patterns.
- Load/stress tools and integration suite scripts for operational readiness.

## 6. Release Readiness Boundary
A release candidate is considered internally ready when:
- Sprint roadmap items are complete and marked done.
- RBAC audit passes.
- Unit/integration suite passes.
- Hardening migration is applied and query plans are validated.
- Docs and runbooks reflect actual deployed behavior.
