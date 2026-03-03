# Sprint 51: Sensor Core

## Cross-platform lightweight agent
- Added `SensorCoreAgent` with runtime platform metadata (`platform_name`, `platform_release`).
- Lightweight in-memory queue + batcher designed for low overhead sensor runtime.

## Secure TLS transport + mutual authentication
- Added `SensorTransportConfig` validation:
  - HTTPS-only endpoint
  - TLS verification required
  - mTLS cert/key/CA required when mutual auth is enabled

## Signed telemetry verification
- Added signed batch envelope `SignedTelemetryBatch`.
- Implemented HMAC-SHA256 signing and verification over canonical batch payloads.

## Telemetry batching support
- Added `SensorBatcher`:
  - max batch size threshold flush
  - interval/force flush support
  - deterministic batch pop behavior

## Sensor health monitoring service
- Added `SensorHealthMonitor` and `SensorHealthSnapshot`.
- Tracks delivery/failure counters, last error, last delivery timestamp, and health state.

## Remote sensor configuration support
- Added `RemoteSensorConfigService`.
- Runtime-safe patch updates for batching/retry/label fields with key allowlist.
- Preserves queued telemetry during config updates.

## Validation
- Ingestion reliability tests validate:
  - retry after transient transport failure
  - signed batch verification
  - batch delivery behavior
  - remote config updates without queue loss
  - TLS/mTLS config validation rules
