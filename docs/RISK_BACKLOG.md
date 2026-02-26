<!--
Copyright (c) 2026 NyxeraLabs
Author: José María Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# Sprint 18 Unresolved Risk Backlog

This backlog captures unresolved risks discovered during Sprint 18 Threat Model v1.0.

## Open Risks

| Risk ID | Category | Description | Impact | Planned Mitigation Sprint |
| --- | --- | --- | --- | --- |
| RISK-S18-001 | Configuration integrity | Unsigned runtime configuration may be accepted by control plane startup path. | High | Sprint 19 |
| RISK-S18-002 | Policy integrity | OPA bundle/policy hash not pinned at runtime, allowing stale or swapped policy use. | High | Sprint 19 |
| RISK-S18-003 | Privileged auth | Privileged actions do not enforce hardware-backed MFA. | High | Sprint 20 |
| RISK-S18-004 | Determinism | Manifest canonicalization and stable hashing guarantees are not yet mandatory. | High | Sprint 21 |
| RISK-S18-005 | Supply chain | Build/bootstrap in disconnected environments still has dependency trust gaps. | Medium | Sprint 19 |
| RISK-S18-006 | Multi-tenant isolation | Per-tenant broker resource quotas are not yet enforced for noisy-tenant DoS resistance. | Medium | Sprint 21 |

## Tracking Rules

- Each risk must be closed only with linked code changes, tests, and roadmap checkbox completion.
- Any mitigation without regression tests remains "open".
