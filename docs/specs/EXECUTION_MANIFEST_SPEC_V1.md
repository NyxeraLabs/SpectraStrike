<!--
Copyright (c) 2026 NyxeraLabs
Author: José María Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# Execution Manifest Specification v1

Version: `1.0.0`
Status: Published (Sprint 33)

## 1. Purpose

The Execution Manifest is the canonical task-authorization payload used for cryptographic endorsement and deterministic execution fingerprint binding.

## 2. Canonical JSON Rules

- Manifest payload MUST be JSON object.
- Serialization MUST be deterministic: sorted keys + compact separators.
- UTF-8 encoding MUST be used for hashing/signing.
- Manifest hash MUST be `sha256(canonical_json)`.

Reference implementation:
- `pkg.orchestrator.manifest.canonical_manifest_json`
- `pkg.orchestrator.manifest.deterministic_manifest_hash`

## 3. Required Fields

Top-level required fields:
- `manifest_version` (semantic version, currently major `1`)
- `issued_at` (ISO-8601)
- `task_context` (object)
- `target_urn` (URN format)
- `tool_sha256` (`sha256:<64 lowercase hex>`)
- `nonce` (8-128 chars `[A-Za-z0-9._:-]`)
- `parameters` (object)

`task_context` required fields:
- `task_id`
- `tenant_id`
- `operator_id`
- `source`
- `action`
- `requested_at`
- `correlation_id`

## 4. Validation Contract

- `target_urn` MUST match `urn:<nid>:<nss>` style format.
- `tool_sha256` MUST match exact lowercase SHA-256 format.
- `manifest_version` MUST satisfy semver and supported policy window.
- Non-canonical submissions MUST be rejected.

Reference validator path:
- `pkg.orchestrator.manifest.parse_and_validate_manifest_submission`

## 5. Security Binding

Manifest fields participate in:
- pre-sign OPA capability authorization
- JWS signing in control plane
- unified execution fingerprint generation
- Merkle ledger append-only intent/evidence chain

## 6. Example (Canonical JSON)

```json
{"issued_at":"2026-02-27T00:00:05+00:00","manifest_version":"1.0.0","nonce":"nonce-0001","parameters":{"ports":[443]},"target_urn":"urn:target:ip:10.0.0.5","task_context":{"action":"run","correlation_id":"bc8d85ff-31f2-4b57-9adf-3ce24227de97","operator_id":"op-001","requested_at":"2026-02-27T00:00:00+00:00","source":"api","task_id":"task-001","tenant_id":"tenant-a"},"tool_sha256":"sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}
```
