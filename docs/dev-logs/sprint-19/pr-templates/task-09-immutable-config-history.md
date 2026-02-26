<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# PR Template - Sprint 19 Task 09

## Task
Implement immutable configuration version history.

## Summary
- Added append-only config history with chained record hashes and duplicate-version rejection.

## Scope
- `src/pkg/orchestrator/control_plane_integrity.py`
- `tests/unit/test_control_plane_integrity.py`

## Validation
- `PYTHONPATH=src .venv/bin/pytest -q tests/unit/test_control_plane_integrity.py -k immutable_history`
