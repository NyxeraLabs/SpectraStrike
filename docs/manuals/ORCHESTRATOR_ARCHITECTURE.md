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

# Orchestrator Architecture (Phase 2 Design)
![SpectraStrike Logo](../../ui/web/assets/images/SprectraStrike_Logo.png)


## Purpose
The orchestrator is the central control plane for SpectraStrike. It coordinates tool wrappers, enforces AAA policy, records audit trails, and publishes telemetry.

## Core Components
1. `OrchestratorEngine`
- Owns runtime lifecycle (`start`, `stop`, `health`).
- Wires scheduler, telemetry pipeline, and policy enforcement.

2. `TaskScheduler`
- Accepts tasks from integrations and manual API.
- Prioritizes and schedules async execution.
- Supports retry policy and failure isolation.

3. `ExecutionWorkers`
- Async workers that execute normalized tool tasks.
- Emit structured execution events for logging and telemetry.

4. `AAAServiceAdapter`
- Wraps `pkg.security.aaa_framework.AAAService`.
- Enforces authentication and role authorization for each action.
- Produces accounting records for all privileged operations.

5. `TelemetryPipeline`
- Normalizes runtime events.
- Buffers and batches telemetry for downstream export.
- Supports secure transport abstraction for VectorVue integration.
- Supports broker-backed async publishing via `TelemetryPublisher`.

6. `AuditLogger`
- Uses `pkg.logging.framework`.
- Writes structured audit events for auth decisions, task execution, and failures.

## Data Contracts
1. `OrchestratorTask`
- `task_id`, `source`, `tool`, `action`, `payload`, `requested_by`, `required_role`.

2. `ExecutionResult`
- `task_id`, `status`, `started_at`, `ended_at`, `output`, `error`, `metadata`.

3. `TelemetryEvent`
- `event_id`, `event_type`, `timestamp`, `actor`, `target`, `status`, `attributes`.

## Runtime Flow
1. Receive task request.
2. Authenticate actor and authorize required role.
3. Record accounting event and enqueue task.
4. Worker executes task asynchronously.
5. Emit operational logs and audit events.
6. Emit telemetry events and batch for export.
7. Persist result and expose status query.

## Messaging Backbone (Sprint 9.5)
1. Broker standard: RabbitMQ (dockerized deployment target).
2. Logical model:
- Exchange: `spectrastrike.telemetry`
- Routing key: `telemetry.events`
- Main queue: `telemetry.events`
- Dead-letter queue: `telemetry.events.dlq`
3. Delivery policy:
- Idempotency key per event (`event_id`) to deduplicate replays.
- Bounded retry attempts for transient broker failures.
- Dead-letter routing when retries are exhausted.
4. Runtime adapters:
- `RabbitMQTelemetryPublisher`: in-memory RabbitMQ model for deterministic tests.
- `PikaRabbitMQTelemetryPublisher`: dockerized RabbitMQ adapter for real runtime publish.
5. Telemetry transport security:
- RabbitMQ listener configured TLS-only (`5671`) with client-certificate verification.
- App-side publisher supports CA/cert/key configuration from `RABBITMQ_SSL_*`.

## Cryptographic Signing (Sprint 10)
1. Signer integration: `pkg.orchestrator.signing.VaultTransitSigner`.
2. Key management:
- Transit key metadata and signing operations are delegated to HashiCorp Vault.
- Optional key bootstrap is supported through `VAULT_TRANSIT_AUTO_CREATE_KEY=true`.
3. Runtime config:
- `VAULT_ADDR`, `VAULT_TOKEN`, `VAULT_NAMESPACE`, `VAULT_VERIFY_TLS`.
- `VAULT_TRANSIT_MOUNT`, `VAULT_TRANSIT_KEY_NAME`, `VAULT_TRANSIT_KEY_TYPE`.
4. Security controls:
- HTTPS is required by default (`VAULT_REQUIRE_HTTPS=true`).
- Token and key material are never logged.
- Public key retrieval is version-aware for future manifest verification.
5. JWS generation:
- Compact JWS payload generation is handled by `pkg.orchestrator.jws.CompactJWSGenerator`.
- The signing input is canonical JSON (`sort_keys=True`) and encoded as `base64url(header).base64url(payload)`.
- Signatures from Vault transit are requested with JWS marshaling and normalized into compact JWS signature segment encoding.
6. Execution Manifest schema:
- Schema is defined in `pkg.orchestrator.manifest.ExecutionManifest`.
- Required fields: `task_context`, `target_urn`, `tool_sha256`, `parameters`.
- `task_context` enforces tenant and operator attribution (`tenant_id`, `operator_id`) and task lineage (`task_id`, `correlation_id`).
- `target_urn` and `tool_sha256` are strictly validated before signing to reduce forged/tampered dispatch risk.
7. Anti-replay controls:
- `ExecutionManifest` includes a per-request `nonce` and `issued_at` timestamp.
- `pkg.orchestrator.anti_replay.AntiReplayGuard` validates allowed time window and nonce uniqueness before dispatch.
- Replay storage is tenant-scoped (`tenant_id + nonce`) to preserve isolation boundaries.

