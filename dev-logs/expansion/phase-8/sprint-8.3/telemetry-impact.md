# Telemetry Impact - Phase 8 Sprint 8.3

## New fields introduced
- None at ingestion contract level.

## Fields now populated
- No new ingestion fields; dashboards compute additional derived metrics from existing fields (`mitre_id`, `cvss_score`, `status`, remediation states).

## Impact on ingestion pipeline
- No ingestion route or schema change.
- UI now surfaces completeness and ATT&CK mapping gaps more explicitly.
