<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# PR Template - Sprint 24 Task 05

## Task
Simulate repudiation attempt and validate detection.

## Summary
- Added repudiation simulation test and detection path with audit emission.

## Scope
- `src/pkg/orchestrator/anti_repudiation.py`
- `tests/unit/test_anti_repudiation.py`
- `tests/qa/test_sprint24_anti_repudiation_qa.py`

## Validation
- `PYTHONPATH=src .venv/bin/pytest -q tests/unit/test_anti_repudiation.py tests/qa/test_sprint24_anti_repudiation_qa.py`
