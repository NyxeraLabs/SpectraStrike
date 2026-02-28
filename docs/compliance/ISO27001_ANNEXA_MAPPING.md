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

# ISO/IEC 27001 Annex A Mapping (Sprint 32)

This mapping tracks SpectraStrike controls to selected Annex A themes relevant to offensive validation infrastructure.

## Mapping Table

| Annex A Domain | SpectraStrike Control Implementation | Primary Evidence Artifacts |
| --- | --- | --- |
| A.5 Organizational controls | Policy-governed execution with documented governance gates and legal controls | `docs/SECURITY_POLICY.md`, `docs/EULA.md`, `docs/ACCEPTABLE_USE_POLICY.md` |
| A.5.15 Access control | Tenant-aware authorization boundaries and operator capability validation | `src/pkg/aaa/framework.py`, `src/pkg/orchestrator/opa_client.py`, `tests/qa/test_zero_trust_sprint17_qa.py` |
| A.5.17 Authentication information | Managed auth flows, lockout controls, and tenant context propagation | `src/pkg/aaa/framework.py`, `src/pkg/orchestrator/telemetry_ingestion.py` |
| A.8.9 Configuration management | Immutable runtime policies and auditable control-plane configuration checks | `make policy-check`, `tests/qa/test_docs_qa.py`, `docs/manuals/QA_RUNBOOK.md` |
| A.8.15 Logging | Structured telemetry, operator-attributed events, and bridge transaction status | `src/pkg/orchestrator/telemetry_ingestion.py`, `src/pkg/integration/vectorvue/client.py` |
| A.8.16 Monitoring activities | Security gates, regression suites, and operational runbook-driven validation | `docs/manuals/QA_RUNBOOK.md`, `tests/qa/` |
| A.8.24 Use of cryptography | JWS signing, execution fingerprinting, mTLS, signature verification and replay controls | `src/pkg/orchestrator/execution_fingerprint.py`, `src/pkg/integration/vectorvue/client.py`, `docs/WHITEPAPER.md` |
| A.8.25 Secure development lifecycle | Sprint-driven engineering logs, QA evidence, security gate and license governance | `docs/dev-logs/`, `docs/manuals/QA_RUNBOOK.md`, `scripts/check_license_headers.py` |
| A.8.28 Secure coding | Deterministic serialization, explicit input validation, replay and tenant checks | `src/pkg/integration/vectorvue/client.py`, `src/pkg/orchestrator/cognitive_feedback.py` |
| A.8.30 Outsourced development and dependencies | SBOM and vulnerability scan controls for tool ingestion and release workflow | `docs/manuals/QA_RUNBOOK.md`, `docs/manuals/ARMORY_RUNNER_EXECUTION_FABRIC.md` |

## Scope Notes

- Mapping references platform capabilities and evidence paths only.
- Formal Statement of Applicability and certification decisioning remain external audit activities.

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
