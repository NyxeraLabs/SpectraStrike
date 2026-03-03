# Phase 2 Sprint 2.2 Changes

## File-by-file change explanation

### `VectorVue/services/technique_scoring.py`
- Added `TechniqueCoverage` model.
- Added detection presence flag handling.
- Added detection latency calculation logic.
- Added alert quality weight scoring.
- Added false negative tracking.
- Added response observed and containment observed flags.
- Added technique confidence scoring formula.
- Added technique maturity index calculation.

### `VectorVue/tests/unit/test_phase2_sprint22_technique_scoring.py`
- Added scoring regression tests:
  - confidence increases with better detection/response signals
  - false negatives reduce confidence and maturity
  - response/containment flags persist
  - summary shape validation
  - invalid technique input rejection

### `SpectraStrike/docs/expansion/phase-2/sprint-2.2/technique_coverage_scoring.md`
- Added scoring model and formula documentation.

### `SpectraStrike/docs/ROADMAP_EXPANSION.md`
- Marked Sprint 41 checklist items complete.

## Reason for each change
- Fulfill Sprint 41 requirements for technique coverage modeling and quantifiable scoring.
