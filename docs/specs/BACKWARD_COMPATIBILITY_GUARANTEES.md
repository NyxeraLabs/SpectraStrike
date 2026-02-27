<!--
Copyright (c) 2026 NyxeraLabs
Author: José María Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# Backward Compatibility Guarantees

Status: Published (Sprint 33)

## 1. Versioning Policy

- Major version changes indicate breaking changes.
- Minor/Patch updates in major `1` MUST remain backward compatible unless explicitly documented as exception.

## 2. Execution Manifest Guarantees

- `manifest_version` major `1` payloads remain supported within policy range.
- Canonical serialization and deterministic hash behavior are stable contracts.
- Required field names and semantics are stable for major `1`.

## 3. Telemetry Contract Guarantees

- Parsers continue supporting CloudEvents + internal + legacy ingestion shapes.
- Normalized canonical fields (`event_type`, `actor`, `target`, `status`, `tenant_id`) are stable.
- Extension fields may grow; existing keys retain semantics.

## 4. Capability Policy Guarantees

- OPA input required fields remain stable for major `1`.
- Added optional fields MUST NOT invalidate existing v1 clients.
- Fail-closed authorization behavior is non-negotiable and stable.

## 5. Federation/Feedback Guarantees

- Signed, mTLS-backed federation paths remain mandatory for trust-critical flows.
- Replay and tenant-bound checks remain mandatory and non-optional.
- Execution fingerprint binding remains invariant for cross-system traceability.

## 6. Deprecation Workflow

Deprecations require:
1. roadmap entry
2. published migration note
3. overlap period with tests covering old and new shapes
4. explicit removal sprint marker
