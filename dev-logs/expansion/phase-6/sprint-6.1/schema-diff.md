# Phase 6 Sprint 6.1 Schema Diff

## Before vs After
- No physical database schema migration was introduced.
- Added logical analytics model:
  - `TechniqueCoverageMetric` (service-layer aggregation projection)

## Migration notes
- No migration file required in this sprint.
- Analytics outputs are generated in-memory and can be materialized to reporting tables in future phases if needed.
