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

# Mutual Attestation and Ephemeral Key Derivation

## 1. Scope

Sprint 35 extends runner trust with:
- TPM identity evidence contract
- per-execution key derivation
- runner-control-plane mutual attestation
- multi-tenant isolation stress validation

## 2. Core Module

- `src/pkg/runner/attestation.py`

Primary classes:
- `TPMIdentityProvider`
- `EphemeralKeyDeriver`
- `MutualAttestationService`
- `MultiTenantIsolationStressValidator`

## 3. Execution Path Integration

Firecracker backend (`src/pkg/runner/universal.py`) now emits:
- `execution_metadata.tpm_identity`
- `execution_metadata.ephemeral_key`
- `execution_metadata.mutual_attestation`
- existing runtime attestation report

Mutual attestation failures are terminal and block execution.

## 4. Tenant Isolation Validation

Stress validator rejects session binding reuse across tenants by detecting identical `session_binding_hash` values mapped to different tenant identifiers.

## 5. Validation Commands

```bash
PYTHONPATH=src .venv/bin/pytest -q \
  tests/unit/test_runner_attestation.py \
  tests/unit/test_universal_edge_runner.py \
  tests/qa/test_sprint35_mutual_attestation_qa.py
```

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
