# Sprint 42: Control Modeling

## Implemented models
- `ControlVendor` table model for vendor identity and product family.
- `ControlInstance` table model for tenant-scoped deployed control metadata.
- `ControlType` enum:
  - `preventive`
  - `detective`
  - `corrective`
  - `compensating`
- `DetectionEvent` table model for normalized alert records and ATT&CK linkage.

## Alert normalization adapter layer
- Introduced `ControlModelingService.normalize_and_record_detection_event(...)` as the adapter entrypoint.
- Supports heterogeneous vendor payload keys:
  - IDs: `alert_id` or `id`
  - title/name: `title` or `name`
  - severity forms: `severity`, `priority`, or `risk_level`

## Alert severity normalization
- Canonical severity enum: `info`, `low`, `medium`, `high`, `critical`.
- Mapped common vendor variants:
  - `informational`, `info`, `warning`, `moderate`, `severe`, `urgent`
  - `P0..P3`
  - numeric `1..5`
- Unknown severities default to `medium`.

## Detection-to-technique mapping logic
- Technique extraction from:
  - explicit `technique_ids` list
  - free-text in `description`, `rule`, `signature`, and alert title
- Supports ATT&CK IDs `T####` and `T####.###`.
- Added signature/rule lookup registration:
  - `register_detection_to_technique_mapping(signature, technique_ids)`

## Vendor performance comparison support
- Added `compare_vendor_detection_performance(tenant_id=...)`.
- Per-vendor metrics:
  - detection count
  - mapped detection count and mapped rate
  - high/critical alert rate
  - average normalized severity score
- Sorted for comparative analytics by mapped rate and severity score.

## Validation
- Unit tests:
  - severity normalization behavior
  - multi-source ATT&CK mapping extraction
  - signature-based ATT&CK mapping fallback
  - vendor performance comparison output
