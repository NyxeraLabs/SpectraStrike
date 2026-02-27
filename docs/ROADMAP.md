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

- [x] Implement signed configuration enforcement (JWS-based)
- [x] Reject unsigned configuration at startup
- [x] Enforce OPA policy hash pinning
- [x] Implement policy hash mismatch detection
- [x] Automate Vault key rotation workflow
- [x] Harden Vault unseal procedure
- [x] Implement runtime binary hash baseline check
- [x] Add tamper-evident audit log channel
- [x] Implement immutable configuration version history

## Sprint 20 – High-Assurance AAA Controls

- [x] Enforce hardware-backed MFA for privileged actions
- [x] Implement dual-control approval for tool ingestion
- [x] Enforce dual-signature for high-risk manifests
- [x] Implement break-glass workflow with irreversible audit flag
- [x] Implement time-bound privilege elevation tokens
- [x] Add privileged session recording support

## Sprint 21 – Deterministic Execution Guarantees

- [x] Enforce canonical JSON serialization for manifests
- [x] Implement deterministic manifest hashing validation
- [x] Define semantic versioning for manifest schema
- [x] Add schema regression validation to CI pipeline
- [x] Reject non-canonical manifest submissions

---

# Phase 5.6: Federation Trust Closure & Execution Binding

## Sprint 22 (Week 41-42): Unified Execution Fingerprint Binding
- [x] Define unified execution fingerprint schema:
      (manifest_hash + tool_hash + operator_id + tenant_id + policy_decision_hash + timestamp)
- [x] Generate fingerprint before dispatch
- [x] Persist fingerprint in tamper-evident audit stream
- [x] Include fingerprint in telemetry payload to VectorVue
- [x] Enforce fingerprint validation before C2 dispatch
- [x] Reject execution if fingerprint mismatch detected
- [x] Add integration tests for fingerprint integrity
- [x] Commit Sprint 22 Unified Execution Fingerprint Binding

## Sprint 23 (Week 43-44): Federation Channel Enforcement
- [x] Enforce single outbound telemetry gateway
- [x] Remove any legacy direct API emission paths
- [x] Enforce mTLS-only outbound federation
- [x] Enforce signed telemetry requirement (no unsigned fallback)
- [x] Add replay detection validation at producer side
- [x] Implement bounded retry with idempotent fingerprint key
- [x] Add federation smoke test suite
- [x] Commit Sprint 23 Federation Channel Enforcement

## Sprint 24 (Week 45-46): Anti-Repudiation Closure
- [x] Bind operator identity irreversibly into execution fingerprint
- [x] Enforce pre-dispatch intent record (write-ahead hash entry)
- [x] Implement execution intent verification API
- [x] Add operator-to-execution audit reconciliation test
- [x] Simulate repudiation attempt and validate detection
- [x] Commit Sprint 24 Anti-Repudiation Closure

## Phase 5.6 Operational Closure (Dockerized Federation Setup)
- [x] Configure local federation endpoint to internal gateway route (`/internal/v1/telemetry`)
- [x] Rotate and align mTLS trust material for local dockerized execution
- [x] Enforce strict gateway path semantics (reject redirect-based false positives)
- [x] Validate live `nmap -> SpectraStrike -> VectorVue` federation acceptance
- [x] Validate live Metasploit telemetry federation acceptance
- [x] Record non-tracked local audit evidence for acceptance/rejection history


# Phase 6: Merkle Ledger Architecture & Append-Only Authority

## Sprint 25 (Week 47-48): Ledger Model Definition
- [x] Define Merkle leaf schema using unified execution fingerprint
- [x] Define strict append-only insertion order
- [x] Define deterministic tree growth rules
- [x] Define root generation cadence
- [x] Define root signing procedure
- [x] Define inclusion proof structure
- [x] Commit Sprint 25 Ledger Model Definition

