<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# Full Federation Integration

## Trust Model

- No implicit network trust.
- Trust is established by mTLS identity and Ed25519 signatures.
- Tenant boundaries are explicit and enforced.

## Threat Model

- Payload tampering
- Replay attacks
- Key misuse/rotation drift
- Cross-tenant impersonation
- Redirect/downgrade attempts

## Cryptographic Flows

- SpectraStrike signs telemetry payloads with Ed25519 private key.
- VectorVue verifies against configured SpectraStrike public key.
- VectorVue signs feedback with Ed25519 private key (`kid`).
- SpectraStrike verifies feedback with keyring lookup by `kid`.

## mTLS Handshake Flow

1. SpectraStrike opens TLS session to VectorVue gateway.
2. Client certificate is presented.
3. Gateway checks pinned cert fingerprint for declared service identity.
4. Requests without valid mTLS identity are rejected.

## Signing Flow

1. Canonical JSON serialization.
2. Signature input: `timestamp + nonce + payload` (telemetry).
3. Feedback signature input includes `tenant|signed_at|nonce|schema|kid|canonical_data`.
4. Verification is fail-closed.

## Attestation Propagation

`attestation_measurement_hash` is embedded in:

- Canonical telemetry payload
- Execution fingerprint input
- Finding records
- Policy engine feedback binding
- Signed payloads

## Policy Engine Binding

- Feedback is applied only when signature and replay checks pass.
- Adjustment context includes attestation hash.
- Optional graph anchoring rejects fingerprint/attestation mismatches.

## Replay Protection Model

- Signed timestamp bounded by allowed clock skew.
- Nonce uniqueness enforced with TTL.
- Reused nonce causes hard rejection.

## Failure Modes

- Invalid signature -> `401/serialization error`
- Schema mismatch -> `422`
- Unknown `kid` -> verification failure
- Mapping violation -> `403`
- Replay -> `409`

## Audit Logging Model

- Accept/reject lifecycle events are emitted with request id.
- Signature and mapping failures are logged as security events.
- E2E smoke outputs are stored under `local_docs/audit/`.

## Production Deployment Considerations

- Store Ed25519 keys in HSM/Vault-backed secret stores.
- Rotate certs and signing keys on fixed schedule.
- Enforce per-tenant key domains for large deployments.
- Forward gateway audit logs into immutable SIEM storage.
