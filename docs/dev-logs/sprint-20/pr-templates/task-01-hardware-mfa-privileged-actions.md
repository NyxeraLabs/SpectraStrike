<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# PR Template - Sprint 20 Task 01

## Task
Enforce hardware-backed MFA for privileged actions.

## Summary
- Added hardware assertion verifier hook in privileged AAA authorization.

## Scope
- `src/pkg/security/aaa_framework.py`
- `tests/unit/test_aaa_framework.py`

## Validation
- `PYTHONPATH=src .venv/bin/pytest -q tests/unit/test_aaa_framework.py -k hardware_mfa`
