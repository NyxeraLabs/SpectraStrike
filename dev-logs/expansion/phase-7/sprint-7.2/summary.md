# Phase 7 Sprint 7.2 Summary

## Sprint objective
- Add behavioral anomaly and ML confidence primitives on top of sensor telemetry outputs.

## Architectural decisions
- Added dedicated service `VectorVue/services/behavioral_ml.py`.
- Designed deterministic baseline/deviation/anomaly computations for reproducible validation runs.
- Exposed both low-level functions and an end-to-end scoring pipeline for direct integration with analytics/reporting.

## Risk considerations
- Baseline quality is sample-dependent and can bias deviation interpretation.
  - Mitigation: explicit low-sample fallback logic and sample count tracking.
- Anomaly weights are policy settings and can vary by organization threat model.
  - Mitigation: weighting inputs are configurable per-technique/tactic.
