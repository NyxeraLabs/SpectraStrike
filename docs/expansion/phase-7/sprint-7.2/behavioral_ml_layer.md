# Sprint 52: Behavioral and ML Layer

## Anomaly correlation engine
- Implemented `correlate_anomalies(...)`.
- Correlates repeated technique events by asset and computes normalized correlation scores.

## Behavioral baseline computation
- Implemented `compute_baselines(...)`.
- Produces per-technique baseline metrics:
  - mean daily count
  - standard deviation
  - sample-day count

## Detection deviation scoring
- Implemented `detection_deviation_score(...)`.
- Uses z-score style deviation when baseline quality is sufficient.
- Falls back to ratio-based deviation for low-sample baselines.

## Technique anomaly weighting
- Implemented `technique_anomaly_weight(...)`.
- Combines deviation score with tactic/priority weighting and critical technique boosts.

## ML confidence scoring adjustment
- Implemented `adjust_ml_confidence(...)`.
- Adjusts confidence using:
  - base confidence
  - deviation intensity
  - baseline sample quality factor

## Regression scoring flow
- Implemented `score_current_observations(...)` end-to-end pipeline:
  - baseline lookup
  - deviation calculation
  - weighted anomaly score
  - adjusted confidence output

## Validation
- ML regression validation suite verifies:
  - anomaly correlation behavior
  - baseline + deviation + weighting coherence
  - confidence adjustment and technique ranking stability
