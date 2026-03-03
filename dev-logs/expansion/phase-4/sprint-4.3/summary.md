# Phase 4 Sprint 4.3 Summary

## Sprint objective
- Convert ASM exposure intelligence into adversary-oriented pathing, risk indexing, and campaign recommendations.

## Architectural decisions
- Added dedicated service `VectorVue/services/asm_adversary_bridge.py`.
- Reused `ExposureFinding` from Sprint 45 as the single input contract for bridge calculations.
- Implemented deterministic mapping/scoring/path generation to keep analytics reproducible across reruns.

## Risk considerations
- ATT&CK mapping heuristics are static and may require domain-specific enrichment over time.
  - Mitigation: mapping tables are centralized and straightforward to extend.
- Current implementation is in-memory and non-persistent.
  - Mitigation: generated outputs are modelized and ready for persistence layer integration.
