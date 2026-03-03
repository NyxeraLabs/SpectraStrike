# Sprint 46: ASM to Adversary Bridge

## Exposure-to-technique mapping engine
- Added `AsmAdversaryBridgeService.map_exposure_to_techniques(...)`.
- Maps normalized exposure service context and misconfigurations into ATT&CK techniques.
- Includes fallback mapping when no direct match is available.

## Initial access probability scoring
- Added `initial_access_probability(...)` bounded to `0..1`.
- Inputs:
  - exposure severity
  - public exposure flag
  - exploitability flag
  - misconfiguration count
  - mapped technique breadth

## Automated attack path builder
- Added `build_attack_path(tenant_id, exposures)`.
- Selects highest-probability exposure candidates and generates ordered technique steps.
- Emits deterministic path identity and path metadata.

## AttackSurfaceRisk composite index
- Added `attack_surface_risk_index(tenant_id, exposures)`:
  - initial-access probability mean
  - severity mean
  - exploitability rate
  - public exposure rate
- Returns normalized index `0..1`.

## ASM-driven campaign suggestion engine
- Added `suggest_campaigns(tenant_id, exposures)`:
  - objective synthesis
  - seed path binding
  - technique chain output
  - risk/prioritization fields

## Validation
- Unit tests validate:
  - exposure-to-technique mappings
  - probability scoring ordering and bounds
  - automated attack path generation
  - composite risk index bounds
  - campaign suggestion generation
