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
- [x] Configure Runner network isolation: Allow outbound *only* to authorized Target IPs defined in Manifest.
- [x] Block lateral movement within internal networks from the execution sandbox.
- [x] Implement micro-segmentation for multi-tenant SaaS environments.
- [x] Commit Network Fencing rules.

### Sprint 16 (Week 32): Telemetry & CloudEvents Standardization
- [x] Implement unified schema parser in Orchestrator for all incoming data.
- [x] Create Python/Bash SDKs for BYOT developers to easily format their tool outputs.
- [x] Ensure `tenant_id` context propagation is strictly enforced in all telemetry.
- [x] Commit Telemetry pipelines.

### Sprint 16.5 (Week 32.5): Legacy Wrapper SDK Migration
- [x] Add explicit deprecation note for legacy direct-wrapper telemetry emission path.
- [x] Migrate Nmap wrapper telemetry emission to BYOT telemetry SDK + unified schema ingestion.
- [x] Migrate Metasploit wrapper telemetry emission to BYOT telemetry SDK + unified schema ingestion.
- [x] Migrate manual Metasploit ingestion connector telemetry emission to BYOT telemetry SDK + unified schema ingestion.
- [x] Preserve security controls from prior sprints (strict `tenant_id` propagation + schema validation).
- [x] Add regression tests for SDK-based emission path compatibility.
- [x] Commit Sprint 16.5 SDK migration.

### Sprint 16.6 (Week 32.6): UI/TUI and Runtime Tenant Alignment
- [x] Update Web UI task and manual-sync action routes to enforce/default `tenant_id`.
- [x] Update Admin TUI client/shell workflows to propagate `tenant_id` in task and manual sync submissions.
- [x] Update dev/prod container environment defaults for tenant context propagation (`SPECTRASTRIKE_TENANT_ID`).
- [x] Update operator docs/Makefile hints for tenant-context requirement in interactive workflows.
- [ ] Commit Sprint 16.6 alignment updates.

### Sprint 16.7 (Week 32.7): Host Toolchain Integration Validation
- [x] Implement host integration smoke module covering local `nmap` execution and tenant-aware telemetry ingestion checks.
- [x] Validate host `metasploit` binary presence/version and add optional RPC authentication smoke path.
- [x] Add optional live VectorVue smoke hook to the same host validation workflow.
- [x] Enforce VectorVue smoke acceptance contract across event, finding, and ingest-status APIs in host integration validation.
- [x] Add unit regression coverage for VectorVue smoke pass/fail gating in host integration workflow.
- [x] Add operator-facing command entrypoint (`make host-integration-smoke`) and QA/User guide documentation.
- [x] Commit Sprint 16.7 host integration validation.

### Sprint 16.8 (Week 32.8): VectorVue RabbitMQ Bridge Alignment
- [x] Implement RabbitMQ-to-VectorVue bridge module for broker envelope to API forwarding.
- [x] Add live bridge CLI entrypoint (`pkg.integration.vectorvue.sync_from_rabbitmq`) and Makefile target (`make vectorvue-rabbitmq-sync`).
- [x] Migrate host integration VectorVue validation path to RabbitMQ-backed bridge flow.
- [x] Add regression unit tests for RabbitMQ bridge forwarding and failure handling.
- [x] Document operator QA flow for broker-backed VectorVue validation.
- [x] Produce whitepaper compliance check for current implementation status and explicit gaps.
- [x] Commit Sprint 16.8 RabbitMQ bridge alignment.

### Sprint 17 (Week 33): Zero-Trust QA
- [x] QA: Verify OPA rejects unauthorized tool execution attempts.
- [x] QA: Verify OPA rejects authorized tools against unauthorized Target URNs.
- [x] QA: Network penetration test of the Runner sandbox (verify containment).
- [x] QA: Re-validate Sprint 16.5 telemetry SDK migration regressions in Sprint 17 gate.
- [x] QA: Re-validate Sprint 16.7 host integration smoke regression suite in Sprint 17 gate.
- [x] QA: Re-validate Sprint 16.8 RabbitMQ bridge regression suite in Sprint 17 gate.

---

# Phase 5.5: Control Plane Integrity & Threat Formalization

