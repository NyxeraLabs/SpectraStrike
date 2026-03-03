# Phase 2 Sprint 2.1 Changes

## File-by-file change explanation

### `VectorVue/services/attack_backbone.py`
- Added ATT&CK relational data models:
  - Tactic, Technique, SubTechnique
  - Technique->Tactic mapping
  - Technique->Platform mapping
  - Technique->DataSource mapping
  - Technique->Mitigation mapping
  - Technique->Detection guidance mapping
- Added `AttackBackboneService` with idempotent upsert/link methods.
- Added ATT&CK import pipeline (`import_from_reference`) and sync summary output.
- Added metadata enrichment parser (`parse_technique_metadata`).

### `VectorVue/scripts/import_attack_backbone.py`
- Added CLI automation script for ATT&CK import sync.

### `VectorVue/tests/unit/test_phase2_sprint21_attack_backbone.py`
- Added sync validation tests:
  - tactic/technique/sub-technique import
  - mapping population for platform/data-source/mitigation/detection guidance
  - idempotent re-sync behavior

### `SpectraStrike/docs/expansion/phase-2/sprint-2.1/attack_backbone_relational_layer.md`
- Added sprint architecture and mapping coverage reference.

### `SpectraStrike/docs/ROADMAP_EXPANSION.md`
- Marked Sprint 40 checklist items complete.

## Reason for each change
- Deliver Sprint 40 ATT&CK relational backbone and import/sync validation requirements end-to-end.

### `VectorVue/tests/unit/test_phase2_sprint21_attack_backbone.py` (alignment hardening)
- Added `test_real_reference_file_alignment_is_complete` to validate import covers every ATT&CK ID in `VectorVue/mitre_reference.txt`.
- Added helper to extract expected IDs from canonical reference file.
