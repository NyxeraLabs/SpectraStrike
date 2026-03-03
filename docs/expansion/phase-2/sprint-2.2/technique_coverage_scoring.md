# Sprint 41: Technique Coverage and Scoring

## TechniqueCoverage model
Implemented as `TechniqueCoverage` with fields:
- `technique_id`
- `detection_present`
- `detection_latency_seconds`
- `alert_quality_weight`
- `false_negative_count`
- `execution_count`
- `response_observed`
- `containment_observed`
- `confidence_score`
- `maturity_index`

## Scoring formulas

### Detection latency score
- `1.0` at `<=5s`
- linear decay to `0.0` at `300s`

### False negative score
- `1 - clamp(false_negative_count / execution_count, 0, 1)`

### Technique confidence scoring formula
Weighted sum (0..1):
- detection presence: `0.22`
- latency score: `0.20`
- alert quality: `0.20`
- false negative score: `0.18`
- response observed: `0.10`
- containment observed: `0.10`

### Technique maturity index
Weighted sum (0..1):
- confidence score: `0.55`
- false negative score: `0.25`
- alert quality: `0.10`
- execution stability bonus (`execution_count >= 3`): `0.10`

## Service behavior
- `record_execution` updates coverage and recalculates scores.
- `update_false_negative_count` supports explicit false-negative tracking.
- `summary` emits normalized reporting view for analytics/UI.
