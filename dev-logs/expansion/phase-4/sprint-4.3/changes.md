# Phase 4 Sprint 4.3 Changes

## File-by-file change explanation

### `VectorVue/services/asm_adversary_bridge.py`
- Added exposure-to-technique mapping engine.
- Added initial access probability scoring logic.
- Added automated attack path builder.
- Added AttackSurfaceRisk composite index.
- Added ASM-driven campaign suggestion engine.

### `VectorVue/tests/unit/test_phase4_sprint43_asm_adversary_bridge.py`
- Added adversary path auto-generation tests:
  - mapping engine behavior
  - probability scoring validation
  - attack path generation checks
  - composite risk index bounds
  - campaign suggestion output validation

### `SpectraStrike/docs/expansion/phase-4/sprint-4.3/asm_adversary_bridge.md`
- Added Sprint 46 design and algorithm documentation.

### `SpectraStrike/docs/ROADMAP_EXPANSION.md`
- Marked Sprint 46 checklist items complete.

## Reason for each change
- Fulfill Sprint 46 requirements to bridge ASM findings into adversary simulation planning logic.
