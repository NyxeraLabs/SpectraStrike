<!-- NYXERA_BRANDING_HEADER_START -->
<p align="center">
  <img src="https://docs.nyxera.cloud/assets/img/product-logo.png" alt="SpectraStrike" width="220" />
</p>

<p align="center">
  <a href="https://docs.nyxera.cloud">Docs</a> |
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

# Sprint 11 Engineering Log

## Program Context

- Phase: Phase 4
- Sprint: Sprint 11
- Status: Completed
- Primary Architecture Layers: Armory Registry, Supply-Chain Security, Operator Control Plane

## Architectural Intent

Implement The Armory as an internal immutable tool registry to support BYOT onboarding without trust-on-first-use.

## Implementation Detail

- Added internal OCI registry service (`armory-registry`) in dev/prod compose with immutable semantics (`REGISTRY_STORAGE_DELETE_ENABLED=false`).
- Implemented Python Armory service (`pkg.armory.service`) with deterministic pipeline:
  - artifact digest (`sha256`) calculation,
  - SBOM generation contract,
  - vulnerability scan summary contract,
  - Cosign/Sigstore-equivalent signing metadata generation.
- Implemented file-backed registry persistence (`.spectrastrike/armory/registry.json`) and approval workflow for authorized digests.
- Expanded Web UI Armory controls:
  - ingest endpoint now emits digest metadata,
  - approve endpoint to authorize specific digests,
  - authorized-list endpoint for execution allowlist visibility.
- Expanded Admin TUI with Armory command set:
  - `armory ingest <tool_name> <image_ref>`
  - `armory list`
  - `armory approve <tool_sha256>`

## Security and Control Posture

- Digest-based execution authorization is explicit and deny-by-default.
- Registry modifications are append/replace-by-digest and approval-gated.
- Armory actions remain bound to authenticated UI/TUI session controls.

## QA and Validation Evidence

- Added `tests/unit/test_armory_service.py` for ingest/approve/authorized retrieval behavior.
- Extended TUI and client unit coverage for Armory command flow.

## Risk Register

Current signer and scanner providers are deterministic local adapters pending external Sigstore/Syft/Grype runtime wiring. Contract boundaries are fixed for drop-in replacement.

## Forward Linkage

Sprint 12 consumes authorized Armory digests in the Universal Edge Runner execution path.

<!-- NYXERA_BRANDING_FOOTER_START -->

---

<p align="center">
  <img src="https://docs.nyxera.cloud/assets/img/nyxera-logo.png" alt="Nyxera Labs" width="110" />
</p>

<p align="center">
  2026 SpectraStrike by Nyxera Labs. All rights reserved.
</p>

<p align="center">
  <a href="https://docs.nyxera.cloud">Docs</a> |
  <a href="https://spectrastrike.nyxera.cloud">SpectraStrike</a> |
  <a href="https://nexus.nyxera.cloud">Nexus</a> |
  <a href="https://nyxera.cloud">Nyxera Labs</a>
</p>
<!-- NYXERA_BRANDING_FOOTER_END -->
