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
- [x] Design orchestrator architecture
- [x] Implement async event loop
- [x] Implement task scheduler
- [x] Implement telemetry ingestion
- [x] Implement logging & audit trails
- [x] Implement AAA enforcement at engine level
- [x] Unit tests for orchestrator
- [x] Commit orchestrator code

### Sprint 3 (Week 5-6): Orchestrator QA
- [x] QA: run functional tests
- [x] QA: validate telemetry output
- [x] QA: AAA access verification

### Deliverables:
- [x] Core orchestrator engine implemented
- [x] Task scheduling, telemetry, logging, AAA fully functional
- [x] Baseline QA verification completed

---

## Phase 3: Integration Layer Development (Sprint 5-8)

### Sprint 4 (Week 7-8): API Integration
- [x] Design API client for VectorVue
- [x] Implement encrypted data transfer (TLS)
- [x] Implement retries / backoff
- [x] Implement event batching
- [x] Implement message signing for integrity
- [x] Commit integration code

### Sprint 5 (Week 9-10): API QA
- [x] QA: test API endpoints
- [x] QA: validate encrypted communication
- [x] QA: confirm telemetry reaches VectorVue

### Sprint 6 (Week 11-12): Nmap Wrapper Development
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

### Sprint 8 (Week 15-16): Metasploit Integration
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
- [x] Implement manual Metasploit ingestion connector (sessions + session-events pull)
- [x] Add checkpoint-based deduplication for Metasploit manual ingestion
- [x] Add CLI sync entrypoint for operator-driven Metasploit ingestion
- [x] Add unit/integration tests for manual ingestion flow
- [x] Commit end-to-end stabilization updates

### Sprint 9 (Week 17-18): Metasploit QA
- [x] QA: validate exploit runs (Metasploit)
- [x] QA: check telemetry delivery (Metasploit)

### Sprint 9.5 (Week 18): Messaging Backbone (Kafka/RabbitMQ)
- [x] Select broker standard (RabbitMQ) and define topic/queue model
- [x] Implement telemetry publisher abstraction (`TelemetryPublisher`)
- [x] Add broker-backed async delivery path for orchestrator telemetry
- [x] Add retry, dead-letter, and idempotency handling for broker delivery
- [x] Add integration tests for publish/consume flow
- [x] Add dockerized RabbitMQ runtime wiring + Makefile command targets
- [x] Add remote operator endpoint configuration (`MSF_RPC_*`, `MSF_MANUAL_*`, `RABBITMQ_*`)
- [x] Commit messaging backbone

### Sprint 9.6 (Week 18-19): User Interface Foundation (Before Cobalt Strike)
- [x] Define UI architecture and API contracts
- [x] Implement Web UI foundation with Next.js (App Router) + Tailwind CSS
- [x] Implement auth views and operator dashboard shell (Web UI)
- [x] Implement telemetry feed view (Nmap/Metasploit/Manual ingestion) (Web UI)
- [x] Implement findings and evidence navigation screens (Web UI)
- [x] Wire Web UI actions to orchestrator and integration endpoints
- [x] Add Web UI tests (component/unit + basic E2E)
- [x] Implement Interactive Terminal UI (Admin TUI) for operational control
- [ ] Add Admin TUI command workflows (task submission, telemetry watch, integration sync)
- [ ] Add Admin TUI tests and command-level QA checks
- [ ] Commit UI foundation (Web UI + Admin TUI)

### Sprint 9.7 (Week 19): Security & Container Platform Hardening (Before Cobalt Strike)
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

---

## Phase 4: Beacon & Scanning Tool Integration (Sprint 10-13)

### Sprint 10 (Week 19-20): Cobalt Strike Integration
- [ ] Connect to Cobalt Strike API
- [ ] Deploy beacon simulation (Cobalt Strike)
- [ ] Capture command output (Cobalt Strike)
- [ ] Log telemetry (Cobalt Strike)
- [ ] Implement retry/error handling (Cobalt Strike)
- [ ] Unit tests (Cobalt Strike)
- [ ] Commit wrapper (Cobalt Strike)

### Sprint 11 (Week 21-22): Cobalt Strike QA
- [ ] QA: verify beacon behavior (Cobalt Strike)
- [ ] QA: telemetry integration (Cobalt Strike)

### Sprint 12 (Week 23-24): Burp Suite Integration
- [ ] Setup Burp headless mode
- [ ] Configure target URLs (Burp)
- [ ] Automate spidering (Burp)
- [ ] Automate active scanning (Burp)
- [ ] Capture findings (Burp)
- [ ] Send to orchestrator (Burp)
- [ ] Unit tests (Burp)
- [ ] Commit wrapper (Burp)

### Sprint 13 (Week 25-26): Burp QA
- [ ] QA: validate scan coverage (Burp)
- [ ] QA: ensure AAA applied (Burp)

