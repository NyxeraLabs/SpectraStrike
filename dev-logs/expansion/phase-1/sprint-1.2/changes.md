# Phase 1 Sprint 1.2 Changes

## File-by-file change explanation

### `SpectraStrike/src/pkg/orchestrator/campaign_engine.py`
- Added privilege classification enum (`PrivilegeLevel`).
- Added credential material type enum (`CredentialMaterialType`).
- Added identity model (`IdentityRecord`).
- Added credential material tracking model (`CredentialMaterialRecord`).
- Added privilege escalation event model (`PrivilegeEscalationRecord`).
- Added lateral movement edge model (`LateralMovementEdge`).
- Added pivot chain projection model (`PivotChain`).
- Added operations for identity creation, credential capture, escalation tracking, lateral edge persistence, and pivot-chain reconstruction.

### `SpectraStrike/src/pkg/orchestrator/__init__.py`
- Exported new identity/pivot domain models and enums.

### `SpectraStrike/tests/unit/test_campaign_identity_pivot.py`
- Added pivot chain reconstruction test with multi-step escalation and lateral movement sequence.
- Validates compromised account attribution and identity-level credential history.

### `SpectraStrike/docs/expansion/phase-1/sprint-1.2/identity_pivot_modeling.md`
- Added architecture reference for identity/pivot data structures and behavior.

### `SpectraStrike/docs/ROADMAP_EXPANSION.md`
- Marked Sprint 39 checklist items complete.

## Reason for each change
- Deliver Sprint 39 identity/pivot modeling requirements with concrete data contracts and reconstruction validation.
