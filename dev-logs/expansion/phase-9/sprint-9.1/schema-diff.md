# Schema Diff - Phase 9 Sprint 9.1

## Before vs After
### Before
- Client API query paths relied on existing generic indexes.
- No hardening-specific tenant/composite indexes for some high-frequency client portal query patterns.

### After
- Added guarded migration file: `VectorVue/sql/phase9_hardening.sql`.
- New conditional indexes (created only when expected columns/tables exist):
  - `idx_findings_tenant_visibility_id_desc`
  - `idx_findings_tenant_created_at_desc`
  - `idx_evidence_items_tenant_finding_approval_id_desc`
  - `idx_client_reports_tenant_status_id_desc`
  - `idx_remediation_tasks_tenant_finding_status_id_desc`

## Migration notes
- Migration is backward-compatible and guarded through `information_schema` checks.
- Apply with existing SQL migration runner (`scripts/apply_pg_sql.py`) against PostgreSQL environments.
- No destructive schema changes; indexes only.

## Addendum - 2026-03-03
- No additional DB schema changes were introduced by the VectorVue bridge diagnostic hardening task.
- No DB schema changes were introduced by CI/license stabilization updates.
