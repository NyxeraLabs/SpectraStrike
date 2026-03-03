# Phase 3 Sprint 3.2 Schema Diff

## Before vs After
- No physical DB schema migration was introduced.
- Added new logical table model in service layer:
  - `ResponseAction`

## Migration notes
- No migration file required in this sprint.
- If persistence is introduced in subsequent sprints, `ResponseAction` maps directly to a relational incident-response table with timestamp columns and SLA target fields.
