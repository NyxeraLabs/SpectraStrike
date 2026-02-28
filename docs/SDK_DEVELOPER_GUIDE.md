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
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# SpectraStrike SDK Developer Guide

## 1. Standardized SDK Contract

All wrappers and runner integrations must follow one contract:

1. Detect tool version.
2. Generate execution fingerprint.
3. Embed attestation measurement hash.
4. Sign payload with Ed25519 only.
5. Emit canonical telemetry through the unified ingestion path.
6. Validate schema before ingestion.
7. Pass unit + smoke + real E2E validation.

## 2. Canonical Telemetry Fields

Required normalized fields:
- `event_type`
- `actor`
- `target`
- `status`
- `tenant_id`
- `attributes.execution_fingerprint`
- `attributes.attestation_measurement_hash`
- `attributes.payload_signature`
- `attributes.payload_signature_algorithm` (`Ed25519`)

## 3. Wrapper SDK Components

- `pkg.wrappers.base.BaseWrapper`
- `pkg.telemetry.sdk`
- `pkg.specs.validation_sdk.validate_telemetry_extension_v1`
- `pkg.orchestrator.telemetry_ingestion.TelemetryIngestionPipeline`

## 4. Runner Standard

Standard execution runtime:
- Firecracker microVM path (`runtime=firecracker`) is the default runner standard.

Standard edge runner implementation:
- Go runner (`src/runner-go`) is the reference edge implementation.

Standard manifest signature verification:
- Compact JWS verified with Ed25519 (`alg=EdDSA`) on edge side.
- Symmetric signing fallback is not permitted in standard path.

## 5. Federation Signing

- Outbound telemetry signing tuple: `{timestamp}.{nonce}.{canonical_payload}`
- Algorithm: Ed25519

## 6. Documentation Requirement Per Wrapper

Each wrapper must include:
- `overview.md`
- `architecture.md` (Mermaid)
- `usage.md`
- `telemetry-schema.md`
- `example-execution.md`
- `signature-verification.md`
- `security-considerations.md`

## 7. Test Gates

Mandatory before wrapper completion:
- Unit tests
- Smoke tests
- Real E2E test (non-dry-run) in controlled environment
- Telemetry schema validation checks

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
