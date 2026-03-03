# Sprint 49: Coverage Analytics

## ATT&CK heatmap generator
- Implemented `generate_attack_heatmap(...)` in `CoverageAnalyticsService`.
- Produces tactic-to-technique heatmap with normalized coverage scores.
- Supports unmapped techniques via `UNMAPPED` bucket.

## Technique-level coverage score
- Implemented `technique_level_coverage_score(...)`.
- Per-technique score built from:
  - confidence score
  - maturity index
  - detection presence
  - execution-volume bonus

## Tactic-level coverage score
- Implemented `tactic_level_coverage_score(...)`.
- Aggregates technique coverage by tactic mapping.

## Detection effectiveness index
- Implemented `detection_effectiveness_index(...)`.
- Weighted by per-technique confidence and observed detection presence.

## Control reliability score
- Implemented `control_reliability_score(...)`.
- Combines:
  - control state quality
  - failure-rate penalty
  - observation coverage percent

## Historical trend comparison engine
- Implemented `historical_trend_comparison(...)`.
- Compares first and latest cycle score to classify:
  - `improving`
  - `stable`
  - `regressing`
  - `insufficient_data`

## Executive risk summary builder
- Implemented `executive_risk_summary(...)`.
- Outputs:
  - overall assurance score
  - residual risk score
  - detection effectiveness index
  - control reliability score
  - lowest tactic coverage highlights
  - trend context

## Validation
- Added unit tests for:
  - heatmap + tactic/technique scoring
  - detection effectiveness + control reliability bounds
  - historical trend and executive summary generation
