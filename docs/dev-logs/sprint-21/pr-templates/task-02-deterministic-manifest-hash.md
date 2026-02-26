<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# PR Template - Sprint 21 Task 02

## Task
Implement deterministic manifest hashing validation.

## Summary
- Added deterministic SHA-256 hashing over canonical manifest payloads.

## Scope
- `src/pkg/orchestrator/manifest.py`
- `scripts/manifest_schema_regression.py`
- `tests/unit/test_orchestrator_manifest.py`

## Validation
- `PYTHONPATH=src .venv/bin/python scripts/manifest_schema_regression.py`
