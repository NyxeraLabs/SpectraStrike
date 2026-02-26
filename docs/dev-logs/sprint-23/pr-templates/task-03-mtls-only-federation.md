<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# PR Template - Sprint 23 Task 03

## Task
Enforce mTLS-only outbound federation.

## Summary
- Added federation precondition checks for TLS verification and mTLS cert/key presence.

## Scope
- `src/pkg/integration/vectorvue/config.py`
- `src/pkg/integration/vectorvue/client.py`
- `tests/unit/integration/test_vectorvue_client.py`

## Validation
- `PYTHONPATH=src .venv/bin/pytest -q tests/unit/integration/test_vectorvue_client.py -k mtls`