## Sprint 18 – Formal Threat Modeling

- [x] Perform full STRIDE threat model across all planes
- [x] Define trust boundary diagram (Control, Runner, C2, Vault)
- [x] Enumerate malicious operator scenarios
- [x] Enumerate compromised runner scenarios
- [x] Enumerate supply-chain compromise scenarios
- [x] Enumerate cross-tenant escalation scenarios
- [x] Map threats to existing mitigations
- [x] Create unresolved risk backlog items
- [ ] Commit Threat Model v1.0 document

## Sprint 19 – Control Plane Integrity Hardening

- [ ] Implement signed configuration enforcement (JWS-based)
- [ ] Reject unsigned configuration at startup
- [ ] Enforce OPA policy hash pinning
- [ ] Implement policy hash mismatch detection
- [ ] Automate Vault key rotation workflow
- [ ] Harden Vault unseal procedure
- [ ] Implement runtime binary hash baseline check
- [ ] Add tamper-evident audit log channel
- [ ] Implement immutable configuration version history

## Sprint 20 – High-Assurance AAA Controls

- [ ] Enforce hardware-backed MFA for privileged actions
- [ ] Implement dual-control approval for tool ingestion
- [ ] Enforce dual-signature for high-risk manifests
- [ ] Implement break-glass workflow with irreversible audit flag
- [ ] Implement time-bound privilege elevation tokens
- [ ] Add privileged session recording support

## Sprint 21 – Deterministic Execution Guarantees

- [ ] Enforce canonical JSON serialization for manifests
- [ ] Implement deterministic manifest hashing validation
- [ ] Define semantic versioning for manifest schema
- [ ] Add schema regression validation to CI pipeline
- [ ] Reject non-canonical manifest submissions

---

# Phase 6: Forensic Ledger Architecture Definition

## Sprint 22 – Ledger Schema & Deterministic Model

- [ ] Define Merkle leaf schema (Manifest, Tool Hash, Operator ID, Tenant ID)
- [ ] Add Policy Decision Hash to leaf schema
- [ ] Add optional C2 Session reference field
- [ ] Define deterministic tree growth algorithm
- [ ] Define root hash signing cadence
- [ ] Design ledger storage abstraction layer
- [ ] Define deterministic replay reconstruction algorithm
- [ ] Commit Ledger Architecture Specification v1

---

# Phase 7: Advanced C2 Gateways & Stateful Integrations

## Sprint 23 – C2 Adapter Framework

- [ ] Define C2 adapter interface (Sidecar model)
- [ ] Implement manifest-to-command translation layer
- [ ] Implement C2 session-to-telemetry sync abstraction
- [ ] Enforce JWS verification before dispatch
- [ ] Enforce OPA policy check before dispatch
- [ ] Integrate C2 event metadata into ledger leaf model

## Sprint 24 – C2 Adapter Implementations

- [ ] Implement Sliver adapter gateway
- [ ] Implement Mythic adapter gateway scaffold
- [ ] Isolate C2 adapters in hardened execution boundary
- [ ] Simulate malicious adapter behavior
- [ ] Validate zero-trust enforcement under C2 execution

---

# Phase 8: Merkle Ledger Implementation & Cryptographic Non-Repudiation

## Sprint 25 – Ledger Core Implementation

- [ ] Implement append-only Merkle tree structure
- [ ] Store signed manifests as immutable leaves
- [ ] Store execution metadata as immutable leaves
- [ ] Implement periodic root hash generation
- [ ] Sign root hash using Control Plane key

## Sprint 26 – Ledger Verification & Transparency

- [ ] Implement inclusion proof generation API
- [ ] Implement third-party verification CLI
- [ ] Implement deterministic rebuild validation mode
- [ ] Implement ledger snapshot export
- [ ] Implement optional public root hash anchoring
- [ ] Implement read-only ledger verifier node
- [ ] Simulate DB tampering and detect root mismatch
- [ ] Validate inclusion proof verification end-to-end

---

# Phase 9: VectorVue Deep Cognitive & Streaming Integration

## Sprint 27 – Streaming Fabric Evolution

- [ ] Abstract broker layer (RabbitMQ + Kafka compatibility)
- [ ] Implement high-throughput pub/sub routing
- [ ] Normalize telemetry schema for ML feature store
- [ ] Hash execution graph metadata before export

