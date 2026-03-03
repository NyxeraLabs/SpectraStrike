# Phase 5 Sprint 5.1 Schema Diff

## Before vs After
- No physical database migration was applied in this sprint.
- Added logical table models in orchestrator service layer:
  - `PlaybookRecord`
  - `PlaybookStepRecord`
  - `WrapperTemplateRecord`
  - `TechniqueModuleRecord`

## Migration notes
- No migration file required for this sprint.
- Models are persistence-ready and can map to relational tables in future schema migration phases.
