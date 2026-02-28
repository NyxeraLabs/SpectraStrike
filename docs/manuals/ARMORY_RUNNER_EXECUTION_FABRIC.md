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

You may:
Study
Modify
Use for internal security testing

You may NOT:
Offer as a commercial service
Sell derived competing products
-->

# Armory + Universal Runner Execution Fabric
![SpectraStrike Logo](../../ui/web/assets/images/SprectraStrike_Logo.png)

## Scope
This document captures Armory registry controls and standardized edge-runner execution behavior.

## Armory Workflow
1. Ingest BYOT artifact (`tool_name`, `image_ref`, binary payload).
2. Compute immutable digest (`sha256`).
3. Generate SBOM metadata.
4. Run vulnerability summary pipeline.
5. Generate signing metadata.
6. Require explicit approval before digest becomes execution-authorized.

## Standard Runner Workflow
Primary edge runner reference implementation:
- `src/runner-go`

Standard controls:
1. Verify compact JWS on edge side using Ed25519 (`alg=EdDSA`).
2. Resolve authorized tool digest from Armory.
3. Enforce exact digest match against manifest.
4. Execute via firecracker microVM contract (simulation in dev/CI, native in hardened runtime).
5. Map output to CloudEvents (`stdout`, `stderr`, `exit_code`, `manifest_jws`).

## QA Controls
- Forged Ed25519 JWS signatures must fail.
- Tampered tool digests must fail.
- Execution output must map to standardized CloudEvents payload.

## Current Standardization Status
- Go runner verification path is Ed25519-first.
- Firecracker microVM path is the standard runner backend.
- Wrapper SDK contract remains aligned to telemetry/fingerprint/attestation/signature requirements.

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
