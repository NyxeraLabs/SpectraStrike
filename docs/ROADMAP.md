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

# SpectraStrike Roadmap – Phases, Sprints, and Commits

![SpectraStrike Logo](../ui/web/assets/images/SprectraStrike_Logo.png)

> **ARCHITECTURAL PIVOT NOTICE (v2.0):** 
> As of Phase 4, SpectraStrike transitions from a legacy "wrapper-based" orchestration tool into a **Policy-Driven, Cryptographically Verifiable Universal Execution Fabric**. Future phases prioritize BYOT (Bring Your Own Tool), ephemeral hardware isolation, cryptographic non-repudiation (JWS/Merkle Trees), and Zero-Trust authorization via OPA. This architecture is designed to seamlessly feed structured, verifiable telemetry to **VectorVue** via our messaging backbone (RabbitMQ/Kafka) to empower its ML/Cognition and Compliance engines.

---

## Phase 1: Setup & Environment Initialization (Sprint 1-2)

### Sprint 1 (Week 1-2): Repository & Dev Environment
- [x] Initialize Git repo – Commit initial setup
- [x] Setup Python virtual environment
- [x] Install core dependencies (requests, asyncio, logging)
- [x] Setup Docker dev containers
- [x] Setup IDE configuration
- [x] Configure pre-commit hooks
- [x] Setup Git branching strategy
- [x] Implement initial CI/CD pipeline (GitHub Actions / GitLab CI)
- [x] Setup logging framework
- [x] Configure AAA framework (AuthN/AuthZ/Accounting)

### Deliverables:
- [x] Baseline repo structure committed
- [x] Working dev environment with Docker & IDE ready
- [x] CI/CD pipeline skeleton
- [x] Logging & AAA framework in place

### Phase 1 QA (Baseline)
- [x] QA: validate environment consistency
- [x] QA: run linter & unit test baseline

---

## Phase 2: Orchestrator Core Development (Sprint 3-4)

### Sprint 2 (Week 3-4): Orchestrator Architecture
-[x] Design orchestrator architecture
- [x] Implement async event loop
- [x] Implement task scheduler
- [x] Implement telemetry ingestion
- [x] Implement logging & audit trails
- [x] Implement AAA enforcement at engine level
- [x] Unit tests for orchestrator
- [x] Commit orchestrator code

### Sprint 3 (Week 5-6): Orchestrator QA
- [x] QA: run functional tests
-[x] QA: validate telemetry output
- [x] QA: AAA access verification

### Deliverables:
- [x] Core orchestrator engine implemented
- [x] Task scheduling, telemetry, logging, AAA fully functional
- [x] Baseline QA verification completed

---

## Phase 3: Integration Layer Development (Sprint 5-9.9)

### Sprint 4 (Week 7-8): API Integration
- [x] Design API client for VectorVue
- [x] Implement encrypted data transfer (TLS)
- [x] Implement retries / backoff
- [x] Implement event batching
- [x] Implement message signing for integrity
-[x] Commit integration code

### Sprint 5 (Week 9-10): API QA
-[x] QA: test API endpoints
- [x] QA: validate encrypted communication
- [x] QA: confirm telemetry reaches VectorVue

### Sprint 6 (Week 11-12): Nmap Wrapper Development (Legacy Baseline)
- [x] Create Python wrapper module (Nmap)
- [x] Implement TCP SYN scan (Nmap)
- [x] Implement UDP scan (Nmap)
- [x] Implement OS detection (Nmap)
- [x] Parse XML/JSON output (Nmap)
- [x] Send scan results to orchestrator (Nmap)
- [x] Integrate logging & telemetry (Nmap)
- [x] Unit tests for wrapper (Nmap)
- [x] Commit wrapper (Nmap)

### Sprint 7 (Week 13-14): Nmap QA
- [x] QA: validate scan accuracy (Nmap)
- [x] QA: AAA enforcement (Nmap)

