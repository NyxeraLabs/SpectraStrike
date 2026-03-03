# ASM Methodology Guide - Phase 9 Sprint 9.2

## 1. Objective
Continuously map external exposure posture into adversary-relevant attack paths that inform campaign planning.

## 2. ASM Workflow
1. Discover assets and normalize ownership.
2. Correlate exposures to assets and service context.
3. Map exposures to ATT&CK-aligned entry techniques.
4. Build pivot paths from external to internal assets.
5. Convert prioritized exposure paths into playbook candidate actions.

## 3. Risk Prioritization Inputs
- Asset criticality
- Exposure severity
- Reachability/pivotability
- Identity/IAM blast radius
- Existing control validation evidence

## 4. Output Artifacts
- Asset graph with relation overlays.
- Exposure linkage inventory.
- External-to-internal pivot chain candidates.
- Campaign suggestion bundle with ranked actions.

## 5. Governance
- Ensure source data is tenant-scoped.
- Track methodology version with each generated risk artifact.
- Preserve historical exposure graph snapshots for trend auditing.
