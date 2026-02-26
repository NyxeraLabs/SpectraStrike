<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# PR Template - Sprint 23 Task 02

## Task
Remove legacy direct API emission paths.

## Summary
- Removed bridge fallback branch to direct events/findings endpoints.

## Scope
- `src/pkg/integration/vectorvue/rabbitmq_bridge.py`
- `src/pkg/integration/vectorvue/sync_from_rabbitmq.py`

## Validation
- `PYTHONPATH=src .venv/bin/pytest -q tests/qa/test_sprint23_federation_channel_qa.py`
