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

# Firecracker MicroVM Transition Runbook

## 1. Scope

This runbook defines Firecracker as the standard execution backend for tool execution paths.

## 2. Modes

- `simulate` mode (default dev/CI): no host Firecracker dependency required.
- `native` mode (production-hardening): requires host Firecracker/jailer and optional KVM enforcement.

## 3. Runtime Contracts

Core module:
- `src/pkg/runner/firecracker.py`

Runner integration:
- `src/pkg/runner/universal.py`

Attestation output:
- `runtime=firecracker`
- `measurement_hash`
- `isolation_checks`
- `boot_mode` (`snapshot-resume` or `cold-boot`)

## 4. Host Prerequisites for Native Mode

Required:
- `firecracker` binary in PATH
- `jailer` binary in PATH when jailer is enabled
- seccomp hardening level >= 2

Optional (enforced when configured):
- `/dev/kvm` available when `require_kvm=true`

## 5. Security Enforcement

- Native launch mode fails closed if isolation checks fail.
- Breakout indicators (`--privileged`, host-network/pid style flags) are explicitly blocked.
- Existing OPA, execution fingerprint, and ledger controls remain mandatory.

## 6. Validation Commands

```bash
PYTHONPATH=src .venv/bin/pytest -q \
  tests/unit/test_firecracker_microvm_runner.py \
  tests/unit/test_universal_edge_runner.py \
  tests/qa/test_sprint34_microvm_transition_qa.py
```

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
