<!--
Copyright (c) 2026 NyxeraLabs
Author: José María Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# SpectraStrike Threat Model

## 1. System Boundaries

SpectraStrike spans these trust zones:
- operator interfaces (web UI, admin TUI)
- orchestrator runtime and internal service mesh
- integration adapters (tool wrappers and external APIs)
- telemetry broker and storage services
- governance/evidence artifacts

## 2. Protected Assets

Primary assets:
- operator credentials and session artifacts
- orchestrator task definitions and execution metadata
- telemetry streams and normalized findings
- audit logs and compliance evidence
- integration credentials and endpoint trust anchors

## 3. Threat Actors

- unauthorized external attacker
- malicious or negligent insider
- compromised integration endpoint
- supply-chain adversary targeting dependencies/images
- unauthorized operator using out-of-scope targets

## 4. Attack Surfaces

- authentication and action APIs
- ingestion and integration endpoints
- admin command interfaces
- container runtime and exposed network ports
- dependency/bootstrap channels (package registries)

## 5. Threat Categories and Mitigations

### Identity Compromise
Mitigations:
- AAA controls, lockout, optional MFA
- session validation and role checks

### Data/Telemetry Tampering
Mitigations:
- structured event models
- audit chain integrity controls
- transport security and endpoint controls

### Orchestrator Abuse
Mitigations:
- scoped task submission contracts
- explicit action logging and attribution
- policy checks and release gates

### Infrastructure Compromise
Mitigations:
- hardened container profile
- TLS/mTLS boundaries
- segmentation and minimized exposure

### Supply-Chain and Dependency Risk
Mitigations:
- SBOM, vulnerability scanning, image signature workflows
- blocker recording when dependency bootstrap cannot be verified

## 6. Residual Risks

- dependency acquisition failures in isolated environments (e.g., npm DNS resolution)
- variable behavior from external integration APIs
- operator misuse outside authorized scope

Residual risks must be captured in roadmap/kanban and linked to remediation actions.
