# Phase 0 Sprint 0.2 Changes

## File-by-file change explanation

### `VectorVue/services/telemetry_processing/validator.py`
- Added `ExecutionLifecycle` enum.
- Added transition map and validator (`validate_lifecycle_transition`).
- Added v2 metadata models: execution, asset, identity, ttp, detection, response, control.
- Added `TelemetryContractV2` and `validate_telemetry_contract_v2`.
- Upgraded canonical attribute handling to support nested objects and recursive sanitization for v2 payload blocks.

### `VectorVue/services/telemetry_gateway/main.py`
- Added `allowed_schema_versions` to gateway settings.
- Added env parsing for `VV_TG_ALLOWED_SCHEMA_VERSIONS` (CSV/JSON array fallback to legacy single value).
- Updated schema-version enforcement to allow configured set, not only one value.
- Added telemetry ingestion middleware for content-type/body-size/body-presence checks.
- Added v2 contract validation path for `schema_version` `2.x` with DLQ publication on validation failure.
- Added `allowed_schema_versions` visibility in `/healthz` response.

### `VectorVue/tests/unit/test_phase1_sprint11_telemetry_gateway.py`
- Added v2 payload factory helper.
- Added test for middleware `415` rejection on non-JSON content-type.
- Added test for accepting valid v2 payload with allowed schema versions.
- Added test for rejecting invalid v2 lifecycle transition.

### `SpectraStrike/docs/expansion/phase-0/sprint-0.2/telemetry_contract_v2_spec.md`
- Added contract spec with lifecycle enum, transition rules, metadata block definitions, and middleware/schema-version policy notes.

### `SpectraStrike/docs/ROADMAP_EXPANSION.md`
- Marked Sprint 37 checklist items as completed.

## Reason for each change
- Fulfill Sprint 37 commit objectives with enforceable, typed contract behavior.
- Preserve backward compatibility while introducing v2 contract strictness.
