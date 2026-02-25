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
This document captures Phase 4 Sprint 11-13 implementation boundaries for Armory registry controls, universal runner verification, and QA gates.

## Armory Workflow
1. Ingest BYOT artifact (`tool_name`, `image_ref`, binary payload).
2. Compute immutable digest (`sha256`).
3. Generate SBOM metadata.
4. Run vulnerability summary pipeline.
5. Generate signing metadata (Cosign/Sigstore-equivalent contract).
6. Require explicit approval before digest becomes execution-authorized.

## Runner Workflow
Runner reference implementation is in Go under `src/runner-go`.

1. Validate compact JWS on edge side.
2. Resolve authorized tool digest from Armory.
3. Enforce exact digest match against signed manifest.
4. Build isolated command contract (`runsc` + AppArmor + read-only + no capabilities + no network baseline).
5. Execute workload and map output to CloudEvents (`stdout`, `stderr`, `exit_code`, `manifest_jws`).

## QA Controls (Sprint 13)
- Forged JWS signatures must fail.
- Tampered tool digests must fail.
- Execution output must map to standardized CloudEvents payload.

## Current Constraints
- HS256 path is fully verified in deterministic QA suites.
- ES256 verifier backend is not yet wired in Go runtime and remains a planned integration task.
