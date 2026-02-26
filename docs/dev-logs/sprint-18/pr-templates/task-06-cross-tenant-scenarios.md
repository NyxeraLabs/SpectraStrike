<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# PR Template - Sprint 18 Task 06

## Task
Enumerate cross-tenant escalation scenarios.

## Summary
- Added STRIDE scenarios for tenant boundary bypass and shared-resource abuse (S4/T4/R4/I4/D4/E4).

## Scope
- `docs/THREAT_MODEL.md`

## Validation
- `PYTHONPATH=src .venv/bin/pytest -q tests/qa/test_sprint18_threat_model_qa.py`

## Checklist
- [x] Cross-tenant scenarios documented
- [x] Tenant isolation risks explicit
- [ ] Merged into `dev`
