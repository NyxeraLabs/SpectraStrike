# Phase 7 Sprint 7.2 Telemetry Impact

## New fields introduced
- No telemetry gateway schema changes in this sprint.
- New derived analytics fields:
  - baseline mean/std per technique
  - detection deviation score
  - weighted anomaly score
  - adjusted ML confidence

## Fields now populated
- Sensor-derived technique event counts can now generate baseline and anomaly intelligence for confidence-aware analytics.

## Impact on ingestion pipeline
- No breaking ingestion contract changes.
- Enhances downstream scoring and risk analytics with behavior-aware confidence adjustment.
