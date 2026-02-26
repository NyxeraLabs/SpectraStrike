<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# PR Template - Sprint 24 Task 02

## Task
Enforce pre-dispatch intent record (write-ahead hash entry).

## Summary
- Added write-ahead execution intent ledger with hash-chained entries and bridge pre-dispatch record call.

## Scope
- `src/pkg/orchestrator/anti_repudiation.py`
- `src/pkg/integration/vectorvue/rabbitmq_bridge.py`
- `tests/unit/test_anti_repudiation.py`

## Validation
- `PYTHONPATH=src .venv/bin/pytest -q tests/unit/test_anti_repudiation.py`
