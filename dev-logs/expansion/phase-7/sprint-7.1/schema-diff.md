# Phase 7 Sprint 7.1 Schema Diff

## Before vs After
- No physical DB migration was introduced.
- Added logical sensor runtime models:
  - `SensorTransportConfig`
  - `SensorRuntimeConfig`
  - `TelemetryRecord`
  - `SignedTelemetryBatch`
  - `SensorHealthSnapshot`

## Migration notes
- No migration file required for this sprint.
- Sensor artifacts are runtime-level structures and can later map to durable telemetry spool/state tables if needed.
