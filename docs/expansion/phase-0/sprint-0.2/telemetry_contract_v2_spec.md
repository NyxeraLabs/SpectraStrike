# Sprint 37: Telemetry Contract v2 Specification

## Scope
Defines `schema_version=2.x` telemetry contract for SpectraStrike -> VectorVue ingestion.

## Execution lifecycle enum
- `planned`
- `queued`
- `dispatched`
- `running`
- `succeeded`
- `failed`
- `canceled`

## Lifecycle transition rules
- `planned` -> `queued|canceled`
- `queued` -> `dispatched|canceled`
- `dispatched` -> `running|failed|canceled`
- `running` -> `succeeded|failed|canceled`
- `succeeded|failed|canceled` -> terminal

Invalid transitions are rejected at ingest with HTTP `422` and DLQ publication.

## v2 metadata schema blocks
`payload.attributes.contract_v2` must be an object with the following sections:

1. `execution`
- `execution_id`
- `lifecycle_state`
- `previous_lifecycle_state` (optional)
- `started_at`
- `completed_at` (optional)
- `failure_reason` (optional, only valid when state=`failed`)
- `correlation_id` (optional)

2. `asset`
- `asset_id`
- `asset_ref`
- `hostname` (optional)
- `ip_address` (optional)
- `platform` (optional)
- `environment` (optional)

3. `identity`
- `principal_id`
- `principal_type`
- `privilege_level`
- `account_domain` (optional)

4. `ttp`
- `technique_id` (`T####` or `T####.###`)
- `tactic_id` (`TA####`)
- `subtechnique_id` (optional)
- `procedure` (optional)

5. `detection`
- `detected`
- `detection_source` (optional)
- `detection_latency_seconds` (optional)
- `alert_id` (optional)
- `alert_severity` (optional)

6. `response`
- `responded`
- `response_action` (optional)
- `response_latency_seconds` (optional)
- `contained`
- `containment_latency_seconds` (optional)

7. `control`
- `control_id`
- `control_type`
- `control_vendor` (optional)
- `control_version` (optional)
- `effectiveness_score` (optional, 0.0-1.0)

## Schema versioning
- Backward-compatible mode supports multiple allowed versions via:
  - `VV_TG_ALLOWED_SCHEMA_VERSION` (single legacy value)
  - `VV_TG_ALLOWED_SCHEMA_VERSIONS` (CSV or JSON array)
- Gateway enforces membership in allowed set when `VV_TG_ENFORCE_SCHEMA_VERSION=1`.

## Ingestion validation middleware
Telemetry endpoint middleware (`POST /internal/v1/telemetry`) now enforces:
- `Content-Type: application/json`
- non-empty request body
- max body size `1 MiB`

These checks run before signature and deep schema validation.
