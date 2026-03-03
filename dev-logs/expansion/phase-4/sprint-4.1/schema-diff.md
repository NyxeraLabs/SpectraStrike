# Phase 4 Sprint 4.1 Schema Diff

## Before vs After
- No physical database schema migration was added in this sprint.
- Added logical `AssetInventory` model at service layer to represent normalized inventory rows.

## Migration notes
- No DB migration file required for this sprint.
- Future persistence mapping can project `AssetInventory` fields into relational `assets`/`asset_inventory` structures without breaking discovery service callers.
