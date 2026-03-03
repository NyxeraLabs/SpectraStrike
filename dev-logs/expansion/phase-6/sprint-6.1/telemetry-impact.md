# Phase 6 Sprint 6.1 Telemetry Impact

## New fields introduced
- No telemetry gateway contract changes in this sprint.
- New analytics outputs derived from existing telemetry-derived coverage/control data:
  - tactic/technique coverage scores
  - detection effectiveness index
  - control reliability score
  - assurance trend deltas

## Fields now populated
- Existing technique scoring fields (`confidence_score`, `maturity_index`, detection flags) now feed normalized ATT&CK heatmap and executive risk outputs.

## Impact on ingestion pipeline
- No breaking ingestion changes.
- Provides downstream reporting and assurance workflows with deterministic analytics artifacts.
