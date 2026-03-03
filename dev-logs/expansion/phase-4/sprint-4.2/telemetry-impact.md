# Phase 4 Sprint 4.2 Telemetry Impact

## New fields introduced
- No telemetry gateway contract changes in this sprint.
- New exposure analytics fields produced in service layer:
  - `severity_score`
  - `misconfigurations`
  - `status`
  - `first_seen_at` / `last_seen_at`
  - `score_history`

## Fields now populated
- Endpoint canonicalization now standardizes protocol/port/service metadata for exposure events.
- Deterministic service fingerprints support stable exposure correlation across repeated scans.

## Impact on ingestion pipeline
- No breaking contract changes.
- Provides structured exposure lifecycle outputs for Phase 4.3 mapping into adversary path and initial-access probability logic.