## Security and Reliability Requirements
1. No secrets in code or logs.
2. TLS-only transport for outbound telemetry.
3. Role-based authorization enforced before execution.
4. Audit trail for denied and successful operations.
5. Retry with bounded backoff; circuit-break style failure protection.
6. Tamper-evident audit stream via hash-chained audit event records.

## Armory + Universal Runner (Sprints 11-13)
1. Armory registry:
- Internal OCI registry service (`armory-registry`) is deployed in compose.
- Registry delete operations are disabled for immutable artifact posture.
2. Armory control service:
- `pkg.armory.service.ArmoryService` handles ingest pipeline:
  - upload digesting (`sha256`),
  - SBOM metadata generation,
  - vulnerability summary generation,
  - signing metadata generation,
  - operator approval gating.
3. Runner cryptographic gate:
- `pkg.runner.jws_verify.RunnerJWSVerifier` validates compact JWS before execution admission.
- Forged signature attempts are hard-failed before any tool resolution.
4. Signed tool retrieval:
- `pkg.runner.universal.UniversalEdgeRunner` resolves only approved Armory digests that exactly match `ExecutionManifest.tool_sha256`.
5. Sandbox profile:
- Runner command contract enforces `--runtime=runsc`, AppArmor profile pinning, read-only rootfs, dropped capabilities, and no-network baseline.
6. Execution contract:
- `stdout`/`stderr`/`exit_code` are mapped into CloudEvents v1.0 via `pkg.runner.cloudevents.map_execution_to_cloudevent`.
7. QA guarantees:
- `tests/qa/test_execution_fabric_qa.py` validates forged-JWS rejection, tampered-digest rejection, and CloudEvents output integrity.

## OPA Capability Policies (Sprint 14)
1. Pre-sign authorization:
- Orchestrator pre-sign flow can query OPA before issuing compact JWS manifests.
2. Capability tuple model:
- Policy evaluation uses a tuple match on `operator_id + tenant_id + tool_sha256 + target_urn`.
3. Policy defaults:
- `spectrastrike.capabilities.allow` is deny-by-default.
- Input contract validation is exposed through `spectrastrike.capabilities.input_contract_valid`.

## Wrapper Telemetry Migration (Sprint 16.5)
1. Legacy wrapper direct telemetry emission (`telemetry.ingest(...)` in wrappers) is deprecated.
2. Wrappers emit SDK-built payloads (`pkg.telemetry.sdk`) and submit through unified parser path (`telemetry.ingest_payload(...)`).
3. Security invariants are preserved by parser/enforcement gates:
- strict tenant context propagation (`tenant_id` required),
- unified schema validation before buffering/publishing.

## Control Plane Integrity Hardening (Sprint 19)
1. Signed startup config gate:
- `pkg.orchestrator.control_plane_integrity.ControlPlaneIntegrityEnforcer` enforces JWS signature validation before startup acceptance.
- Unsigned or invalid signatures are hard-rejected.
2. Policy trust pinning:
- Startup config must include `policy_sha256` that matches `OPA_POLICY_PINNED_SHA256`.
- Any mismatch is rejected with integrity audit evidence.
3. Runtime baseline integrity:
- Optional startup binary baseline (`SPECTRASTRIKE_ENFORCE_BINARY_HASH=true`) validates SHA-256 against signed envelope value.
4. Immutable configuration history:
- `ImmutableConfigurationHistory` stores append-only config versions with hash chaining and duplicate-version rejection.
5. Integrity audit channel:
- `pkg.logging.framework.emit_integrity_audit_event` writes hash-chained records to dedicated logger `spectrastrike.audit.integrity`.
6. Vault hardening workflow:
- `pkg.orchestrator.vault_hardening.VaultHardeningWorkflow` automates transit key rotation checks and unseal share policy enforcement.

