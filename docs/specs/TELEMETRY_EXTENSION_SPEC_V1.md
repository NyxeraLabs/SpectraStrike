<!-- NYXERA_BRANDING_HEADER_START -->
<p align="center">
  <img src="https://docs.nyxera.cloud/assets/img/product-logo.png" alt="SpectraStrike" width="220" />
</p>

<p align="center">
  <a href="https://docs.nyxera.cloud">Docs</a> |
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

# Telemetry Extension Specification v1

Version: `1.0.0`
Status: Published (Sprint 33)

## 1. Purpose

Define normalized telemetry contract across orchestrator, broker, and federation bridge for VectorVue ingestion.

## 2. Supported Input Shapes

- CloudEvents `specversion=1.0`
- Internal telemetry event (`event_type`, `actor`, `target`, `status`)
- Legacy compatibility event (`event`, `result`, `context`)

Reference parser:
- `pkg.orchestrator.telemetry_schema.TelemetrySchemaParser`

## 3. Required Normalized Fields

Canonical event fields after parsing:
- `event_type`
- `actor`
- `target`
- `status`
- `tenant_id`
- `attributes`

## 4. Federation Extension Fields

Outbound federation payload MUST carry:
- `execution_hash` (unified execution fingerprint)
- `tenant_id`
- `operator_id`
- signed metadata and nonce/timestamp fields

Telemetry enrichment fields:
- `mitre_techniques`
- `mitre_tactics`
- `soc2_controls`
- `iso27001_annex_a_controls`
- `nist_800_53_controls`

## 5. Integrity and Trust Requirements

- mTLS MUST be used for federation transport.
- Payload signing MUST be enabled for federation requests.
- Replay detection MUST enforce nonce uniqueness + bounded timestamp freshness.
- Tenant context MUST remain present and unambiguous across parsing and federation.

## 6. Compatibility Notes

- Unknown attributes are preserved in `attributes`.
- Default ATT&CK/compliance mappings are applied when omitted.
- Explicit producer-supplied mappings override defaults when present and valid.

<!-- NYXERA_BRANDING_FOOTER_START -->

---

<p align="center">
  <img src="https://docs.nyxera.cloud/assets/img/nyxera-logo.png" alt="Nyxera Labs" width="110" />
</p>

<p align="center">
  2026 SpectraStrike by Nyxera Labs. All rights reserved.
</p>

<p align="center">
  <a href="https://docs.nyxera.cloud">Docs</a> |
  <a href="https://spectrastrike.nyxera.cloud">SpectraStrike</a> |
  <a href="https://nexus.nyxera.cloud">Nexus</a> |
  <a href="https://nyxera.cloud">Nyxera Labs</a>
</p>
<!-- NYXERA_BRANDING_FOOTER_END -->
