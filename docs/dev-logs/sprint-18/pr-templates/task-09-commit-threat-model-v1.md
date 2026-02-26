<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# PR Template - Sprint 18 Task 09

## Task
Commit Threat Model v1.0 document.

## Summary
- Prepared commit package for Sprint 18 threat model deliverables.

## Scope
- `docs/THREAT_MODEL.md`
- `docs/RISK_BACKLOG.md`
- `docs/dev-logs/sprint-18.md`
- `docs/dev-logs/sprint-18/pr-templates/*`
- `tests/qa/test_sprint18_threat_model_qa.py`
- `docs/ROADMAP.md`

## Validation
- `PYTHONPATH=src .venv/bin/pytest -q tests/qa/test_sprint18_threat_model_qa.py`

## Checklist
- [x] Deliverables complete
- [x] QA passing
- [ ] Commit signed and pushed
- [ ] Merged into `dev`
