# Sprint 43: SOC and IR Readiness

## ResponseAction model
Implemented `ResponseAction` as a typed table model with:
- identity: `response_action_id`, `tenant_id`, `detection_event_id`
- ownership: `action_type`, `owner`, `status`
- timing: `signal_observed_at`, `detected_at`, `acknowledged_at`, `responded_at`, `contained_at`, `closed_at`
- policy: `sla_target_minutes`
- metadata: `notes`, `metadata`

## Escalation timeline tracking
- Added `escalation_timeline(response_action_id=...)`.
- Emits ordered stages with timestamps and elapsed minutes from detection:
  - `signal_observed`
  - `detected`
  - `acknowledged`
  - `responded`
  - `contained`
  - `closed`

## Timing metrics
- `time_to_detect_minutes`: `detected_at - signal_observed_at`
- `time_to_respond_minutes`: `responded_at - detected_at`
- `time_to_contain_minutes`: `contained_at - detected_at`

## SOC effectiveness index
- Added `soc_effectiveness_index(tenant_id=...)` with bounded 0..1 score.
- Weighted factors:
  - detection speed (TTD quality): `0.30`
  - response completion rate: `0.30`
  - containment completion rate: `0.20`
  - SLA compliance rate: `0.20`

## IR readiness composite score
- Added `ir_readiness_composite_score(tenant_id=...)`.
- Combines:
  - SOC effectiveness index: `0.60`
  - TTR quality score: `0.20`
  - TTC quality score: `0.20`

## SLA violation detection logic
- Added `detect_sla_violation(response_action_id=..., reference_time=...)`.
- Violation modes:
  - `open_timeout`: unresolved action elapsed beyond SLA target
  - `response_timeout`: responded but response time exceeded SLA target
- Added `list_sla_violations(tenant_id=...)` for tenant-level breach reporting.

## Validation
- Unit tests verify:
  - escalation timeline stage ordering
  - TTD/TTR/TTC metric correctness
  - SLA violation behavior for open and late-response cases
  - SOC and IR score bounds and SLA violation aggregation
