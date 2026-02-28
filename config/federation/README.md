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

# SpectraStrike Federation Configuration

This folder stores local/operator-managed federation artifacts for the
SpectraStrike -> VectorVue secure telemetry channel.

Do not commit secrets. Private keys and issued certificates are ignored via
`.gitignore` in this directory.

Required runtime values:

- `VECTORVUE_FEDERATION_URL`
- `VECTORVUE_FEDERATION_ENDPOINT`
- `VECTORVUE_FEDERATION_SERVICE_IDENTITY`
- `VECTORVUE_FEDERATION_MTLS_CERT_FILE`
- `VECTORVUE_FEDERATION_MTLS_KEY_FILE`
- `VECTORVUE_FEDERATION_MTLS_CA_FILE`
- `VECTORVUE_FEDERATION_CLIENT_CERT_SHA256`
- `VECTORVUE_FEDERATION_SIGNING_KEY_PATH`
- `VECTORVUE_FEDERATION_SCHEMA_VERSION`
- `VECTORVUE_FEDERATION_ENFORCE_SCHEMA_VERSION`
- `VECTORVUE_FEDERATION_OPERATOR_ID`
- `VECTORVUE_FEEDBACK_VERIFY_KEYS_JSON` (required keyring for signed feedback verification)

Artifact exchange checklist:

1. Place client cert/key/CA files outside git-tracked paths.
2. Deliver SpectraStrike Ed25519 public key to VectorVue.
3. Register cert fingerprint and operator->tenant mapping in VectorVue gateway.
4. Share VectorVue feedback Ed25519 verify key(s) with SpectraStrike runtime keyring.

Sprint 31 cognitive endpoints:

- `POST /internal/v1/cognitive/execution-graph`
- `POST /internal/v1/cognitive/feedback/adjustments/query`

Feedback contract enforcement:

- `signature` (Ed25519 over canonical adjustment array + tenant/timestamp/nonce/schema/kid)
- `signed_at` (unix epoch seconds)
- `nonce` (single-use replay token)
- `kid` (feedback signing key id for rotation)
- `signature_algorithm` (`Ed25519`)
- `schema_version` (`feedback.response.v1`)
- each adjustment includes `execution_fingerprint`, `tenant_id`, `timestamp`, `schema_version`

Local dockerized layout on this host:

- SpectraStrike mTLS client cert/key/CA:
  - `/home/xoce/Workspace/VectorVue/deploy/certs/client.crt`
  - `/home/xoce/Workspace/VectorVue/deploy/certs/client.key`
  - `/home/xoce/Workspace/VectorVue/deploy/certs/ca.crt`
- SpectraStrike federation signing key:
  - `/home/xoce/Workspace/VectorVue/deploy/certs/spectrastrike_ed25519.key`

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
