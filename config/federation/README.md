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
- `VECTORVUE_SIGNATURE_SECRET` (required for signed feedback verification)

Artifact exchange checklist:

1. Place client cert/key/CA files outside git-tracked paths.
2. Deliver SpectraStrike Ed25519 public key to VectorVue.
3. Register cert fingerprint and operator->tenant mapping in VectorVue gateway.
4. Share feedback signing secret with SpectraStrike runtime in a secure secret store.

Sprint 31 cognitive endpoints:

- `POST /internal/v1/cognitive/execution-graph`
- `POST /internal/v1/cognitive/feedback/adjustments/query`

Feedback contract enforcement:

- `signature` (HMAC-SHA256 over canonical adjustment array)
- `signed_at` (unix epoch seconds)
- `nonce` (single-use replay token)
- `schema_version` (`feedback.response.v1`)
- each adjustment includes `execution_fingerprint`, `tenant_id`, `timestamp`, `schema_version`

Local dockerized layout on this host:

- SpectraStrike mTLS client cert/key/CA:
  - `/home/xoce/Workspace/VectorVue/deploy/certs/client.crt`
  - `/home/xoce/Workspace/VectorVue/deploy/certs/client.key`
  - `/home/xoce/Workspace/VectorVue/deploy/certs/ca.crt`
- SpectraStrike federation signing key:
  - `/home/xoce/Workspace/VectorVue/deploy/certs/spectrastrike_ed25519.key`
