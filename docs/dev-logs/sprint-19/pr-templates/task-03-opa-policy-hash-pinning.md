<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# PR Template - Sprint 19 Task 03

## Task
Enforce OPA policy hash pinning.

## Summary
- Added `OPA_POLICY_PINNED_SHA256` startup integrity pin validation.

## Scope
- `src/pkg/orchestrator/control_plane_integrity.py`
- `tests/unit/test_control_plane_integrity.py`

## Validation
- `PYTHONPATH=src .venv/bin/pytest -q tests/unit/test_control_plane_integrity.py -k policy_pin`
