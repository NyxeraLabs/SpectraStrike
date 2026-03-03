# Phase 7 Sprint 7.2 Schema Diff

## Before vs After
- No physical DB schema migration was introduced.
- Added logical behavioral/ML models:
  - `TechniqueBaseline`
  - `TechniqueAnomaly`

## Migration notes
- No migration file required in this sprint.
- Models are service-layer analytics projections and can be persisted later if long-term anomaly baselines are required.