## High-Assurance AAA Controls (Sprint 20)
1. Hardware-backed MFA for privileged actions:
- `pkg.security.aaa_framework.AAAService` now supports hardware assertion verification via `HardwareMFAVerifier`.
- Privileged role authorization can require `hardware_mfa_assertion` in policy context.
2. Time-bound privilege elevation:
- `pkg.security.high_assurance.PrivilegeElevationService` issues short-lived, one-time elevation tokens.
- AAA privileged authorization can consume required `elevation_token_id` via validator hook.
3. Dual-control Armory approval:
- `pkg.armory.service.ArmoryService` enforces approval quorum (`approval_quorum=2` default) for tool authorization.
- Distinct approvers are required before a digest is marked authorized.
4. Dual-signature high-risk manifests:
- `pkg.orchestrator.dual_signature.HighRiskManifestDualSigner` enforces independent second signature for `high/critical` risk levels.
5. Break-glass and session recording:
- Break-glass activation uses irreversible audit flag semantics.
- `PrivilegedSessionRecorder` provides structured session start/command/end event capture for privileged activity evidence.

## Deterministic Execution Guarantees (Sprint 21)
1. Canonical manifest serialization:
- `pkg.orchestrator.manifest.canonical_manifest_json` enforces deterministic compact JSON (`sort_keys=True`, fixed separators).
2. Deterministic hashing:
- `pkg.orchestrator.manifest.deterministic_manifest_hash` computes stable SHA-256 over canonical manifest payload.
3. Schema semantic versioning:
- `ManifestSchemaVersionPolicy` enforces `MAJOR.MINOR.PATCH` format and supported major compatibility bounds.
4. Non-canonical submission rejection:
- `parse_and_validate_manifest_submission` rejects payloads that are not canonical JSON before manifest construction.
5. Runtime ingress guard:
- `OrchestratorEngine.validate_manifest_submission` exposes canonical validation path for raw manifest intake.
6. CI regression guard:
- `scripts/manifest_schema_regression.py` validates stable schema hash and is executed in CI (`.github/workflows/lint-test.yml`).

## Federation Fingerprint Binding (Sprint 22)
1. Unified execution fingerprint schema:
- `manifest_hash + tool_hash + operator_id + tenant_id + policy_decision_hash + timestamp`.
- Implemented in `pkg.orchestrator.execution_fingerprint.ExecutionFingerprintInput`.
2. Fingerprint generation and validation:
- `generate_execution_fingerprint` creates deterministic SHA-256 execution fingerprint.
- `validate_fingerprint_before_c2_dispatch` enforces pre-dispatch integrity gate.
3. Tamper-evident fingerprint audit:
- Fingerprint bind/validate outcomes are emitted to integrity audit channel via `emit_integrity_audit_event`.
4. VectorVue federation payload binding:
- RabbitMQ bridge includes `execution_fingerprint` in outgoing telemetry metadata and federation bundle.
- Bridge uses federated gateway dispatch path (`send_federated_telemetry`).

## Federation Channel Enforcement (Sprint 23)
1. Single outbound gateway:
- Bridge dispatch uses only internal federation endpoint (`/internal/v1/telemetry`) via `send_federated_telemetry`.
2. Legacy path removal:
- Direct bridge event/finding API emission path is removed from active bridge runtime.
3. mTLS-only federation:
- Federation dispatch requires TLS verification plus configured mTLS client cert/key.
4. Signed telemetry required:
- Federation dispatch requires payload signature secret configuration; unsigned federation payloads are denied.
5. Producer replay detection:
- Bridge tracks nonce replay window and denies duplicate producer nonce usage.
6. Idempotent bounded retry:
- Idempotency key for federation dispatch is execution fingerprint hash, aligning retries with deterministic replay-safe semantics.

## Anti-Repudiation Closure (Sprint 24)
1. Operator-identity-bound fingerprint:
- Operator identity is required and validated when generating execution fingerprint.
2. Write-ahead execution intent:
- Pre-dispatch execution intent records are appended before outbound federation dispatch.
- Intent records are hash-chained (`prev_hash -> intent_hash`) for tamper evidence.
3. Execution intent verification API:
- `verify_execution_intent_api` exposes verification contract for `execution_fingerprint` and optional `operator_id` checks.
4. Reconciliation and repudiation detection:
- Operator-to-execution reconciliation confirms immutable attribution.
- Repudiation attempts (claiming wrong operator) are detected and emitted to integrity audit stream.
5. Federation bundle intent metadata:
- Outbound federation bundle now includes `intent_id`, `intent_hash`, and `write_ahead=true`.

## Testing Strategy (for next tasks)
1. Unit tests for scheduler ordering and retry behavior.
2. Unit tests for AAA enforcement on task submission.
3. Unit tests for telemetry event normalization.
4. Integration tests for async execution lifecycle.
