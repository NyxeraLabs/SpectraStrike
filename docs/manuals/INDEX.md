# SpectraStrike Documentation Index

**Author:** José María Micoli  
**IP Holder:** Nyxera Labs  
**License:** Business Source License 1.1 (BSL 1.1)

---

## Table of Contents

### 1. Introduction
- [Overview of SpectraStrike](docs/introduction/overview.md)
- [Key Features](docs/introduction/features.md)
- [Architecture Overview](docs/introduction/architecture.md)
- [System Requirements](docs/introduction/requirements.md)
- [Installation & Setup](docs/introduction/installation.md)
- [Security & Compliance](docs/introduction/security.md)

---

### 2. Phase 1 – Setup & Environment Initialization
- [Repository Setup & Git Initialization](docs/phase1/git_setup.md)
- [Python Virtual Environment](docs/phase1/python_venv.md)
- [Core Dependencies Installation](docs/phase1/core_dependencies.md)
- [Docker Development Containers](docs/phase1/docker.md)
- [IDE Configuration](docs/phase1/ide.md)
- [Pre-commit Hooks & Git Branching](docs/phase1/git_hooks_branching.md)
- [CI/CD Pipeline Setup](docs/phase1/cicd.md)
- [Logging & AAA Framework](docs/phase1/logging_aaa.md)
- [Phase 1 QA](docs/phase1/qa.md)

---

### 3. Phase 2 – Orchestrator Core
- [Orchestrator Architecture](docs/phase2/architecture.md)
- [Async Event Loop Implementation](docs/phase2/event_loop.md)
- [Task Scheduler](docs/phase2/task_scheduler.md)
- [Telemetry Ingestion](docs/phase2/telemetry.md)
- [Logging & Audit Trails](docs/phase2/logging_audit.md)
- [AAA Enforcement](docs/phase2/aaa.md)
- [Unit Tests](docs/phase2/unit_tests.md)
- [Orchestrator Commit & Versioning](docs/phase2/commit.md)
- [Phase 2 QA](docs/phase2/qa.md)

---

### 4. Phase 3 – Integration Layer
- [VectorVue API Client](docs/phase3/vectorvue_client.md)
- [Encrypted Data Transfer (TLS)](docs/phase3/encryption.md)
- [Retries, Backoff & Event Batching](docs/phase3/retries_batching.md)
- [Message Signing & Integrity](docs/phase3/message_signing.md)
- [Integration Commits](docs/phase3/commit.md)
- [Phase 3 QA](docs/phase3/qa.md)

---

### 5. Phase 4 – Tool Wrappers & Automation
- **Nmap Wrapper**
  - [TCP & UDP Scans](docs/phase4/nmap_scans.md)
  - [OS Detection & Result Parsing](docs/phase4/nmap_os_parsing.md)
  - [Telemetry Integration](docs/phase4/nmap_telemetry.md)
  - [Unit Tests & Commits](docs/phase4/nmap_tests_commit.md)
  - [QA Validation](docs/phase4/nmap_qa.md)

- **Metasploit Wrapper**
  - [RPC Connection & Module Loader](docs/phase4/metasploit_loader.md)
  - [Exploit Execution](docs/phase4/metasploit_execute.md)
  - [Session Capture & Telemetry](docs/phase4/metasploit_telemetry.md)
  - [Retries/Error Handling](docs/phase4/metasploit_retries.md)
  - [Unit Tests & Commits](docs/phase4/metasploit_tests_commit.md)
  - [QA Validation](docs/phase4/metasploit_qa.md)

- **Cobalt Strike, Burp Suite, Gobuster/DirBuster, Impacket, BloodHound**
  - Each module will have:
    - [Wrapper Implementation](docs/phase4/<module>_wrapper.md)
    - [Unit Tests](docs/phase4/<module>_tests.md)
    - [Telemetry Integration](docs/phase4/<module>_telemetry.md)
    - [QA Validation](docs/phase4/<module>_qa.md)

---

### 6. Phase 5 – Cloud, Mobile & API Pentesting
- [Cloud & CI/CD Wrappers](docs/phase5/cloud_ci_cd.md)
- [Mobile/API/Web Wrappers](docs/phase5/mobile_api_web.md)
- [Unit Tests & Telemetry](docs/phase5/unit_telemetry.md)
- [QA Validation](docs/phase5/qa.md)

---

### 7. Phase 6 – Red Team Simulations
- [ATT&CK Scenario Execution](docs/phase6/attack_scenarios.md)
- [Chaos Monkey / Chaos Toolkit Scripts](docs/phase6/chaos.md)
- [Failure Simulation & Telemetry](docs/phase6/failure_sim.md)
- [Unit Tests & Commits](docs/phase6/unit_commit.md)
- [QA Validation](docs/phase6/qa.md)

---

### 8. Phase 7 – Manual Pentesting Integration
- [Manual Input API](docs/phase7/manual_api.md)
- [Authentication & Authorization](docs/phase7/aaa_manual.md)
- [Audit Logging](docs/phase7/audit_manual.md)
- [Integration with Orchestrator](docs/phase7/integration_manual.md)
- [Unit Tests & Commits](docs/phase7/unit_commit.md)
- [QA Validation](docs/phase7/qa.md)

---

### 9. Phase 8 – AI Pentesting Modules
- [AI Pentest API Research](docs/phase8/ai_research.md)
- [Integration Layer Design](docs/phase8/ai_integration.md)
- [AI Query Module](docs/phase8/ai_query.md)
- [Telemetry & Logging](docs/phase8/ai_telemetry.md)
- [Unit Tests & Commits](docs/phase8/unit_commit.md)
- [QA Validation](docs/phase8/qa.md)

---

### 10. Phase 9 – Final Integration & Release
- [VectorVue Final Integration](docs/phase9/vectorvue_final.md)
- [End-to-End Testing](docs/phase9/e2e_testing.md)
- [Telemetry & AAA Checks](docs/phase9/telemetry_aaa.md)
- [Deployment Scripts](docs/phase9/deployment.md)
- [Documentation Review](docs/phase9/docs_review.md)
- [Final QA & Regression Tests](docs/phase9/final_qa.md)
- [Release Tagging & Versioning](docs/phase9/release.md)

---

### 11. User & Developer Guides
- [User Guide – Basic Operations](docs/guides/user_guide.md)
- [Developer Guide – Modules & API](docs/guides/developer_guide.md)
- [Troubleshooting & FAQ](docs/guides/troubleshooting.md)
- [Best Practices & Security](docs/guides/best_practices.md)

---

### Notes

- Each phase section should be **updated progressively as tasks are completed**.  
- Links point to **phase-specific documentation** which contains **step-by-step instructions, code examples, telemetry info, unit tests, and QA procedures**.  
- Designed for **commercial boutique clients** and internal security teams.  
- Use this index as the **master navigation hub** for SpectraStrike’s full documentation.