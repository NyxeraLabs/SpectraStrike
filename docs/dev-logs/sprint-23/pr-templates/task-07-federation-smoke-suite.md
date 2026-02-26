<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# PR Template - Sprint 23 Task 07

## Task
Add federation smoke test suite.

## Summary
- Added Sprint 23 QA suite validating gateway-only dispatch and legacy path removal signals.

## Scope
- `tests/qa/test_sprint23_federation_channel_qa.py`

## Validation
- `PYTHONPATH=src .venv/bin/pytest -q tests/qa/test_sprint23_federation_channel_qa.py`
