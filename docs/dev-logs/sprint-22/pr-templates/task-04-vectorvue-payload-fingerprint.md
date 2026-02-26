<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# PR Template - Sprint 22 Task 04

## Task
Include fingerprint in telemetry payload to VectorVue.

## Summary
- Bridge payload now includes execution fingerprint in telemetry metadata and federation bundle.

## Scope
- `src/pkg/integration/vectorvue/rabbitmq_bridge.py`
- `src/pkg/integration/vectorvue/client.py`

## Validation
- `PYTHONPATH=src .venv/bin/pytest -q tests/unit/integration/test_vectorvue_client.py tests/unit/integration/test_vectorvue_rabbitmq_bridge.py`
