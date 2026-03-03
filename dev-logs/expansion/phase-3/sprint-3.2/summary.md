# Phase 3 Sprint 3.2 Summary

## Sprint objective
- Implement SOC and IR readiness primitives with typed response tracking, timing metrics, and SLA-aware scoring.

## Architectural decisions
- Added dedicated service `VectorVue/services/soc_ir_readiness.py` to isolate response timing analytics from control ingestion.
- Modeled `ResponseAction` as an immutable typed row with strict temporal validation.
- Implemented deterministic scoring formulas (`soc_effectiveness_index`, `ir_readiness_composite_score`) bounded to `0..1`.
- Added explicit SLA breach classifier for both unresolved and late-responded incidents.

## Risk considerations
- In-memory model state is not persisted.
  - Mitigation: stable API supports later DB mapping without caller contract changes.
- Score weights are policy defaults and may require calibration per SOC maturity profile.
  - Mitigation: formulas are centralized and test-covered for deterministic tuning.
