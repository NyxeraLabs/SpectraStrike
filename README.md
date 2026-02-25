


<!--
Copyright (c) 2026 NyxeraLabs
Author: José María Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# SpectraStrike
![SpectraStrike Logo](ui/web/assets/images/SprectraStrike_Logo.png)

**SpectraStrike is a Policy-Driven, Cryptographically Verifiable Universal Execution Fabric.** 

Designed for Tier-1 MSSPs, Military Cyber Commands, and Enterprise Security teams, SpectraStrike transcends traditional pentest automation. It operates as a Zero-Trust Offensive Infrastructure-as-a-Service (IaaS), providing mathematical non-repudiation for every executed operation and serving as the primary kinetic sensory array for the **VectorVue Security Assurance Platform**.

## Executive Summary

SpectraStrike is engineered under a strict **Assume Breach** model to prevent offensive infrastructure from becoming a weaponized C2 against the enterprise. It replaces vulnerable hardcoded script wrappers with an immutable, cryptographically signed BYOT (Bring Your Own Tool) execution pipeline. 

By separating tactical execution (SpectraStrike) from cognitive intelligence and compliance tracking (VectorVue), the platform provides:
- **Zero-Trust Capability Enforcement:** Every execution requires Open Policy Agent (OPA) authorization.
- **Cryptographic Execution (JWS):** Edge runners only execute payloads cryptographically signed by the Control Plane's HSM/Vault.
- **Hardware-Level Blast Radius Control:** Tools execute within sub-second ephemeral microVMs (Firecracker/gVisor).
- **Forensic Non-Repudiation:** An append-only Merkle Tree ledger mathematically proves exactly what was executed, when, and by whom.
- **VectorVue Interoperability:** High-throughput telemetry streaming (Kafka/RabbitMQ) feeds VectorVue's ML analytics and Phase 9 Continuous Compliance engines.

---

## Core Platform Architecture

### 1. Identity & Policy Plane (Zero-Trust)
- **Workload Identity:** SPIFFE/SPIRE dynamically provisions short-lived mTLS certificates for all microservices and edge runners. No static API keys.
- **Policy Engine:** Open Policy Agent (OPA) strictly gates all operations based on `[Operator Identity] + [Target URN] + [Tool Hash]`.
- **AAA Framework:** Advanced authentication, multi-tenant Row-Level Security (RLS) contexts, and multi-party computation for destructive actions.

### 2. Control Plane (Stateless Orchestrator)
- **Cryptographic Signer:** The Orchestrator evaluates the OPA policy and generates a JSON Web Signature (JWS) manifest via HashiCorp Vault.
- **The Armory (Tool Registry):** An internal, immutable OCI container registry storing heavily vetted, SBOM-scanned, and Cosign-signed tools (BYOT).
- **Task Scheduler & Event Loop:** Asynchronous routing engine.

### 3. Execution Plane (The Universal Edge)
- **The Universal Runner:** A lightweight, Go/Python-based edge binary that strictly validates the Orchestrator's JWS public key before initiating any code.
- **Ephemeral Sandboxing:** Arbitrary scripts and tools run inside strictly isolated microVMs with eBPF network fencing (restricting outbound traffic *only* to the authorized Target URN).
- **C2 Gateways:** Event-driven adapters (Sidecars) that securely synchronize stateful frameworks like Sliver and Mythic into the SpectraStrike schema without exposing the platform to direct RCE.

### 4. Telemetry & State Plane (VectorVue Sync)
- **Messaging Backbone:** Kafka/RabbitMQ streams standardized CloudEvents JSON telemetry.
- **Merkle Tree Ledger:** Tamper-evident, hash-chained audit trails upgraded to a mathematically verifiable Merkle Tree for enterprise compliance.
- **Bi-Directional Sync:** Ingests AI-driven action recommendations from VectorVue and pushes deterministic execution telemetry back to VectorVue's ML feature store.

---

## Current Delivery Status

SpectraStrike has completed its foundational layers and is currently executing its **Architectural Pivot (v2.0)** toward the Zero-Trust Universal Execution Fabric.

- **Phase 1-3 (Completed):** Core orchestrator, repository baseline, RabbitMQ messaging backbone (with retry, DLQ, idempotency), Web UI / Admin TUI foundation, and military-grade container hardening (mTLS, firewall baselines, SBOM gates).
- **Phase 4 (In Progress):** Replacing legacy wrappers (Nmap/Metasploit) with the **Cryptographic Payload Engine (JWS)**, The Armory (BYOT Registry), and the Universal Edge Runner.
- **Phase 5-9 (Roadmap):** OPA Integration, C2 Gateways (Sliver), the Merkle Tree Ledger, Kafka streaming migration, and AWS Firecracker MicroVM execution.

*Known QA block (tracked in kanban): Web UI dependency bootstrap may fail in restricted environments with DNS resolution error to npm registry (`EAI_AGAIN`), blocking `vitest`/`playwright` execution.*

---

## Quickstart (Development Baseline)

```bash
cp .env.example .env
make secrets-init
make tls-dev-cert
make pki-internal
make up
```

**UI Endpoints:**
- `https://localhost:${HOST_PROXY_TLS_PORT:-18443}/ui`
- `https://localhost:${HOST_PROXY_TLS_PORT:-18443}/ui/login`

**Admin TUI:**
```bash
make ui-admin-shell
```

---

## Legal, Governance & Compliance

SpectraStrike ships with native legal enforcement gates and enterprise-grade operational policies.

- `docs/DISCLAIMER.md`: Legal boundaries and operational liability framing.
- `docs/EULA.md`: Software license usage terms and constraints.
- `docs/ACCEPTABLE_USE_POLICY.md`: Authorized and prohibited security-testing behavior.
- `docs/PRIVACY_POLICY.md`: Data handling model across self-hosted and future SaaS.
- `docs/SECURITY_POLICY.md` & `SECURITY.md`: Internal controls and vulnerability disclosure.
- `docs/THREAT_MODEL.md`: Threat surfaces, mitigations, and residual-risk posture.
- `docs/ARCHITECTURE_SECURITY_OVERVIEW.md`: Layered architecture security controls.
- `docs/COMPLIANCE_STATEMENT.md`: Compliance-enablement posture.

**Runtime Governance Controls:**
- Environment-aware legal enforcement (`self-hosted`, `enterprise`, `saas`).
- Versioned legal acceptance invalidation with mandatory re-acceptance flows.
- Auth/Token gating via explicit `LEGAL_ACCEPTANCE_REQUIRED` middleware.

---

## QA and Security Gates

**Primary QA Execution:**
```bash
make test
make test-unit
make test-integration
make test-docker
./.venv/bin/pytest -q tests/qa/test_docs_qa.py
```

**Security and Policy Gates:**
```bash
make policy-check
make security-check
make security-gate
make full-regression
```

**Web UI QA (Dependency-ready environments):**
```bash
npm --prefix ui/web install --no-audit --no-fund
npm --prefix ui/web run test:unit
npm --prefix ui/web run test:e2e
```

---

## Documentation

- Roadmap: `docs/ROADMAP.md`
- Architecture Whitepaper: `docs/WHITEPAPER.md`
- Kanban board: `docs/kanban-board.csv`
- Manuals index: `docs/manuals/INDEX.md`
- Sprint engineering logs: `docs/dev-logs/INDEX.md`

## License

Business Source License 1.1 (BSL 1.1). See `LICENSE`.