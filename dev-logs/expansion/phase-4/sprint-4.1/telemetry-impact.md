# Phase 4 Sprint 4.1 Telemetry Impact

## New fields introduced
- No telemetry gateway contract changes in this sprint.
- New asset discovery model attributes now available for downstream telemetry joins:
  - `asn`
  - `cloud_provider`
  - `cloud_account_id`
  - `owner_tag`
  - `criticality`
  - normalized source lineage fields

## Fields now populated
- Discovery outputs can now populate normalized domain/IP/cloud asset context.
- Duplicate asset observations across source types are merged into one canonical inventory row.

## Impact on ingestion pipeline
- No breaking ingestion contract changes.
- Enables higher-quality enrichment for subsequent exposure scoring and attack-path generation phases.
