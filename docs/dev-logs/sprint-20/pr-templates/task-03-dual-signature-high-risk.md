<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# PR Template - Sprint 20 Task 03

## Task
Enforce dual-signature for high-risk manifests.

## Summary
- Added high-risk dual-signature orchestrator policy and signature bundle model.

## Scope
- `src/pkg/orchestrator/dual_signature.py`
- `tests/unit/test_orchestrator_dual_signature.py`

## Validation
- `PYTHONPATH=src .venv/bin/pytest -q tests/unit/test_orchestrator_dual_signature.py`