## Sprint 28 – Cognitive Feedback Integration

- [ ] Push execution graph metadata to VectorVue
- [ ] Implement explainability metadata mapping
- [ ] Implement VectorVue → SpectraStrike DAG feedback sync
- [ ] Display Defensive Effectiveness scoring in UI
- [ ] Implement anomaly feedback loop into policy engine
- [ ] Stress-test high-volume streaming stability

---

# Phase 10: Enterprise Readiness & Standardization Gate

## Sprint 29 – Compliance & Documentation

- [ ] Map controls to SOC 2
- [ ] Map controls to ISO 27001 Annex A
- [ ] Map controls to NIST 800-53
- [ ] Map telemetry to MITRE ATT&CK techniques
- [ ] Produce Secure SDLC documentation package
- [ ] Publish Enterprise Security Whitepaper v1
- [ ] Publish enterprise hardening deployment guide

## Sprint 30 – Specification & Governance

- [ ] Publish Execution Manifest Specification v1
- [ ] Publish Telemetry CloudEvents Extension Specification
- [ ] Publish Capability Policy Model Specification
- [ ] Define backward compatibility guarantees
- [ ] Define extension RFC proposal workflow
- [ ] Publish public validation SDK
- [ ] Define semantic versioning governance policy
- [ ] Define deprecation lifecycle model

---

# Phase 11: Military-Grade Isolation & Hardware Boundaries

## Sprint 31 – MicroVM Isolation & Attestation

- [ ] Transition Universal Runner to Firecracker MicroVM
- [ ] Implement sub-200ms ephemeral boot optimization
- [ ] Enforce hardware virtualization isolation boundary
- [ ] Implement runtime attestation reporting
- [ ] Implement TPM-backed identity (on-prem)
- [ ] Implement ephemeral key derivation per execution
- [ ] Implement mutual attestation (Runner ↔ Control Plane)
- [ ] Attempt VM breakout simulation
- [ ] Validate multi-tenant stress isolation

---

# Phase 12: Independent Security Validation

## Sprint 32 – External Audit & Red Team

- [ ] Commission third-party cryptographic audit (JWS + Merkle)
- [ ] Commission Control Plane red team engagement
- [ ] Conduct Runner escape attempt campaign
- [ ] Conduct OPA bypass simulation attempts
- [ ] Simulate supply-chain injection attack
- [ ] Conduct secure configuration audit
- [ ] Publish summarized audit findings
- [ ] Track remediation actions

---

# Phase 13: Market Standardization Strategy

## Sprint 33 – Interoperability & Ecosystem

- [ ] Publish public read-only verification node
- [ ] Publish SDK for external tool builders (BYOT)
- [ ] Publish open policy authoring guide
- [ ] Release standalone manifest validator CLI
- [ ] Define interoperability conformance test suite
- [ ] Launch early-adopter partner program

## Sprint 34 – Governance & Industry Adoption

- [ ] Produce MSSP reference architecture blueprint
- [ ] Publish regulated-industry deployment guide
- [ ] Create cloud-native reference deployment patterns
- [ ] Establish spec versioning governance process
- [ ] Define long-term compatibility contract
- [ ] Publish SpectraStrike Architecture Standard v1.0
- [ ] Define neutral foundation transition strategy

---

# Phase 14: Operational Resilience & Scale Hardening

## Sprint 35 – Reliability & Scale Hardening

- [ ] Implement chaos testing for control plane components
- [ ] Simulate broker failure under load
- [ ] Simulate ledger corruption recovery
- [ ] Define and validate RPO/RTO targets
- [ ] Define SLO/SLI reliability metrics
- [ ] Implement rate limiting & abuse protection
- [ ] Validate multi-region deployment architecture
- [ ] Load test at 10x projected enterprise scale

---

# Long-Term Strategic Objective

- [ ] Position SpectraStrike as a verifiable offensive execution standard
- [ ] Achieve recognition as enterprise-grade validated execution fabric
- [ ] Build ecosystem adoption beyond internal platform usage
- [ ] Establish SpectraStrike as a cryptographically trusted execution reference model
