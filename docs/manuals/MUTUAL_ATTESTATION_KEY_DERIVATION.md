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
