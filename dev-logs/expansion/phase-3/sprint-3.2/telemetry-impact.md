# Phase 3 Sprint 3.2 Telemetry Impact

## New fields introduced
- No gateway contract changes in this sprint.
- New response-layer fields in `ResponseAction` model:
  - `signal_observed_at`
  - `detected_at`
  - `acknowledged_at`
  - `responded_at`
  - `contained_at`
  - `closed_at`
  - `sla_target_minutes`

## Fields now populated
- SOC/IR metric functions consume and normalize response timing fields for:
  - TTD
  - TTR
  - TTC
  - escalation stage progression
  - SLA breach state

## Impact on ingestion pipeline
- No breaking change to telemetry ingestion contracts.
- Enables downstream SOC effectiveness and IR readiness analytics once response timestamps are fed from orchestration/incident systems.
