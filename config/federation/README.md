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

Artifact exchange checklist:

1. Place client cert/key/CA files outside git-tracked paths.
2. Deliver SpectraStrike Ed25519 public key to VectorVue.
3. Register cert fingerprint and operator->tenant mapping in VectorVue gateway.
