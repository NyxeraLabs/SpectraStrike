<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# PR Template - Sprint 23 Task 04

## Task
Enforce signed telemetry requirement (no unsigned fallback).

## Summary
- Federation dispatch now fails closed if signature secret is not configured.

## Scope
- `src/pkg/integration/vectorvue/client.py`
- `tests/unit/integration/test_vectorvue_client.py`

## Validation
- `PYTHONPATH=src .venv/bin/pytest -q tests/unit/integration/test_vectorvue_client.py -k signed`
