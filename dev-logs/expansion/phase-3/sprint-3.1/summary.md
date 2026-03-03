# Phase 3 Sprint 3.1 Summary

## Sprint objective
- Implement control-domain modeling and normalized detection ingestion primitives for cross-vendor analytics.

## Architectural decisions
- Added dedicated service `VectorVue/services/control_modeling.py` for Sprint 42 scope rather than embedding logic in legacy modules.
- Modeled `ControlVendor`, `ControlInstance`, and `DetectionEvent` as typed dataclass records to provide deterministic table-like structures.
- Introduced canonical `ControlType` and `AlertSeverity` enums to standardize data across heterogeneous sources.
- Implemented explicit adapter method for alert normalization and ATT&CK mapping extraction.

## Risk considerations
- Current implementation is in-memory and non-persistent.
  - Mitigation: service API is stable and can be wired to DB persistence in a follow-up sprint without breaking callers.
- Vendor payload variance can exceed current key mapping assumptions.
  - Mitigation: adapter allows extending mapping keys and signature-based technique lookups deterministically.