### Sprint 8 (Week 15-16): Metasploit Integration (Legacy Baseline)
- [x] Connect to Metasploit RPC
- [x] Implement module loader (Metasploit)
- [x] Execute exploits (Metasploit)
- [x] Capture session output (Metasploit)
- [x] Send results to orchestrator (Metasploit)
- [x] Logging & telemetry (Metasploit)
- [x] Retry/error handling (Metasploit)
- [x] Unit tests (Metasploit)
- [x] Commit wrapper (Metasploit)

### Sprint 8.5 (Week 16-17): Nmap + Metasploit End-to-End Stabilization
- [x] Add unprivileged Nmap execution fallback (`-sS` -> `-sT`) for local/operator runs
- [x] Validate real Nmap scan execution path and telemetry handoff
-[x] Implement manual Metasploit ingestion connector (sessions + session-events pull)
- [x] Add checkpoint-based deduplication for Metasploit manual ingestion
- [x] Add CLI sync entrypoint for operator-driven Metasploit ingestion
- [x] Add unit/integration tests for manual ingestion flow
-[x] Commit end-to-end stabilization updates

### Sprint 9 (Week 17-18): Metasploit QA
- [x] QA: validate exploit runs (Metasploit)
-[x] QA: check telemetry delivery (Metasploit)

### Sprint 9.5 (Week 18): Messaging Backbone (RabbitMQ baseline)
- [x] Select broker standard (RabbitMQ) and define topic/queue model
- [x] Implement telemetry publisher abstraction (`TelemetryPublisher`)
- [x] Add broker-backed async delivery path for orchestrator telemetry
- [x] Add retry, dead-letter, and idempotency handling for broker delivery
- [x] Add integration tests for publish/consume flow
- [x] Add dockerized RabbitMQ runtime wiring + Makefile command targets
- [x] Add remote operator endpoint configuration (`MSF_RPC_*`, `MSF_MANUAL_*`, `RABBITMQ_*`)
- [x] Commit messaging backbone

### Sprint 9.6 (Week 18-19): Infrastructure Control Plane & Armory UI
- [x] Define UI architecture and API contracts
- [x] Implement Web UI foundation with Next.js (App Router) + Tailwind CSS
- [x] Implement auth views and operator dashboard shell (Web UI)
- [x] Implement raw execution telemetry feed view for operator debugging (Web UI)
- [x] Implement Armory management screens (tool ingest, SBOM scan, signature approval) (Web UI)
- [x] Implement Fleet management screens (runner/microVM/queue health) (Web UI)
- [x] Implement Policy & Trust screens (OPA controls + Vault/HSM signer health) (Web UI)
- [x] Wire Web UI control actions to orchestrator infrastructure endpoints
- [x] Add Web UI tests (component/unit + basic E2E)
-[x] Implement Interactive Terminal UI (Admin TUI) for operational control
- [x] Add Admin TUI command workflows (task/manifest submission, telemetry watch, break-glass controls)
- [x] Add Admin TUI tests and command-level QA checks
- [x] Commit UI foundation (Web UI + Admin TUI)

### Sprint 9.7 (Week 19): Security & Container Platform Hardening
- [x] Implement Dockerized runtime stack for all components
- [x] Add Nginx reverse proxy container (TLS termination, routing, rate limits)
- [x] Add PostgreSQL container for persistent operational data
- [x] Add Redis container for cache, buffering, and near-real-time log/event stream
- [x] Add secure internal Docker network segmentation between services
- [x] Add secrets/config management for credentials, tokens, and API keys
- [x] Add centralized log pipeline and retention policy in containers
- [x] Add host firewall baseline for published container ports (`DOCKER-USER` policy)
- [x] Add egress allowlist enforcement baseline for Docker bridge traffic
- [x] Add TLS certificate pinning checks for external integrations (Metasploit/VectorVue)
- [x] Add HTTPS edge with optional mTLS client verification in Nginx
- [x] Add internal mTLS for telemetry data plane (app <-> RabbitMQ)
- [x] Add full service-to-service end-to-end TLS (internal mTLS between all runtime services, including DB/cache)
- [x] Add health checks, startup ordering, and restart policies for all services
- [x] Add backup/restore workflow for PostgreSQL and Redis state
- [x] Add container security baseline (non-root, minimal images, pinned versions)
- [x] Add infrastructure integration tests and security QA checks
- [x] Add project Makefile for easy test, easy deploy, and easy QA operations
- [x] Add local supply-chain security gate (SBOM + CVE scan + signature workflow)
- [x] Add tamper-evident audit event hash-chaining
- [x] Add stronger AAA controls (constant-time auth, lockout, optional MFA)
- [x] Add QA runbook and full-regression command targets (local and CI-aligned)
- [x] Commit security/container platform baseline

