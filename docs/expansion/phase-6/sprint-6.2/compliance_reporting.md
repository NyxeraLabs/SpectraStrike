# Sprint 50: Compliance and Reporting

## Framework control mappings
Implemented canonical mappings for:
- `NIST`
- `ISO27001`
- `SOC2`

Each mapping includes:
- internal control id
- external requirement reference
- control title
- control domain

## Automated assurance report generator
- Added `generate_assurance_report(...)`.
- Produces normalized report payload containing:
  - framework metadata
  - period metadata
  - control state summary (operating/degraded/failed)
  - pass rate
  - assurance and residual risk scores
  - analytics context

## Signed audit export package
- Added `build_signed_audit_export_package(...)`.
- Exports:
  - `report.json`
  - `checksums.txt`
  - `signature.txt`
- Package is zip-compressed and signed via HMAC-SHA256.

## Multi-cycle validation comparison
- Added `compare_validation_cycles(...)`.
- Compares assurance/risk deltas across ordered reporting cycles.
- Emits trend classification:
  - `improving`
  - `regressing`
  - `mixed`
  - `insufficient_data`

## Validation
- Added compliance mapping validation tests for:
  - framework mapping coverage
  - assurance report generation and signed export package structure
  - multi-cycle comparison trend logic
