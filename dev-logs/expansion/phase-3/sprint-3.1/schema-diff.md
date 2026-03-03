# Phase 3 Sprint 3.1 Schema Diff

## Before vs After
- No physical database schema migration was introduced in this sprint.
- New logical table models were implemented as typed service-layer dataclasses:
  - `ControlVendor`
  - `ControlInstance`
  - `DetectionEvent`

## Migration notes
- No migration file required for this sprint because persistence-layer schema remains unchanged.
- If persistence is introduced later, these logical models can map to relational tables without breaking current service contracts.
