# Phase 4 Sprint 4.3 Telemetry Impact

## New fields introduced
- No telemetry gateway schema changes.
- New bridge outputs:
  - mapped ATT&CK technique chains from exposures
  - initial access probabilities
  - attack surface composite risk index
  - campaign suggestion payloads

## Fields now populated
- Exposure metadata from Sprint 45 now maps into adversary strategy primitives.
- Technique chain outputs are now directly derivable from ASM evidence.

## Impact on ingestion pipeline
- No ingestion contract breakage.
- Enables downstream campaign orchestration and scoring engines to consume ASM-derived adversary paths.
