# Phase 5 Sprint 5.2 Schema Diff

## Before vs After
- No physical DB migration was introduced.
- Added logical graph models:
  - `AttackPathRecord`
  - `TechniqueLinkRecord`
  - `IdentityCompromiseChain`

## Migration notes
- No migration file required in this sprint.
- Models are persistence-ready and map naturally to graph/relational tables for future durable storage.
