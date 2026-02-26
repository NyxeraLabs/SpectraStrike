<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# PR Template - Sprint 21 Task 04

## Task
Add schema regression validation to CI pipeline.

## Summary
- Added deterministic manifest schema regression script and CI workflow execution step.

## Scope
- `scripts/manifest_schema_regression.py`
- `.github/workflows/lint-test.yml`
- `Makefile`

## Validation
- `PYTHONPATH=src .venv/bin/python scripts/manifest_schema_regression.py`