## Sprint 26 (Week 49-50): Ledger Core Implementation
- [x] Implement append-only Merkle tree
- [x] Persist immutable execution leaves
- [x] Implement periodic root generation
- [x] Sign root with Control Plane signing authority
- [x] Implement root verification routine
- [x] Add tamper simulation test
- [x] Commit Sprint 26 Ledger Core Implementation

## Sprint 27 (Week 51-52): Ledger Verification & Export
- [x] Implement inclusion proof API
- [x] Implement deterministic rebuild mode
- [x] Implement ledger snapshot export
- [x] Implement read-only verifier node
- [x] Validate DB tampering detection via root mismatch
- [x] Commit Sprint 27 Ledger Verification & Export


# Phase 7: C2 Trust Extension Layer

## Sprint 28 (Week 53-54): C2 Adapter Trust Enforcement
- [x] Bind C2 dispatch to unified execution fingerprint
- [x] Enforce JWS verification at adapter boundary
- [x] Enforce policy hash validation at adapter boundary
- [x] Isolate adapters within hardened execution boundary
- [x] Simulate malicious adapter behavior
- [x] Commit Sprint 28 C2 Adapter Trust Enforcement

## Sprint 29 (Week 55-56): Advanced C2 Implementations
- [x] Implement Sliver adapter hardened version
- [x] Implement Mythic adapter scaffold
- [x] Integrate C2 execution metadata into ledger leaf
- [x] Validate zero-trust enforcement during live session
- [x] Commit Sprint 29 Advanced C2 Implementations


# Phase 8: Streaming Fabric & VectorVue Cognitive Integration

## Sprint 30 (Week 57-58): Broker Abstraction & High-Throughput Path
- [ ] Abstract broker layer (RabbitMQ/Kafka compatible)
- [ ] Enforce ordered execution event streaming
- [ ] Normalize telemetry schema for ML ingestion
- [ ] Add high-volume load testing
- [ ] Commit Sprint 30 Broker Abstraction & Throughput

## Sprint 31 (Week 59-60): Cognitive Feedback Loop
- [ ] Push execution graph metadata to VectorVue
- [ ] Implement VectorVue → SpectraStrike feedback sync
- [ ] Bind feedback adjustments to policy engine
- [ ] Display defensive effectiveness metrics in UI
- [ ] Validate end-to-end cognitive loop
- [ ] Commit Sprint 31 Cognitive Feedback Loop


# Phase 9: Enterprise & Compliance Gate

## Sprint 32 (Week 61-62): Compliance Mapping
- [ ] Map controls to SOC 2
- [ ] Map controls to ISO 27001 Annex A
- [ ] Map controls to NIST 800-53
- [ ] Map telemetry to MITRE ATT&CK
- [ ] Produce Secure SDLC documentation package
- [ ] Commit Sprint 32 Compliance Mapping

## Sprint 33 (Week 63-64): Specification Publication
- [ ] Publish Execution Manifest Specification v1
- [ ] Publish Telemetry Extension Specification
- [ ] Publish Capability Policy Specification
- [ ] Define backward compatibility guarantees
- [ ] Publish validation SDK
- [ ] Commit Sprint 33 Specification Publication


# Phase 10: Hardware-Assisted Isolation

## Sprint 34 (Week 65-66): MicroVM Transition
- [ ] Transition Runner to Firecracker MicroVM
- [ ] Implement ephemeral boot optimization
- [ ] Implement runtime attestation reporting
- [ ] Enforce hardware isolation boundary
- [ ] Simulate breakout attempt
- [ ] Commit Sprint 34 MicroVM Transition

## Sprint 35 (Week 67-68): Mutual Attestation & Key Derivation
- [ ] Implement TPM-backed identity (on-prem)
- [ ] Implement per-execution ephemeral key derivation
- [ ] Implement Runner ↔ Control Plane mutual attestation
- [ ] Validate multi-tenant stress isolation
- [ ] Commit Sprint 35 Mutual Attestation & Isolation Validation
