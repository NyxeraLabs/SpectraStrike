<!-- NYXERA_BRANDING_HEADER_START -->
<p align="center">
  <img src="https://spectrastrike.nyxera.cloud/branding/spectrastrike-logo.png" alt="SpectraStrike" width="220" />
</p>

<p align="center">
  <a href="https://docs.spectrastrike.nyxera.cloud">Docs</a> |
  <a href="https://spectrastrike.nyxera.cloud">SpectraStrike</a> |
  <a href="https://nexus.nyxera.cloud">Nexus</a> |
  <a href="https://nyxera.cloud">Nyxera Labs</a>
</p>
<!-- NYXERA_BRANDING_HEADER_END -->

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

<!-- NYXERA_BRANDING_FOOTER_START -->

---

<p align="center">
  <img src="https://spectrastrike.nyxera.cloud/branding/nyxera-logo.png" alt="Nyxera Labs" width="110" />
</p>

<p align="center">
  2026 SpectraStrike by Nyxera Labs. All rights reserved.
</p>

<p align="center">
  <a href="https://docs.spectrastrike.nyxera.cloud">Docs</a> |
  <a href="https://spectrastrike.nyxera.cloud">SpectraStrike</a> |
  <a href="https://nexus.nyxera.cloud">Nexus</a> |
  <a href="https://nyxera.cloud">Nyxera Labs</a>
</p>
<!-- NYXERA_BRANDING_FOOTER_END -->
