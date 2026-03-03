# Telemetry Impact

## New fields introduced
- `payload.attributes.contract_v2` object (for `schema_version` `2.x`), including:
  - execution metadata
  - asset metadata
  - identity metadata
  - TTP metadata
  - detection metadata
  - response metadata
  - control metadata

## Fields now populated
- Existing `payload.attributes.schema_version` now drives versioned contract enforcement path.

## Impact on ingestion pipeline
- Added v2 contract validation with lifecycle transition checks.
- Added schema allowlist policy (`VV_TG_ALLOWED_SCHEMA_VERSIONS`).
- Added ingress middleware checks (content-type/body/body-size).
- Invalid v2 contracts are rejected with DLQ publication.
