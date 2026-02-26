<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# PR Template - Sprint 19 Task 04

## Task
Implement policy hash mismatch detection.

## Summary
- Added dedicated mismatch denial and integrity audit event emission.

## Scope
- `src/pkg/orchestrator/control_plane_integrity.py`
- `tests/unit/test_control_plane_integrity.py`

## Validation
- `PYTHONPATH=src .venv/bin/pytest -q tests/unit/test_control_plane_integrity.py -k mismatch`
