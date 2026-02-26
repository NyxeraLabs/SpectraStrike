<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# PR Template - Sprint 19 Task 07

## Task
Implement runtime binary hash baseline check.

## Summary
- Added startup runtime binary SHA-256 baseline enforcement path.

## Scope
- `src/pkg/orchestrator/control_plane_integrity.py`
- `tests/unit/test_control_plane_integrity.py`

## Validation
- `PYTHONPATH=src .venv/bin/pytest -q tests/unit/test_control_plane_integrity.py -k runtime_binary`
