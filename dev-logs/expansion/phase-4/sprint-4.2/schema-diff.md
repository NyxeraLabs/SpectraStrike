# Phase 4 Sprint 4.2 Schema Diff

## Before vs After
- No physical DB schema migration was introduced.
- Added logical service-layer model:
  - `ExposureFinding`

## Migration notes
- No migration file required in this sprint.
- Future persistence can map `ExposureFinding` lifecycle and scoring fields into relational exposure tables without breaking current service APIs.
