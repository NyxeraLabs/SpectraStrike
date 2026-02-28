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

# Validation SDK

Status: Published (Sprint 33)
Module: `pkg.specs.validation_sdk`

## 1. Purpose

Provide a lightweight SDK surface for validating:
- execution manifest payloads (v1)
- telemetry extension payloads (v1)
- capability policy input payloads (v1)

## 2. API Surface

- `validate_execution_manifest_v1(payload)`
- `validate_telemetry_extension_v1(payload)`
- `validate_capability_policy_input_v1(payload)`
- `validate_spec_bundle_v1(manifest_payload, telemetry_payload, capability_payload)`

Return model:
- `ValidationResult(ok: bool, errors: list[str], normalized: dict[str, Any] | None)`

## 3. Example

```python
from pkg.specs.validation_sdk import validate_spec_bundle_v1

result = validate_spec_bundle_v1(
    manifest_payload=manifest_payload,
    telemetry_payload=telemetry_payload,
    capability_payload=capability_payload,
)

if not result["manifest"].ok:
    raise RuntimeError(result["manifest"].errors)
```

## 4. Notes

- SDK is deterministic and schema-focused.
- Runtime trust checks (mTLS, signature verification, replay windows) still occur in production control paths.

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
