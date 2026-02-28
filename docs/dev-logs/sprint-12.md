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

# Sprint 12 Engineering Log

## Program Context

- Phase: Phase 4
- Sprint: Sprint 12
- Status: Completed
- Primary Architecture Layers: Universal Runner, Cryptographic Verification, Sandbox Execution

## Architectural Intent

Build the Universal Edge Runner as a cryptographically enforced Go execution path that only runs approved Armory artifacts under isolated sandbox controls.

## Implementation Detail

- Added Go runner module (`src/runner-go`) with:
  - compact JWS verification (`VerifyHS256JWS`),
  - execution output -> CloudEvents mapping (`MapToCloudEvent`),
  - sandbox command contract and execution wrapper.
- Implemented local JWS verification logic:
  - HS256 verification path for deterministic QA and CI validation.
- Implemented signed-tool retrieval policy:
  - runner resolves only `authorized` Armory digests,
  - digest mismatch or missing authorization raises hard failure.
- Implemented sandbox command contract:
  - `--runtime=runsc` (gVisor runtime target),
  - AppArmor security profile pinning,
  - read-only, no-capabilities, no-network defaults.
- Implemented execution output contract:
  - captures `stdout`, `stderr`, `exit_code`,
  - maps to CloudEvents v1.0 payload including `manifest_jws`, `tenant_id`, and task metadata.

## Security and Control Posture

- Runner enforces deny-by-default on missing/invalid signatures and unauthorized digests.
- Tool retrieval and execution are strongly bound to signed manifest hash.
- Output telemetry keeps manifest linkage for non-repudiation traceability.

## QA and Validation Evidence

- Added `tests/unit/test_runner_jws_verify.py` for signature verification and forged-token rejection.
- Added `tests/unit/test_universal_edge_runner.py` for digest authorization and CloudEvents execution contract mapping.

## Risk Register

ES256 verification backend remains pluggable by design and is not hardwired to a single crypto runtime implementation in this sprint.

## Forward Linkage

Sprint 13 executes adversarial QA cases for forged signatures, tampered digests, and telemetry contract integrity.

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
