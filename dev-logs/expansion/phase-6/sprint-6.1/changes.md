# Phase 6 Sprint 6.1 Changes

## File-by-file change explanation

### `VectorVue/services/coverage_analytics.py`
- Added ATT&CK heatmap generator.
- Added tactic-level coverage score calculator.
- Added technique-level coverage score calculator.
- Added detection effectiveness index.
- Added control reliability score.
- Added historical trend comparison engine.
- Added executive risk summary builder.

### `VectorVue/tests/unit/test_phase6_sprint61_coverage_analytics.py`
- Added analytics engine validation tests:
  - heatmap generation and score aggregation checks
  - detection/control index range checks
  - trend and executive summary output checks

### `SpectraStrike/docs/expansion/phase-6/sprint-6.1/coverage_analytics.md`
- Added Sprint 49 analytics design and formula documentation.

### `SpectraStrike/docs/ROADMAP_EXPANSION.md`
- Marked Sprint 49 checklist items complete.

## Reason for each change
- Fulfill Sprint 49 requirements for assurance analytics and executive-level coverage/risk reporting.
