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

## Security and Reliability Requirements
1. No secrets in code or logs.
2. TLS-only transport for outbound telemetry.
3. Role-based authorization enforced before execution.
4. Audit trail for denied and successful operations.
5. Retry with bounded backoff; circuit-break style failure protection.
6. Tamper-evident audit stream via hash-chained audit event records.

## Testing Strategy (for next tasks)
1. Unit tests for scheduler ordering and retry behavior.
2. Unit tests for AAA enforcement on task submission.
3. Unit tests for telemetry event normalization.
4. Integration tests for async execution lifecycle.
