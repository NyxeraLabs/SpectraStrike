<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# PR Template - Sprint 23 Task 08

## Task
Commit Sprint 23 Federation Channel Enforcement.

## Summary
- Prepared Sprint 23 federation channel enforcement package for signed commit.

## Scope
- `src/pkg/integration/vectorvue/config.py`
- `src/pkg/integration/vectorvue/client.py`
- `src/pkg/integration/vectorvue/rabbitmq_bridge.py`
- `src/pkg/integration/vectorvue/sync_from_rabbitmq.py`
- `tests/unit/integration/test_vectorvue_client.py`
- `tests/unit/integration/test_vectorvue_rabbitmq_bridge.py`
- `tests/qa/test_sprint23_federation_channel_qa.py`
- `docs/ROADMAP.md`
- `docs/dev-logs/sprint-23.md`

## Validation
- `PYTHONPATH=src .venv/bin/pytest -q tests/unit/integration/test_vectorvue_client.py tests/unit/integration/test_vectorvue_rabbitmq_bridge.py tests/qa/test_sprint23_federation_channel_qa.py`
