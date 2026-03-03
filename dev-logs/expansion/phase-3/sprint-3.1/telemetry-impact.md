# Phase 3 Sprint 3.1 Telemetry Impact

## New fields introduced
- No new gateway contract fields were added in this sprint.
- New normalized detection event attributes are produced in service-layer records:
  - `normalized_severity`
  - `technique_ids`
  - `vendor_id`
  - `control_instance_id`

## Fields now populated
- ATT&CK technique identifiers can now be populated from:
  - explicit payload lists
  - free-text extraction
  - signature/rule mapping registry
- Severity is now canonicalized for downstream scoring and comparison.

## Impact on ingestion pipeline
- Improves multi-vendor detection consistency before analytics consumption.
- Enables deterministic vendor performance comparisons and stronger ATT&CK coverage attribution.
- Backward compatibility preserved: existing telemetry validation/gateway contracts were not broken.
