<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# PR Template - Sprint 18 Task 05

## Task
Enumerate supply-chain compromise scenarios.

## Summary
- Added STRIDE scenarios for dependency, image, and pipeline compromise (S3/T3/R3/I3/D3/E3).

## Scope
- `docs/THREAT_MODEL.md`

## Validation
- `PYTHONPATH=src .venv/bin/pytest -q tests/qa/test_sprint18_threat_model_qa.py`

## Checklist
- [x] Scenarios documented
- [x] Existing controls referenced
- [ ] Merged into `dev`
