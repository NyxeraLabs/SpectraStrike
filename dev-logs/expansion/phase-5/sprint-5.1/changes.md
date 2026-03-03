# Phase 5 Sprint 5.1 Changes

## File-by-file change explanation

### `SpectraStrike/src/pkg/orchestrator/playbook_engine.py`
- Added `Playbook` table model (`PlaybookRecord`).
- Added `PlaybookStep` table model (`PlaybookStepRecord`).
- Added step ordering constraints.
- Added conditional branching support (`condition_expression`, `next_on_success`, `next_on_failure`).
- Added variable injection/template rendering.
- Added wrapper template registry (`WrapperTemplateRecord`).
- Added reusable technique modules (`TechniqueModuleRecord`).
- Added execution rollback handling and simulation output models.

### `SpectraStrike/src/pkg/orchestrator/__init__.py`
- Exported playbook framework classes and enums for package-level reuse.

### `SpectraStrike/tests/unit/test_playbook_engine.py`
- Added complex multi-step simulation tests validating:
  - ordering validation
  - variable injection
  - wrapper rendering
  - branching behavior
  - rollback on terminal failure

### `SpectraStrike/docs/expansion/phase-5/sprint-5.1/playbook_framework.md`
- Added Sprint 47 architecture and behavior documentation.

### `SpectraStrike/docs/ROADMAP_EXPANSION.md`
- Marked Sprint 47 checklist items complete.

## Reason for each change
- Fulfill Sprint 47 requirements for a production-grade playbook framework ahead of adversary graph modeling in Sprint 48.
