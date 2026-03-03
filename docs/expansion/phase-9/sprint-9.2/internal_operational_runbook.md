# Internal Operational Runbook - Phase 9 Sprint 9.2

## 1. Daily Operational Checks
1. Verify service health for SpectraStrike UI/API and VectorVue API/portal.
2. Confirm legal/auth gate behavior and RBAC on privileged actions.
3. Inspect structured audit logs for failed privileged access attempts.
4. Validate tenant-critical dashboards (workflow, nexus, analytics, risk).

## 2. Release Verification Steps
1. Run SpectraStrike UI unit tests and build.
2. Run VectorVue portal unit tests.
3. Run `SpectraStrike/scripts/rbac_audit.py`.
4. Run `SpectraStrike/scripts/phase9_full_integration_suite.py`.
5. Apply and verify pending DB migrations in staging (including index hardening SQL).

## 3. Incident Triage
- Authentication/authorization failures: validate session token, role, and legal acceptance state.
- Portal/API latency spikes: check request timing headers and backend logs.
- Data visibility anomalies: confirm tenant filters and visibility predicates.
- Export/compliance issues: verify signed envelope generation and audit-session flow.

## 4. Load & Stress Readiness
- Load baseline:
  - `VectorVue/scripts/phase9_load_test.py`
- Stress profile runner:
  - `VectorVue/scripts/phase9_stress_runner.py --profile balanced|read_heavy|burst`

## 5. Change Control
- No production release without:
  - passing integration suite
  - updated sprint logs/docs
  - roadmap completion mark
  - signed commit chain in both repos