### Sprint 9.8 (Week 19-20): Cross-Sprint QA Consolidation
- [x] QA: validate Sprint 9.5 messaging backbone tests
- [x] QA: validate Sprint 9.5 remote endpoint/manual-ingestion integration tests
- [x] QA: validate Sprint 9.6 Admin TUI workflows
- [ ] QA: rerun Sprint 9.6 Web UI unit/E2E suite in dependency-ready environment
- [x] QA: validate Sprint 9.7 AAA + audit trail hardening tests
- [x] QA: validate Sprint 9.7 compose configuration and security policy checks
- [x] QA: validate docs integrity and references
- [x] QA: validate license header compliance across repo
- [x] Blocker captured with exact command output for dependency and test commands

### Sprint 9.9 (Week 20): Governance & Legal Enforcement
- [x] Implement environment-aware legal enforcement service (`self-hosted`, `enterprise`, `saas`)
- [x] Add versioned legal configuration (`EULA`, `AUP`, `PRIVACY`)
-[x] Implement self-hosted acceptance storage and validation
- [x] Add enterprise installation acceptance model (schema draft)
- [x] Add SaaS user-level acceptance model (migration draft)
- [x] Integrate legal enforcement into auth middleware and token issuance gates
- [x] Add re-acceptance flow on legal version mismatch
-[x] Add legal acceptance route and Web UI acceptance workflow
- [x] Add CLI/TUI legal gate integration
- [x] Update governance/security documentation indexing

---

## Phase 4: The Universal Execution Fabric & Armory (Sprint 10-13)
*Goal: Move away from hardcoded wrappers. Implement cryptographic signing for arbitrary execution.*

### Sprint 10 (Week 21-22): Cryptographic Payload Engine
- [x] Implement HashiCorp Vault (or HSM equivalent) integration for signing keys.
- [x] Implement JWS (JSON Web Signature) payload generation in the Orchestrator.
- [x] Design Execution Manifest schema (Task Context, Target URN, Tool SHA256, Parameters).
- [x] Implement Anti-Replay mechanisms (nonce and timestamp validation).
- [x] Commit cryptographic engine updates.

### Sprint 11 (Week 23-24): The Armory (Tool Registry)
- [x] Deploy internal, immutable OCI container registry / binary store ("The Armory").
- [x] Implement tool ingestion pipeline (Upload -> SBOM generation -> Vulnerability Scan).
- [x] Implement Cosign/Sigstore cryptographic signing for all ingested tools.
- [x] Create UI/TUI module for registering and managing authorized tools (BYOT support).
- [x] Commit The Armory infrastructure.

### Sprint 12 (Week 25-26): The Universal Edge Runner
- [x] Build the Universal Runner (lightweight Go or secured Python binary).
- [x] Implement local JWS public-key verification logic inside the Runner.
- [x] Implement secure retrieval of signed tools from The Armory based on Manifest hash.
- [x] Implement strict execution sandboxing using `gVisor` (`runsc`) or Docker AppArmor profiles.
- [x] Implement standard execution contract: output capture mapping `stdout`/`stderr` to CloudEvents schema.
- [x] Commit the Universal Runner.

### Sprint 13 (Week 27): Execution Fabric QA
- [x] QA: Attempt execution with forged JWS signatures (must fail).
- [x] QA: Attempt execution with tampered tool binaries/hashes (must fail).
-[x] QA: Verify telemetry output accurately maps to standardized CloudEvents.

---

## Phase 5: Zero-Trust & Policy-Driven Control Plane (Sprint 14-17)
*Goal: Decouple authorization logic from codebase. Enforce strict capability checks.*

