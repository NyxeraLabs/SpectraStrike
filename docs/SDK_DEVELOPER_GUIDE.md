<!--
Copyright (c) 2026 NyxeraLabs
Author: Jose Maria Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# SpectraStrike SDK Developer Guide

## Architecture Overview

- Wrappers execute tools and emit normalized telemetry.
- Orchestrator enriches payloads with tenant/operator/policy/attestation context.
- VectorVue client signs payloads and sends over mTLS.
- Feedback responses are verified before policy application.

## How Federation Signing Works

- Outbound: SpectraStrike signs `{timestamp}.{nonce}.{canonical_payload}` with Ed25519.
- Inbound feedback: SpectraStrike verifies Ed25519 signature using `kid`-selected verify key.

## Canonical Telemetry Schema Definition

Required normalized fields include:

- `event_id`, `event_type`, `tenant_id`, `operator_id`
- `attributes.schema_version`
- `attributes.attestation_measurement_hash`
- `attributes.policy_decision_hash`
- `execution_fingerprint`

## How To Extend Tool Wrappers (Metasploit, Sliver, Mythic)

1. Add execution method in wrapper module.
2. Normalize command output into SDK event schema.
3. Attach tenant/operator metadata.
4. Attach `attestation_measurement_hash`.
5. Emit through telemetry ingestion pipeline.

## How To Emit Signed Telemetry

1. Configure `VECTORVUE_FEDERATION_SIGNING_KEY_PATH`.
2. Configure mTLS cert/key and CA file.
3. Use `VectorVueClient.send_federated_telemetry(...)`.
4. Ensure nonces/timestamps are unique and current.

## How To Validate Feedback Signatures

1. Configure `VECTORVUE_FEEDBACK_VERIFY_KEYS_JSON`.
2. Validate `kid`, `signature_algorithm`, `signed_at`, `nonce`, `schema_version`.
3. Verify Ed25519 signature on canonical response tuple.
4. Reject replayed nonce or stale timestamp.

## Test Strategy

- Unit tests for signing, verification, replay, schema validation.
- Integration tests for gateway acceptance/rejection paths.
- Host smoke tests for nmap/metasploit/sliver/firecracker workflows.

## Key Rotation Strategy

- Maintain keyring map: `{kid: public_key_ref}` on verifier side.
- Rotate by adding new key and switching active `kid` on signer side.
- Keep old key for overlap window, then remove.
- Test old/new `kid` handling in CI before cutover.
