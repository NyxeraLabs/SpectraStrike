<!--
Copyright (c) 2026 NyxeraLabs
Author: José María Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# SOC 2 Control Mapping (Sprint 32)

This mapping aligns current SpectraStrike controls to SOC 2 Trust Services Criteria (Security + Availability relevant controls).

## Mapping Table

| SOC 2 Criteria | SpectraStrike Control Implementation | Primary Evidence Artifacts |
| --- | --- | --- |
| CC6.1 Logical access security | AAA enforcement, OPA delegation, tenant-scoped policy checks before execution signing | `src/pkg/aaa/framework.py`, `src/pkg/orchestrator/opa_client.py`, `tests/qa/test_opa_policy_schema.py` |
| CC6.2 Authentication | Constant-time auth path, lockout support, optional MFA controls | `src/pkg/aaa/framework.py`, `docs/SECURITY_POLICY.md`, `tests/unit/test_aaa_framework.py` |
| CC6.6 Least privilege | Capability model `[identity + tenant + tool_hash + target]` via OPA policy contract | `docs/WHITEPAPER.md`, `src/pkg/orchestrator/opa_client.py`, `tests/qa/test_zero_trust_sprint17_qa.py` |
| CC7.2 Change management | Sprint-gated roadmap, QA runbook, kanban traceability, dev logs | `docs/ROADMAP.md`, `docs/manuals/QA_RUNBOOK.md`, `docs/kanban-board.csv`, `docs/dev-logs/` |
| CC7.3 Monitoring and anomaly response | Structured telemetry ingestion + audit emission + federation bridge status polling | `src/pkg/orchestrator/telemetry_ingestion.py`, `src/pkg/integration/vectorvue/rabbitmq_bridge.py`, `tests/qa/test_vectorvue_api_qa.py` |
| CC7.4 Incident evidence integrity | Tamper-evident audit chain and immutable execution intent records | `src/pkg/orchestrator/anti_repudiation.py`, `src/pkg/orchestrator/merkle_ledger.py`, `tests/unit/test_merkle_ledger.py` |
| A1.2 Availability processing capacity | Broker abstraction and high-throughput deterministic streaming | `src/pkg/orchestrator/messaging.py`, `tests/qa/test_sprint30_broker_abstraction_throughput_qa.py` |
| A1.3 Recovery and continuity support | Dockerized service health checks, backup/restore workflows in platform runbooks | `docs/manuals/QA_RUNBOOK.md`, `docs/manuals/USER_GUIDE.md` |

## Scope Notes

- Mapping is implementation-evidence focused and does not assert external SOC 2 attestation status.
- Customer deployment governance remains required for production controls (key custody, retention, legal scope).
