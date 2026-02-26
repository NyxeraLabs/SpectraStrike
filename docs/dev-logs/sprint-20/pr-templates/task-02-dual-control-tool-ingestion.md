<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# PR Template - Sprint 20 Task 02

## Task
Implement dual-control approval for tool ingestion.

## Summary
- Added Armory approval quorum enforcement with distinct approvers.

## Scope
- `src/pkg/armory/service.py`
- `tests/unit/test_armory_service.py`

## Validation
- `PYTHONPATH=src .venv/bin/pytest -q tests/unit/test_armory_service.py`
