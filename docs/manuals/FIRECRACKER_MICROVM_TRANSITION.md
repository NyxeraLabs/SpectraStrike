<!--
Copyright (c) 2026 NyxeraLabs
Author: José María Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# Firecracker MicroVM Transition Runbook

## 1. Scope

This runbook covers Sprint 34 firecracker runtime integration for SpectraStrike runner execution.

## 2. Modes

- `simulate` mode (default): no host Firecracker dependency required; used for dev/CI.
- `native` mode: requires host Firecracker/jailer and optional KVM enforcement.

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
- Breakout indicators (`--privileged`, host-network/pid style flags) are explicitly blocked in firecracker backend execution path.
- Existing OPA, execution fingerprint, and ledger controls remain mandatory and unchanged.

## 6. Validation Commands

```bash
PYTHONPATH=src .venv/bin/pytest -q \
  tests/unit/test_firecracker_microvm_runner.py \
  tests/unit/test_universal_edge_runner.py \
  tests/qa/test_sprint34_microvm_transition_qa.py
```
