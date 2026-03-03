# Phase 0 Sprint 0.1 Changes

## File-by-file change explanation

### `SpectraStrike/docs/expansion/phase-0/sprint-0.1/vv_core_model_index.md`
- Added complete table inventory from live vv_core migration materialization.
- Included column counts, outbound FK counts, and non-schema reference counts.

### `SpectraStrike/docs/expansion/phase-0/sprint-0.1/vv_core_er_diagram.md`
- Added Mermaid ER flowchart for all discovered FK relationships.

### `SpectraStrike/docs/expansion/phase-0/sprint-0.1/vv_core_nullable_fields.md`
- Added nullable column inventory per table.

### `SpectraStrike/docs/expansion/phase-0/sprint-0.1/vv_core_fk_relationships.md`
- Added FK edge listing (child/parent columns + update/delete behavior).

### `SpectraStrike/docs/expansion/phase-0/sprint-0.1/vv_core_orphan_unused_models.md`
- Added static "potentially-unused" model analysis based on code token references outside schema declarations.

### `SpectraStrike/docs/expansion/phase-0/sprint-0.1/vv_core_unused_scoring_fields.md`
- Added static low-usage scoring field list.

### `SpectraStrike/docs/expansion/phase-0/sprint-0.1/vv_core_unused_detection_fields.md`
- Added static low-usage detection field list.

### `SpectraStrike/docs/expansion/phase-0/sprint-0.1/vv_core_unused_attack_fields.md`
- Added static low-usage ATT&CK field list.

### `SpectraStrike/docs/expansion/phase-0/sprint-0.1/spectrastrike_to_vectorvue_field_mapping.csv`
- Added source-to-target mapping spreadsheet for core telemetry/security/compliance fields.

### `VectorVue/tests/unit/test_phase0_sprint36_migration_dry_run.py`
- Added dry-run migration idempotency test that initializes vv_core migrations twice and asserts unchanged schema snapshot.

### `SpectraStrike/docs/ROADMAP_EXPANSION.md`
- Marked Sprint 36 commit checklist items as complete (`[x]`).

## Reason for each change
- Deliver all required Sprint 36 audit artifacts.
- Provide evidence-backed model visibility before schema/contract changes.
- Add automated migration safety check to reduce regression risk.
