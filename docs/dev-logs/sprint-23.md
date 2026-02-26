<!--
Copyright (c) 2026 NyxeraLabs
Author: José María Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# Sprint 23 Engineering Log

## Program Context

- Phase: Phase 5.6
- Sprint: Sprint 23
- Status: Completed
- Primary Architecture Layers: Federation Gateway, Integration Bridge, Audit Plane

## Architectural Intent

Enforce single secure federation channel for VectorVue telemetry and remove legacy emission paths.

## Implementation Detail

Completed Sprint 23 controls:
- Enforced single outbound telemetry gateway path via `send_federated_telemetry`.
- Removed legacy direct API emission branch from bridge runtime path.
- Enforced mTLS-only outbound federation preconditions (cert/key + TLS verification).
- Enforced signed telemetry requirement for federation outbound (no unsigned fallback).
- Added producer-side replay nonce detection in bridge dispatch flow.
- Enforced bounded retry with idempotent fingerprint key (execution fingerprint as idempotency key).
- Added federation smoke QA suite and regression coverage.

## Security and Control Posture

- Gateway dispatch path is now fail-closed on missing mTLS/signature configuration.
- Replay and fingerprint mismatch conditions are blocked before outbound federation dispatch.
- Legacy direct integration path is no longer available in bridge CLI/runtime.

## QA and Validation Evidence

Commands:
- `PYTHONPATH=src .venv/bin/pytest -q tests/unit/integration/test_vectorvue_rabbitmq_bridge.py`
- `PYTHONPATH=src .venv/bin/pytest -q tests/unit/integration/test_vectorvue_client.py`
- `PYTHONPATH=src .venv/bin/pytest -q tests/qa/test_sprint23_federation_channel_qa.py`

## Risk Register

Residual risk:
- Ed25519 asymmetric signing migration is still represented through current signature header control and should be hardened in a follow-on cryptographic key provider iteration.

## Forward Linkage

Sprint 24 implements anti-repudiation closure with write-ahead intent records and verification APIs.
