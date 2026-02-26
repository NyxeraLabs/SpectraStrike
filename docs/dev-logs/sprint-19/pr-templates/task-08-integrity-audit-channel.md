<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# PR Template - Sprint 19 Task 08

## Task
Add tamper-evident audit log channel.

## Summary
- Added hash-chained integrity event channel under `spectrastrike.audit.integrity`.

## Scope
- `src/pkg/logging/framework.py`
- `tests/unit/test_logging_framework.py`

## Validation
- `PYTHONPATH=src .venv/bin/pytest -q tests/unit/test_logging_framework.py`