### Sprint 14 (Week 28-29): Open Policy Agent (OPA) Integration
- [x] Deploy OPA container alongside the Orchestrator.
- [x] Define standard Rego policy schemas for Operator Capabilities.
- [x] Implement Orchestrator pre-execution hooks: query OPA before signing any JWS.
- [x] Develop capability policies based on `[Identity] + [Tenant] +[Tool Hash] + [Target URN]`.
- [x] Refactor existing Python AAA to delegate complex execution checks to OPA.
- [x] Commit OPA Integration.

### Sprint 15 (Week 30-31): Network Fencing & Blast Radius Control
- [x] Implement dynamic eBPF/Cilium network policies for the Universal Runner.
- [ ] Configure Runner network isolation: Allow outbound *only* to authorized Target IPs defined in Manifest.
- [ ] Block lateral movement within internal networks from the execution sandbox.
- [ ] Implement micro-segmentation for multi-tenant SaaS environments.
- [ ] Commit Network Fencing rules.

### Sprint 16 (Week 32): Telemetry & CloudEvents Standardization
- [ ] Implement unified schema parser in Orchestrator for all incoming data.
- [ ] Create Python/Bash SDKs for BYOT developers to easily format their tool outputs.
- [ ] Ensure `tenant_id` context propagation is strictly enforced in all telemetry.
- [ ] Commit Telemetry pipelines.

### Sprint 17 (Week 33): Zero-Trust QA
- [ ] QA: Verify OPA rejects unauthorized tool execution attempts.
-[ ] QA: Verify OPA rejects authorized tools against unauthorized Target URNs.
- [ ] QA: Network penetration test of the Runner sandbox (verify containment).

---

## Phase 6: Advanced C2 Gateways & Adapters (Sprint 18-21)
*Goal: Support complex, stateful C2 frameworks (Sliver, Mythic) without exposing the platform to RCE.*

### Sprint 18 (Week 34-35): C2 Gateway Architecture
- [ ] Design the Event-Driven C2 Adapter interface (Sidecar pattern).
-[ ] Implement bidirectional sync abstractions (C2 Session -> SpectraStrike Telemetry).
- [ ] Implement command dispatch abstractions (SpectraStrike Manifest -> C2 Command).
- [ ] Commit C2 Gateway base classes.

### Sprint 19 (Week 36-37): Sliver Framework Integration
- [ ] Deploy `sliver-sync-gateway` microservice.
- [ ] Connect Gateway to Sliver's Multi-Player `gRPC` API.
- [ ] Translate Sliver implant callbacks into SpectraStrike CloudEvents.
- [ ] Enforce JWS and OPA checks before sending commands from TUI/Web to Sliver.
- [ ] Commit Sliver Integration.

### Sprint 20 (Week 38-39): Generic Webhook & DAG Pipeline
- [ ] Implement secure, authenticated Webhook endpoints for asynchronous third-party tools (e.g., OSINT platforms).
- [ ] Implement Directed Acyclic Graph (DAG) parser for chaining script execution (e.g., Tool A output -> Tool B input).
- [ ] Commit Pipeline orchestrator.

### Sprint 21 (Week 40): C2 & Gateway QA
- [ ] QA: End-to-end command execution via Sliver.
- [ ] QA: Verify OPA correctly blocks unauthorized C2 commands.
- [ ] QA: Test DAG execution workflows with multiple sequenced tools.

---

## Phase 7: Forensic Ledger & Non-Repudiation (Sprint 22-25)
*Goal: Provide enterprise clients with mathematical proof of executed operations.*

### Sprint 22 (Week 41-42): Append-Only Merkle Tree
- [ ] Upgrade hash-chaining to a formal Merkle Tree structure (Trillian/Sigstore inspired).
- [ ] Store JWS Manifest, Tool Hash, and Execution Timestamp as immutable tree leaves.
-[ ] Implement periodic tree root hashing and signing by Control Plane.
- [ ] Commit Merkle Ledger core.

