<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# PR Template - Sprint 18 Task 01

## Task
Perform full STRIDE threat model across all planes.

## Summary
- Added STRIDE-based threat model coverage for Control, Runner, C2, and Vault/HSM planes.

## Scope
- `docs/THREAT_MODEL.md`

## Validation
- `PYTHONPATH=src .venv/bin/pytest -q tests/qa/test_sprint18_threat_model_qa.py`

## Checklist
- [x] Threat model updated
- [x] QA test added
- [ ] Merged into `dev`
