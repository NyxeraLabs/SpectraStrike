<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# PR Template - Sprint 19 Task 05

## Task
Automate Vault key rotation workflow.

## Summary
- Added transit key rotation API in signer and workflow automation with version increment checks.

## Scope
- `src/pkg/orchestrator/signing.py`
- `src/pkg/orchestrator/vault_hardening.py`
- `tests/unit/test_orchestrator_signing.py`
- `tests/unit/test_vault_hardening.py`

## Validation
- `PYTHONPATH=src .venv/bin/pytest -q tests/unit/test_orchestrator_signing.py tests/unit/test_vault_hardening.py`
