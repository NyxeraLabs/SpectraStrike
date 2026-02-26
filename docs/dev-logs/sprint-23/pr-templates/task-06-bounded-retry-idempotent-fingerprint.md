<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# PR Template - Sprint 23 Task 06

## Task
Implement bounded retry with idempotent fingerprint key.

## Summary
- Federation outbound uses execution fingerprint as idempotency key while reusing bounded client retry policy.

## Scope
- `src/pkg/integration/vectorvue/rabbitmq_bridge.py`
- `src/pkg/integration/vectorvue/client.py`
- `tests/unit/integration/test_vectorvue_rabbitmq_bridge.py`

## Validation
- `PYTHONPATH=src .venv/bin/pytest -q tests/unit/integration/test_vectorvue_rabbitmq_bridge.py`
