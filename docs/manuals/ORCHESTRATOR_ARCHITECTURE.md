# Orchestrator Architecture (Phase 2 Design)

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

## Security and Reliability Requirements
1. No secrets in code or logs.
2. TLS-only transport for outbound telemetry.
3. Role-based authorization enforced before execution.
4. Audit trail for denied and successful operations.
5. Retry with bounded backoff; circuit-break style failure protection.

## Testing Strategy (for next tasks)
1. Unit tests for scheduler ordering and retry behavior.
2. Unit tests for AAA enforcement on task submission.
3. Unit tests for telemetry event normalization.
4. Integration tests for async execution lifecycle.
