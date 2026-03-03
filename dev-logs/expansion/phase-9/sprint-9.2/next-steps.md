# Next Steps - Phase 9 Sprint 9.2

1. Keep this doc set synchronized with endpoint and workflow changes in future phases.
2. Add release checklist automation to verify documentation references before merge.
3. Prepare internal release candidate sign-off using the hardening and runbook criteria.
4. Configure `MSF_RPC_*` values for a resolvable/reachable endpoint so `--check-metasploit-rpc` can pass in local federation E2E.
5. Install and configure `mythic-cli` on the execution host to validate Mythic wrapper path.
6. Extend smoke output with bridge failure-count detail (`bridge_result.failed`) to diagnose `vectorvue_ok=False` when acceptance statuses are present.
