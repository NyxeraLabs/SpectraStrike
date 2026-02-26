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
- Status: Completed
- Primary Architecture Layers: Identity and Policy Plane, Execution Plane

## Architectural Intent

Validate zero-trust denial controls and execution containment guarantees.

## Implementation Detail

Added explicit Sprint 17 QA suite:
- OPA denies unauthorized tool hash execution attempts.
- OPA denies authorized tool execution against unauthorized target URNs.
- Runner dynamic Cilium policy reflects deny-by-default containment and target egress allowlist.
- Added carry-over QA gate for Sprint 16.5, 16.7, and 16.8 regressions.

## Security and Control Posture

- OPA pre-sign authorization denials are validated for malicious insider scenarios.
- Runner network fencing controls are validated for lateral movement resistance.
- Security posture remains aligned with policy-driven control plane goals in Phase 5.

## QA and Validation Evidence

Command:
- `PYTHONPATH=src .venv/bin/pytest -q tests/qa/test_zero_trust_sprint17_qa.py`

Result:
- `3 passed`
- `28 passed` (carry-over validation set for Sprint 16.5/16.7/16.8)

## Risk Register

Residual risk is environment-specific Cilium runtime variance outside fixture scope.
Mitigation is controlled live validation in target cluster lanes.

## Forward Linkage

Sprint 18 begins C2 gateway architecture baseline.
