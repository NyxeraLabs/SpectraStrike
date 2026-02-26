<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# PR Template - Sprint 21 Task 01

## Task
Enforce canonical JSON serialization for manifests.

## Summary
- Added canonical serializer utility and manifest-level canonical JSON output.

## Scope
- `src/pkg/orchestrator/manifest.py`
- `tests/unit/test_orchestrator_manifest.py`

## Validation
- `PYTHONPATH=src .venv/bin/pytest -q tests/unit/test_orchestrator_manifest.py -k canonical`
