<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# PR Template - Sprint 19 Task 06

## Task
Harden Vault unseal procedure.

## Summary
- Added unseal policy checks for quorum threshold, uniqueness, and minimum share quality.

## Scope
- `src/pkg/orchestrator/vault_hardening.py`
- `tests/unit/test_vault_hardening.py`

## Validation
- `PYTHONPATH=src .venv/bin/pytest -q tests/unit/test_vault_hardening.py -k unseal`
