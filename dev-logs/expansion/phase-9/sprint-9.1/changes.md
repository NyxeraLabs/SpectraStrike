# Changes - Phase 9 Sprint 9.1

## File-by-file changes
- `SpectraStrike/ui/web/app/lib/auth-store.ts`
  - Added session principals (`userId`, `roles`), role-aware auth validation options, and `forbidden` decision path.
  - Added bootstrap role configuration defaulting to `operator,admin` for hardened admin actions.

- `SpectraStrike/ui/web/app/lib/observability.ts`
  - Added structured API audit logger and centralized auth failure status mapping.

- `SpectraStrike/ui/web/app/api/actions/runner/kill-all/route.ts`
- `SpectraStrike/ui/web/app/api/actions/queue/purge/route.ts`
- `SpectraStrike/ui/web/app/api/actions/auth/revoke-tenant/route.ts`
- `SpectraStrike/ui/web/app/api/actions/armory/approve/route.ts`
  - Added role requirements and structured audit logging hooks.

- `SpectraStrike/ui/web/tests/unit/auth-store.test.ts`
  - Added RBAC enforcement test validating forbidden behavior when role requirements are unmet.

- `SpectraStrike/scripts/rbac_audit.py`
  - Added static RBAC audit script to verify role guards and audit logging in sensitive routes.

- `SpectraStrike/scripts/phase9_full_integration_suite.py`
  - Added cross-repo integration suite runner for SpectraStrike + VectorVue validation.

- `VectorVue/vv_client_api.py`
  - Added HTTP request observability middleware with request-id and response-time headers.
  - Added reflected table cache for query path performance optimization.

- `VectorVue/sql/phase9_hardening.sql`
  - Added guarded index migration targeting high-traffic tenant/client query patterns.

- `VectorVue/scripts/phase9_load_test.py`
  - Added load testing harness with concurrency, latency metrics, and error-rate thresholds.

- `VectorVue/scripts/phase9_stress_profiles.json`
- `VectorVue/scripts/phase9_stress_runner.py`
  - Added profile-driven stress test scenarios and runner.

- `SpectraStrike/docs/ROADMAP_EXPANSION.md`
  - Marked Sprint 58 checklist as complete.

## Reason for each change
- Implement all Sprint 58 hardening commitments with practical runtime safeguards, measurable validation tooling, and backward-compatible DB improvements.
