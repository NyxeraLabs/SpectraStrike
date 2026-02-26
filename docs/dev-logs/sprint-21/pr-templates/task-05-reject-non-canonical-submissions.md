<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# PR Template - Sprint 21 Task 05

## Task
Reject non-canonical manifest submissions.

## Summary
- Added strict parse-and-validate path and orchestrator runtime method for non-canonical rejection.

## Scope
- `src/pkg/orchestrator/manifest.py`
- `src/pkg/orchestrator/engine.py`
- `tests/unit/test_orchestrator_manifest.py`
- `tests/unit/test_orchestrator_engine_aaa.py`

## Validation
- `PYTHONPATH=src .venv/bin/pytest -q tests/unit/test_orchestrator_manifest.py tests/unit/test_orchestrator_engine_aaa.py`
