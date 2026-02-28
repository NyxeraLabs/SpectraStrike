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

# Runner Standard

## Scope

This manual defines the standard edge-runner baseline used by SpectraStrike.

## Standard Baseline

- Edge runner implementation standard: Go runner (`src/runner-go`)
- Runtime isolation standard: Firecracker microVM backend
- Manifest signature verification standard: Ed25519 (`alg=EdDSA`)
- Telemetry output contract: CloudEvents + manifest binding

## Operational Notes

- Dev/CI can use simulated Firecracker launch behavior.
- Hardened environments should use native Firecracker/jailer mode with host prerequisites.
- Any deviation from this baseline must be explicitly documented and approved.

## Validation Commands

```bash
cd src/runner-go
GOCACHE=../../.gocache go test ./...

cd ../../
PYTHONPATH=src .venv/bin/pytest -q \
  tests/unit/test_universal_edge_runner.py \
  tests/unit/test_firecracker_microvm_runner.py
```

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
