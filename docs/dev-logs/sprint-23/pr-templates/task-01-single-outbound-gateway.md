<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# PR Template - Sprint 23 Task 01

## Task
Enforce single outbound telemetry gateway.

## Summary
- Bridge dispatch path now targets only federated telemetry gateway endpoint.

## Scope
- `src/pkg/integration/vectorvue/rabbitmq_bridge.py`
- `src/pkg/integration/vectorvue/client.py`

## Validation
- `PYTHONPATH=src .venv/bin/pytest -q tests/unit/integration/test_vectorvue_rabbitmq_bridge.py`
