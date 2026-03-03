# Phase 3 Sprint 3.2 Changes

## File-by-file change explanation

### `VectorVue/services/soc_ir_readiness.py`
- Added `ResponseAction` table model.
- Added escalation timeline tracking.
- Added time-to-detect metric.
- Added time-to-respond metric.
- Added time-to-contain metric.
- Added SOC effectiveness index calculation.
- Added IR readiness composite score.
- Added SLA violation detection logic.

### `VectorVue/tests/unit/test_phase3_sprint32_soc_ir_readiness.py`
- Added response timing validation tests:
  - escalation timeline stage ordering
  - TTD/TTR/TTC metric validation
  - SLA violation checks for open timeout and late response
  - SOC/IR score bounds and tenant SLA violation listing

### `SpectraStrike/docs/expansion/phase-3/sprint-3.2/soc_ir_readiness.md`
- Added Sprint 43 technical documentation for model, formulas, and SLA logic.

### `SpectraStrike/docs/ROADMAP_EXPANSION.md`
- Marked Sprint 43 checklist items complete.

## Reason for each change
- Fulfill Sprint 43 requirements for SOC/IR readiness measurement, operational timing observability, and SLA governance.
