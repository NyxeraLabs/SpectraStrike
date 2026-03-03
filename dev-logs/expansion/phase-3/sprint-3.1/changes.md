# Phase 3 Sprint 3.1 Changes

## File-by-file change explanation

### `VectorVue/services/control_modeling.py`
- Added `ControlVendor` table model.
- Added `ControlInstance` table model.
- Added `ControlType` enum.
- Added `DetectionEvent` table model.
- Added alert normalization adapter layer.
- Added alert severity normalization.
- Added detection-to-technique mapping logic.
- Added vendor performance comparison support.

### `VectorVue/tests/unit/test_phase3_sprint31_control_modeling.py`
- Added detection normalization tests:
  - severity canonicalization cases
  - ATT&CK extraction from payload and free text
  - signature-based ATT&CK mapping
  - vendor comparison metrics ranking

### `SpectraStrike/docs/expansion/phase-3/sprint-3.1/control_modeling.md`
- Added Sprint 42 technical documentation and normalization rules.

### `SpectraStrike/docs/ROADMAP_EXPANSION.md`
- Marked Sprint 42 checklist items complete.

## Reason for each change
- Fulfill Sprint 42 requirements for control modeling, normalized detection events, ATT&CK mapping, and vendor performance analytics.
