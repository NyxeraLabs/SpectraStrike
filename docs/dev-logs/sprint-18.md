<!--
Copyright (c) 2026 NyxeraLabs
Author: José María Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# Sprint 18 Engineering Log

## Program Context

- Phase: Phase 5
- Sprint: Sprint 18
- Status: Planned
- Primary Architecture Layers: Detection Engine, Telemetry Ingestion, Correlation Core

## Architectural Intent

Implement AD graph collection and orchestrator-aligned telemetry export from BloodHound workflows.

## Implementation Detail

Planned work includes AD enumeration execution, graph data transformation, telemetry publication, and observability hooks.

## Security and Control Posture

- AAA scope and authorization boundaries are enforced according to current orchestrator policy.
- Telemetry and audit events are expected to remain structured, attributable, and export-ready.
- Integration interfaces are maintained as loosely coupled contracts to preserve VectorVue interoperability.

## QA and Validation Evidence

Unit and integration test design planned for graph-model mapping and ingestion behavior.

## Risk Register

Risk includes large graph payload handling and schema drift; mitigation via normalized contracts and bounded ingestion paths.

## Forward Linkage

Sprint 19 executes BloodHound QA.
