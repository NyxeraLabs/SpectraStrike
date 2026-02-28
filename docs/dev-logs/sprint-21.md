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

# Sprint 21 Engineering Log

## Program Context

- Phase: Phase 5.5
- Sprint: Sprint 21
- Status: Completed
- Primary Architecture Layers: Control Plane, Identity and Policy Plane

## Architectural Intent

Enforce deterministic execution guarantees for manifest serialization, hashing, and schema compatibility.

## Implementation Detail

Completed Sprint 21 controls:
- Added canonical JSON serialization API for execution manifests.
- Added deterministic SHA-256 manifest hashing API over canonical payloads.
- Added semantic-version policy enforcement for manifest schema versions.
- Added strict parser that rejects non-canonical JSON manifest submissions.
- Added orchestrator runtime validation entrypoint for raw manifest submissions.
- Added schema regression guard script and CI workflow step.

## Security and Control Posture

- Dispatch integrity now relies on deterministic canonical payload and hash behavior.
- Non-canonical manifest submissions are explicitly denied before execution admission.
- Schema version acceptance is bounded by semantic-version compatibility policy.

## QA and Validation Evidence

Commands:
- `PYTHONPATH=src .venv/bin/pytest -q tests/unit/test_orchestrator_manifest.py`
- `PYTHONPATH=src .venv/bin/pytest -q tests/unit/test_orchestrator_engine_aaa.py`
- `PYTHONPATH=src .venv/bin/python scripts/manifest_schema_regression.py`
- `PYTHONPATH=src .venv/bin/pytest -q tests/qa/test_sprint21_deterministic_manifest_qa.py`

## Risk Register

Residual risk:
- Canonical-submission enforcement currently applies to explicit parser path and must be enforced at every external ingress route using raw manifest intake.

## Forward Linkage

Sprint 22 proceeds with federation trust closure and unified execution fingerprint binding.

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
