<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# PR Template - Sprint 23 Task 05

## Task
Add replay detection validation at producer side.

## Summary
- Added nonce replay validation in bridge dispatch path with TTL-based cache.

## Scope
- `src/pkg/integration/vectorvue/rabbitmq_bridge.py`
- `tests/unit/integration/test_vectorvue_rabbitmq_bridge.py`

## Validation
- `PYTHONPATH=src .venv/bin/pytest -q tests/unit/integration/test_vectorvue_rabbitmq_bridge.py -k replay`
