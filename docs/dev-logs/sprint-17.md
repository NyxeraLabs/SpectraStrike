<!--
Copyright (c) 2026 NyxeraLabs
Author: José María Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# Sprint 17 Engineering Log

## Program Context

- Phase: Phase 5
- Sprint: Sprint 17
- Status: Planned
- Primary Architecture Layers: Detection Engine, Reporting / Compliance

## Architectural Intent

Validate protocol handling fidelity and telemetry correctness for Impacket integrations.

## Implementation Detail

QA strategy includes protocol-specific fixtures, error-path checks, and telemetry schema verification.

## Security and Control Posture

- AAA scope and authorization boundaries are enforced according to current orchestrator policy.
- Telemetry and audit events are expected to remain structured, attributable, and export-ready.
- Integration interfaces are maintained as loosely coupled contracts to preserve VectorVue interoperability.

## QA and Validation Evidence

Planned QA includes regression checks for SMB/LDAP/NTLM result normalization.

## Risk Register

Risk is protocol edge-case undercoverage; mitigation through broadened fixture catalog.

## Forward Linkage

Sprint 18 starts BloodHound wrapper implementation.
