<!--
Copyright (c) 2026 NyxeraLabs
Author: José María Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# SpectraStrike Compliance Statement

## 1. Scope and Intent

SpectraStrike provides control enablement for enterprise security validation programs.

The platform is engineered to support compliance evidence production, but SpectraStrike itself does not automatically certify an organization for any framework.

## 2. Control Domains Supported

SpectraStrike contributes implementation and evidence support to common control families:
- Access control and least privilege (AAA, role controls, lockout, optional MFA)
- Auditability and traceability (structured logs, audit chain)
- Change control and release evidence (roadmap, kanban, sprint logs, QA runbook)
- Data security in transit (TLS and internal mTLS)
- Security operations governance (policy checks, regression gates, security scripts)

## 3. Framework Mapping Posture

SpectraStrike can be mapped by customer governance teams to:
- SOC 2 Security/Availability principles
- ISO 27001 Annex A controls
- NIST CSF function categories
- CIS Controls implementation practices
- GDPR security and accountability obligations

Sprint 32 implementation package:
- `docs/compliance/SOC2_CONTROL_MAPPING.md`
- `docs/compliance/ISO27001_ANNEXA_MAPPING.md`
- `docs/compliance/NIST_800_53_MAPPING.md`
- `docs/compliance/MITRE_ATTACK_TELEMETRY_MAPPING.md`
- `docs/compliance/SECURE_SDLC_PACKAGE.md`

## 4. Evidence Artifacts Produced by Platform

Core artifacts available for audits and internal assurance:
- task and telemetry execution traces
- role-attributed operational logs
- QA run outputs and blocker records
- security gate evidence (policy checks, vulnerability scans, SBOM generation)
- roadmap and sprint governance records

## 5. Customer Responsibilities

Customers remain responsible for:
- lawful authorization and scope management for offensive validation activities
- deployment hardening and key/secrets management
- framework interpretation and legal/regulatory applicability
- retention policies and data residency controls

## 6. Nyxera Labs Responsibilities

Nyxera Labs provides:
- platform-level security controls and documented architecture
- release governance artifacts and operational runbooks
- defect remediation process for reported vulnerabilities

## 7. Continuous Compliance Model

Compliance readiness is treated as a continuous engineering process:
- controls are versioned and verifiable
- blockers are recorded with evidence
- QA gates are tied to release decisions
- documentation is maintained as a first-class control artifact
