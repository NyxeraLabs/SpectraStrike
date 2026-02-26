<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# PR Template - Sprint 18 Task 04

## Task
Enumerate compromised runner scenarios.

## Summary
- Added STRIDE scenarios for compromised runner conditions (S2/T2/R2/I2/D2/E2).

## Scope
- `docs/THREAT_MODEL.md`

## Validation
- `PYTHONPATH=src .venv/bin/pytest -q tests/qa/test_sprint18_threat_model_qa.py`

## Checklist
- [x] Scenarios documented
- [x] Zero-trust implications captured
- [ ] Merged into `dev`
