<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# PR Template - Sprint 21 Task 03

## Task
Define semantic versioning for manifest schema.

## Summary
- Added schema version policy with semantic version parsing and supported range checks.

## Scope
- `src/pkg/orchestrator/manifest.py`
- `tests/unit/test_orchestrator_manifest.py`

## Validation
- `PYTHONPATH=src .venv/bin/pytest -q tests/unit/test_orchestrator_manifest.py -k version`