### Sprint 23 (Week 43-44): Cryptographic Audit APIs
- [ ] Create endpoints for exporting cryptographic inclusion proofs.
- [ ] Build third-party verification script for clients/auditors.
- [ ] Integrate ledger hashes into Web UI / TUI audit views.
- [ ] Commit Audit API.

### Sprint 24 (Week 45): VectorVue Compliance Alignment
- [ ] Structure the Merkle Tree exports to match VectorVue Phase 9 (Compliance & Regulatory Assurance) requirements.
- [ ] Ensure non-repudiation artifacts map cleanly to `compliance_events` and `control_observations` in VectorVue.
- [ ] Commit integration schemas.

### Sprint 25 (Week 46): Ledger QA
- [ ] QA: Simulate database tampering (verify Merkle root mismatch).
-[ ] QA: Test end-to-end inclusion proof generation and validation.

---

## Phase 8: VectorVue Ecosystem Integration & Streaming (Sprint 26-29)
*Goal: Turn SpectraStrike into the definitive offensive sensory array for VectorVue.*

### Sprint 26 (Week 47-48): Event Broker Evolution (RabbitMQ to Kafka Prep)
- [ ] Implement robust publish/subscribe routing for multi-platform delivery.
- [ ] Introduce Kafka abstractions (Topics, Partitions, Consumer Groups) for high-throughput offensive telemetry.
- [ ] Maintain RabbitMQ backward compatibility for single-tenant deployments.
- [ ] Commit broker evolution.

### Sprint 27 (Week 49-50): VectorVue ML Data Pipeline
- [ ] Map SpectraStrike Universal Telemetry to VectorVue Phase 8 (ML/Analytics) feature store schemas.
- [ ] Implement high-speed asynchronous push of execution graphs to VectorVue for cognitive analysis.
- [ ] Include execution contexts (tenant_id, operator, environment_burn metrics) for VectorVue’s Defensive Effectiveness Models.
- [ ] Commit telemetry pipeline.

### Sprint 28 (Week 51): Bi-Directional Cognitive Sync
- [ ] Ingest "Action Recommendations" generated by VectorVue's Phase 5.5 (Cognitive Layer).
- [ ] Auto-generate SpectraStrike execution DAGs based on VectorVue ML recommendations.
- [ ] Display VectorVue Defensive Pressure scores in SpectraStrike UI to inform operator tempo.
-[ ] Commit bi-directional sync.

### Sprint 29 (Week 52): VectorVue Integration QA
- [ ] QA: Validate high-volume event streaming stability.
- [ ] QA: Verify accuracy of data ingested into VectorVue’s ML feature store.
- [ ] QA: End-to-end loop (VectorVue Recommends -> SpectraStrike Executes -> VectorVue Learns).

---

## Phase 9: Military-Grade Isolation & Release (Sprint 30-33)
*Goal: Final hardware-level security hardening and enterprise production release.*

### Sprint 30 (Week 53-54): Firecracker MicroVM Execution
-[ ] Transition Universal Runner from Docker/gVisor to AWS Firecracker.
- [ ] Implement sub-200ms ephemeral microVM bootstrapping.
- [ ] Ensure true hardware virtualization boundary for generic BYOT execution.
- [ ] Commit MicroVM orchestration.

### Sprint 31 (Week 55-56): Full System Security Audit
- [ ] Conduct internal Red Team assessment of the SpectraStrike control plane.
- [ ] Conduct third-party cryptographic review of JWS/Merkle implementation.
- [ ] Patch discovered vulnerabilities.

### Sprint 32 (Week 57-58): Enterprise Documentation
- [ ] Write CISO/Architect Security Whitepapers (explaining BYOT safety and non-repudiation).
- [ ] Write Operator Manuals (DAG writing, tool registration).
-[ ] Write Compliance/Auditor Guides (Verifying the ledger).

### Sprint 33 (Week 59): Enterprise v1.0 Release
- [ ] Finalize deployment orchestration (Helm, Terraform, systemd).
- [ ] Final QA regression sweep.
- [ ] Tag `v1.0.0` Release in Git.
- [ ] Deliver to select Enterprise/Tier-1 MSSP partners.
