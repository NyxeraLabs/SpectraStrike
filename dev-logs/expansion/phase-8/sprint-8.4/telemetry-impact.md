# Telemetry Impact - Phase 8 Sprint 8.4

## New fields introduced
- No ingestion contract fields added.
- New UI-level Nexus context query fields introduced:
  - `nexus_v`
  - `tenant_id`
  - `tenant_name`
  - `role`
  - `campaign_id` (optional)
  - `finding_id` (optional)
  - `ts`

## Fields now populated
- Cross-product deep links now carry campaign/finding/role context for drill-down continuity.

## Impact on ingestion pipeline
- No pipeline ingestion changes.
- Context synchronization occurs at route/query layer only.
