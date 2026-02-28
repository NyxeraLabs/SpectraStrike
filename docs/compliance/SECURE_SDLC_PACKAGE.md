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

# Secure SDLC Documentation Package (Sprint 32)

This package defines how SpectraStrike enforces secure software lifecycle controls as release-gating evidence.

## 1. Governance Model

- Roadmap-driven delivery and control traceability: `docs/ROADMAP.md`
- Task-level tracking and status integrity: `docs/kanban-board.csv`
- Sprint engineering evidence and risk documentation: `docs/dev-logs/`
- Mandatory QA gate orchestration: `docs/manuals/QA_RUNBOOK.md`

## 2. Security Design and Threat Controls

- Threat model and architecture posture:
  - `docs/THREAT_MODEL.md`
  - `docs/WHITEPAPER.md`
  - `docs/ARCHITECTURE_SECURITY_OVERVIEW.md`
- Zero-trust authorization and policy delegation:
  - `src/pkg/orchestrator/opa_client.py`
  - `tests/qa/test_zero_trust_sprint17_qa.py`
- Cryptographic execution integrity and anti-repudiation:
  - `src/pkg/orchestrator/execution_fingerprint.py`
  - `src/pkg/orchestrator/merkle_ledger.py`
  - `src/pkg/orchestrator/anti_repudiation.py`

## 3. Build/Test/Release Security Gates

Minimum release gates:

```bash
make policy-check
make test
make security-check
./.venv/bin/python scripts/check_license_headers.py
./.venv/bin/pytest -q tests/qa/test_docs_qa.py
```

For federation and cognitive integration:

```bash
PYTHONPATH=src .venv/bin/pytest -q \
  tests/unit/integration/test_vectorvue_client.py \
  tests/unit/integration/test_vectorvue_rabbitmq_bridge.py \
  tests/qa/test_sprint30_broker_abstraction_throughput_qa.py \
  tests/qa/test_sprint31_cognitive_feedback_loop_qa.py
```

## 4. Control Evidence Expectations

Each release candidate must retain:
- command transcript summary
- pass/fail QA snapshot
- blocker and remediation linkage
- architecture and policy drift assessment
- compliance mapping snapshot (`docs/compliance/`)

## 5. Supply Chain and Dependency Hygiene

- SBOM and vulnerability scanning are mandatory pre-release controls.
- Tool registry/armory ingestion paths require signing and integrity verification.
- Third-party license boundaries are preserved; local license-header checker applies to in-scope project files only.

## 6. Roles and Responsibilities

- Engineering: implements sprint scope with tests and control references.
- Security: validates policy/security gate outcomes and threat-model consistency.
- QA: executes runbook and captures blocker evidence with reproducible commands.
- Release owner: approves release only when all mandatory gates pass or accepted risk waiver exists.

## 7. Scope Notes

- This package documents platform secure development process.
- External certification/audit outcomes depend on deployment context and organizational controls.

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
