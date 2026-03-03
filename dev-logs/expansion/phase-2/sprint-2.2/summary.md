# Phase 2 Sprint 2.2 Summary

## Sprint objective
- Implement technique coverage and scoring primitives for detection/response effectiveness measurement.

## Architectural decisions
- Added dedicated service `VectorVue/services/technique_scoring.py` rather than embedding formulas in `vv_core.py`.
- Modeled TechniqueCoverage state as typed immutable dataclass records with recalculation on each update.
- Used bounded deterministic formulas and explicit weights for confidence and maturity metrics.

## Risk considerations
- In-memory storage does not persist across restarts.
  - Mitigation: stable model/service interface can be bound to DB persistence later.
- Formula weights are policy decisions and may need calibration.
  - Mitigation: regression tests guarantee deterministic behavior while tuning can be applied centrally.
