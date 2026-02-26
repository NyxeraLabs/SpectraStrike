<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# PR Template - Sprint 22 Task 02

## Task
Generate fingerprint before dispatch.

## Summary
- Added fingerprint generation in VectorVue bridge pre-dispatch path.

## Scope
- `src/pkg/integration/vectorvue/rabbitmq_bridge.py`

## Validation
- `PYTHONPATH=src .venv/bin/pytest -q tests/unit/integration/test_vectorvue_rabbitmq_bridge.py`
