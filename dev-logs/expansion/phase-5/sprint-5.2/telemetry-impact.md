# Phase 5 Sprint 5.2 Telemetry Impact

## New fields introduced
- No telemetry gateway schema changes in this sprint.
- New graph reconstruction outputs now available:
  - attack path node and edge sequences
  - technique-link relationships with relation type/weight
  - identity compromise chain lineage

## Fields now populated
- Campaign execution, escalation, and lateral movement records can now be projected into unified graph artifacts.

## Impact on ingestion pipeline
- No breaking ingestion changes.
- Enables downstream analytics/reporting/UI phases to consume graph-native campaign structures.
