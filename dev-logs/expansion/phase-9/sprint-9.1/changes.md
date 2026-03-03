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

- `SpectraStrike/src/pkg/integration/vectorvue/exceptions.py`
  - Extended VectorVue transport/API exceptions with retry and request/signature context fields for downstream diagnostics.

- `SpectraStrike/src/pkg/integration/vectorvue/models.py`
  - Added `retry_count` to `ResponseEnvelope` for surfaced request retry observability.

- `SpectraStrike/src/pkg/integration/vectorvue/client.py`
  - Populated per-request retry count on envelopes and propagated retry/signature-state context into API/transport exceptions.

- `SpectraStrike/src/pkg/integration/vectorvue/rabbitmq_bridge.py`
  - Extended bridge drain result with failure diagnostics lists (envelope IDs, reason categories, signature states, retry counts).
  - Added failure categorization logic (`transport_error`, `api_error`, `fingerprint_validation`, `replay_nonce`, etc.).

- `SpectraStrike/src/pkg/integration/host_integration_smoke.py`
  - Added VectorVue failure diagnostic fields to smoke result and printed them in `HOST_SMOKE` output.

- `SpectraStrike/tests/unit/integration/test_vectorvue_rabbitmq_bridge.py`
  - Added assertions for failure diagnostics and transport retry classification.

- `SpectraStrike/tests/unit/test_host_integration_smoke.py`
  - Added assertions that smoke result carries and exposes failed envelope diagnostics.

- `SpectraStrike/docs/ROADMAP_EXPANSION.md`
  - Marked `feat: VectorVue bridge failure diagnostics for E2E audit clarity` as done under Sprint 58.

## Reason for each change
- Implement all Sprint 58 hardening commitments with practical runtime safeguards, measurable validation tooling, and backward-compatible DB improvements.
- Convert ambiguous VectorVue bridge outcomes into machine-parseable audit evidence for E2E verification.
