# Detection Validation Methodology - Phase 9 Sprint 9.2

## 1. Purpose
Measure whether defensive controls detect and contain realistic adversary behavior, not just whether telemetry exists.

## 2. Validation Dimensions
- ATT&CK coverage (technique observed vs expected)
- Detection latency (time-to-detect)
- Alert quality and triage outcome
- False-negative indicators
- Response and containment confirmation

## 3. Evidence Chain
- Campaign step execution evidence from SpectraStrike
- Detection and confidence metrics from VectorVue
- Remediation and containment status
- Compliance/control mapping where applicable

## 4. Scoring Inputs
- Technique confidence
- Detection effectiveness index
- Control validation matrix results (EDR/XDR/NGFW/AV)
- SOC performance metrics (MTTD/MTTR/containment)

## 5. QA Validation Loop
1. Execute controlled campaign scenario.
2. Verify detection mapping and timing.
3. Compare expected vs observed containment actions.
4. Flag gaps and generate remediation tasks.
5. Re-run cycle and compare multi-cycle deltas.
