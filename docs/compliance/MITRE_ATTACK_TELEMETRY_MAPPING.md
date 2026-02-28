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

# MITRE ATT&CK Telemetry Mapping (Sprint 32)

This mapping ties SpectraStrike telemetry normalization and federation payloads to ATT&CK-aligned attributes used by downstream analytics.

## Telemetry Contract Alignment

- Event payloads are normalized with deterministic schema fields (`telemetry.ml.v1` path).
- Federation bridge sets ATT&CK fields from event attributes:
  - `mitre_techniques` (default fallback `T1595`)
  - `mitre_tactics` (default fallback `TA0043`)
- Federation bridge also injects compliance control tags into outbound payload attributes:
  - `soc2_controls`
  - `iso27001_annex_a_controls`
  - `nist_800_53_controls`
- Event/finding payloads preserve tenant and execution fingerprint context for traceable ATT&CK analytics.

References:
- `src/pkg/orchestrator/telemetry_ingestion.py`
- `src/pkg/integration/vectorvue/rabbitmq_bridge.py`
- `src/pkg/telemetry/sdk.py`

## Tool/Event to ATT&CK Mapping Baseline

| Tool/Event Pattern | ATT&CK Technique(s) | ATT&CK Tactic(s) | Mapping Source |
| --- | --- | --- | --- |
| `nmap_scan_completed` / network probing | T1595 Active Scanning | TA0043 Reconnaissance | Event defaults and wrapper attributes |
| `metasploit_exploit_completed` | T1059 Command and Scripting Interpreter (context dependent) | TA0002 Execution | Wrapper event metadata + finding normalization |
| `sliver_command_completed` | T1105 Ingress Tool Transfer / operator command channel context | TA0011 Command and Control | Sliver wrapper telemetry attributes |
| `mythic_task_completed` | T1059 Command and Scripting Interpreter (task dependent) | TA0002 Execution | Mythic wrapper task telemetry attributes |
| Generic `PROCESS_ANOMALY` federation event | technique/tactic passed in attributes or fallback | attribute-driven | `vectorvue/rabbitmq_bridge.py` normalization |

## Quality and Integrity Constraints

- Tenant boundary: telemetry/finding payloads remain tenant-scoped.
- Execution integrity: `execution_fingerprint` is carried for deterministic cross-system correlation.
- Signed channel requirement: federation payloads are signed and delivered over mTLS.
- Replay resistance: nonce and timestamp windows enforced on feedback ingestion path.

## Scope Notes

- ATT&CK mapping is a telemetry enrichment baseline for analytics and compliance evidence.
- Operational teams can override with richer per-technique tags in tool-specific output attributes.

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
