<!--
Copyright (c) 2026 NyxeraLabs
Author: José María Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# NIST SP 800-53 Rev. 5 Mapping (Sprint 32)

This mapping connects current SpectraStrike controls to selected NIST 800-53 control families commonly requested for high-assurance environments.

## Mapping Table

| NIST Control | SpectraStrike Control Implementation | Primary Evidence Artifacts |
| --- | --- | --- |
| AC-2 Account management | Operator identity model and role-aware execution admission | `src/pkg/aaa/framework.py`, `docs/USER_REGISTRATION_POLICY.md` |
| AC-3 Access enforcement | OPA-based policy decision gate before execution endorsement | `src/pkg/orchestrator/opa_client.py`, `tests/qa/test_opa_policy_schema.py` |
| AC-6 Least privilege | Capability tuple validation for tenant + tool + target + operator | `docs/WHITEPAPER.md`, `src/pkg/orchestrator/execution_fingerprint.py` |
| AU-2 Event logging | Structured telemetry ingestion and normalized event publication | `src/pkg/orchestrator/telemetry_ingestion.py`, `src/pkg/orchestrator/messaging.py` |
| AU-8 Time stamps | Signed timestamp and nonce verification in federation and feedback channels | `src/pkg/integration/vectorvue/client.py`, `tests/unit/integration/test_vectorvue_client.py` |
| AU-10 Non-repudiation | Merkle ledger root signing and immutable execution intent chain | `src/pkg/orchestrator/merkle_ledger.py`, `src/pkg/orchestrator/anti_repudiation.py` |
| SC-8 Transmission confidentiality/integrity | TLS/mTLS enforced data-plane and certificate pinning for federation | `src/pkg/integration/vectorvue/client.py`, `docs/manuals/QA_RUNBOOK.md` |
| SC-12/SC-13 Cryptographic key establishment/use | Signed manifest flow and execution fingerprint integrity chain | `src/pkg/orchestrator/execution_fingerprint.py`, `docs/WHITEPAPER.md` |
| SI-4 System monitoring | Broker bridge observability, status polling, and anomaly telemetry normalization | `src/pkg/integration/vectorvue/rabbitmq_bridge.py`, `tests/qa/test_vectorvue_api_qa.py` |
| SA-11 Developer testing and evaluation | Mandatory unit/integration/QA gates and sprint evidence logs | `docs/manuals/QA_RUNBOOK.md`, `tests/qa/`, `docs/dev-logs/` |

## Scope Notes

- Mapping is evidence-oriented and excludes inherited controls from customer infrastructure.
- Control tailoring to Moderate/High baselines must be performed by deployment owners.
