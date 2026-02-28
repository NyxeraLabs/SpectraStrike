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
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# SpectraStrike + VectorVue End User Guide

## 1) Installation (Linux/macOS)

1. Install `git`, `make`, `docker`, and `docker compose`.
2. Clone both repositories side-by-side: `SpectraStrike` and `VectorVue`.
3. In `SpectraStrike`, run `python -m venv .venv && .venv/bin/pip install -r requirements.txt`.
4. In `VectorVue`, install Python dependencies with `pip install -r requirements.txt`.

## 2) Docker Requirements

- Docker Engine 24+
- Docker Compose v2+
- Minimum host: 4 CPU, 8 GB RAM, 20 GB free disk

Validate:

```bash
docker --version
docker compose version
```

## 3) How To Generate Certs

1. Use existing local cert generation in VectorVue deploy assets:
   `ls VectorVue/deploy/certs`
2. Required files:
   `ca.crt`, `server.crt`, `server.key`, `client.crt`, `client.key`
3. Required federation keys:
   `spectrastrike_ed25519.key` and `vectorvue_feedback_ed25519.key`

## 4) How To Start Both Platforms

1. `cd SpectraStrike`
2. `make local-federation-up`
3. Confirm services: `docker compose ps` (in each repo)

The command autoloads gitignored local federation env files and compose override files.

## 5) How To Run First Execution (nmap example)

```bash
cd SpectraStrike
PYTHONPATH=src .venv/bin/python -m pkg.integration.host_integration_smoke \
  --tenant-id 10000000-0000-0000-0000-000000000001 \
  --check-vectorvue
```

## 6) How To Verify Federation Is Active

Check smoke output fields:

- `vectorvue_event_status=accepted`
- `vectorvue_finding_status=accepted`
- `vectorvue_status_poll_status=accepted|partial`

Then inspect `local_docs/audit/final-e2e-asymmetric-*.log`.

## 7) How To View Findings In VectorVue

1. Open VectorVue UI.
2. Login with tenant user credentials.
3. Navigate to findings/risk views.
4. Filter by tenant and latest timestamp.

## 8) How Feedback Loop Works

1. SpectraStrike sends signed execution graph metadata.
2. VectorVue validates signatures and mapping, then computes adjustments.
3. VectorVue returns Ed25519-signed feedback (`kid`, `signature`, `nonce`, `signed_at`).
4. SpectraStrike verifies signature and replay conditions before applying policy changes.

## 9) Troubleshooting

- `401 Invalid telemetry signature`: verify SpectraStrike signing key and VectorVue trusted public key.
- `401 certificate fingerprint mismatch`: update pinned cert hash in local federation env.
- `409 Replay detected`: regenerate nonce; do not reuse request bodies.
- `422 schema version not allowed`: align payload schema to gateway allowed schema.
- `feedback uses unknown key id`: update `VECTORVUE_FEEDBACK_VERIFY_KEYS_JSON` with active `kid`.

## 10) Security Explanation (Plain English)

The platforms trust only requests that pass all checks: mTLS identity, certificate pinning, signature verification, schema checks, and anti-replay logic. If any check fails, the request is rejected and not processed.

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