---

## Phase 5: Additional Tools & Wrappers (Sprint 14-18)

### Sprint 14: Gobuster / DirBuster Wrapper
- [ ] Implement wrapper module (Gobuster / DirBuster)
- [ ] Configure wordlists
- [ ] Automate directory scan
- [ ] Parse results
- [ ] Send to orchestrator
- [ ] Unit tests
- [ ] Commit wrapper

### Sprint 15: Gobuster QA
- [ ] QA: validate coverage
- [ ] QA: telemetry integration

### Sprint 16: Impacket Wrapper
- [ ] Implement wrapper (Impacket)
- [ ] Execute SMB/LDAP/NTLM tests
- [ ] Capture output
- [ ] Send telemetry
- [ ] Unit tests
- [ ] Commit wrapper

### Sprint 17: Impacket QA
- [ ] QA: verify network protocol handling
- [ ] QA: telemetry checks

### Sprint 18: BloodHound Wrapper
- [ ] Execute AD enumeration
- [ ] Build graph data
- [ ] Send to orchestrator
- [ ] Logging & telemetry
- [ ] Unit tests
- [ ] Commit wrapper

### Sprint 19: BloodHound QA
- [ ] QA: validate AD graph
- [ ] QA: telemetry delivery

---

## Phase 6: Cloud, Mobile & API Pentest Wrappers (Sprint 19-23)

### Sprint 20: Cloud & CI/CD Wrappers
- [ ] AWS SDK/Boto3 integration
- [ ] Azure SDK integration
- [ ] GCP SDK integration
- [ ] Jenkins / GitLab / GitHub Actions integration
- [ ] Terraform / Ansible checks
- [ ] Logging & telemetry (Cloud/CI)
- [ ] Unit tests (Cloud/CI)
- [ ] Commit wrapper (Cloud/CI)

### Sprint 21: Cloud QA
- [ ] QA: verify cloud data collection
- [ ] QA: CI/CD pipeline validation

### Sprint 22: Mobile/API/Web Pentest Wrappers
- [ ] Implement mobile scanner integration
- [ ] API fuzzing tools integration
- [ ] Web vulnerability scanners (OWASP ZAP)
- [ ] Capture results
- [ ] Send telemetry
- [ ] Unit tests
- [ ] Commit wrapper

### Sprint 23: Mobile/API/Web QA
- [ ] QA: validate scans
- [ ] QA: telemetry integration

---

## Phase 7: Red Team & Manual Testing Wrappers (Sprint 24-27)

### Sprint 24: Red Team Scenarios
- [ ] Implement ATT&CK scenarios
- [ ] Implement Chaos Monkey / Chaos Toolkit scripts
- [ ] Failure simulation scripts
- [ ] Logging & telemetry
- [ ] Unit tests
- [ ] Commit wrapper

### Sprint 25: Red Team QA
- [ ] QA: validate simulation scenarios
- [ ] QA: telemetry delivery

### Sprint 26: Manual Input API
- [ ] Design manual input API
- [ ] Implement authentication & authorization
- [ ] Implement audit logging
- [ ] Implement Metasploit manual-ingestion connector (pull sessions/events)
- [ ] Integrate manual results into orchestrator
- [ ] Unit tests
- [ ] Commit code

### Sprint 27: Manual QA
- [ ] QA: verify manual test ingestion
- [ ] QA: telemetry delivery

---

## Phase 8: AI Pentest Module & Final Integrations (Sprint 28-30)

### Sprint 28: AI Pentest Module
- [ ] Research AI pentest API
- [ ] Design integration layer (AI)
- [ ] Implement AI query module
- [ ] Send/receive results to orchestrator
- [ ] Logging & telemetry
- [ ] Unit tests
- [ ] Commit code

### Sprint 29: AI QA
- [ ] QA: validate AI suggestions
- [ ] QA: telemetry integration

### Sprint 30: Final Integration & VectorVue
- [ ] Finalize API calls for VectorVue
- [ ] Implement secure data push
- [ ] Verify event batching
- [ ] End-to-end test with SpectraStrike
- [ ] Logging & telemetry
- [ ] Unit tests
- [ ] Commit code

### Sprint 31: Final QA
- [ ] QA: end-to-end validation
- [ ] QA: verify AAA & audit logging
- [ ] QA: confirm telemetry accuracy

---

## Phase 9: Documentation & Release (Sprint 32-33)

### Sprint 32: Documentation
- [ ] Write user documentation
- [ ] Write developer documentation

### Sprint 33: Release Preparation
- [ ] Prepare deployment scripts
- [ ] Final QA review
- [ ] Final commit
- [ ] Tag release in Git
- [ ] QA: documentation review
- [ ] QA: final regression tests
