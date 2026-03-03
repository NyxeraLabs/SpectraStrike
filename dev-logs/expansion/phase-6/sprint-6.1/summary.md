# Phase 6 Sprint 6.1 Summary

## Sprint objective
- Deliver ATT&CK-native coverage analytics and executive risk summarization capabilities.

## Architectural decisions
- Added dedicated analytics service `VectorVue/services/coverage_analytics.py`.
- Reused existing ATT&CK tactic inference (`infer_default_tactic_ids`) and technique-scoring outputs as primary input contracts.
- Modeled calculations as deterministic pure-service functions for repeatable cycle-over-cycle comparisons.

## Risk considerations
- Tactic mapping fallback relies on heuristic prefix mapping when explicit mapping is missing.
  - Mitigation: service accepts explicit `technique_to_tactic` mappings to override defaults.
- Scores are policy-calibrated and may need tuning for organization-specific baselines.
  - Mitigation: scoring formulas are centralized and regression-tested.
