<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# PR Template - Sprint 22 Task 01

## Task
Define unified execution fingerprint schema.

## Summary
- Added canonical execution fingerprint schema and validation model.

## Scope
- `src/pkg/orchestrator/execution_fingerprint.py`
- `tests/unit/test_execution_fingerprint.py`

## Validation
- `PYTHONPATH=src .venv/bin/pytest -q tests/unit/test_execution_fingerprint.py`
