# Sprint 40: ATT&CK Relational Layer

## Implemented relational tables (service-level)

1. `Tactic` table
- Backed by `AttackTactic`
- Includes canonical tactic IDs (`TA0001` ... `TA0040`)

2. `Technique` table
- Backed by `AttackTechnique`
- Stores parent techniques (`T####`)

3. `SubTechnique` table
- Backed by `AttackSubTechnique`
- Stores sub-techniques (`T####.###`) linked to parent technique

4. Technique -> Tactic mapping
- `TechniqueTacticMapping`

5. Technique -> Platform mapping
- `TechniquePlatformMapping`

6. Technique -> Data Source mapping
- `TechniqueDataSourceMapping`

7. Technique -> Mitigation mapping
- `TechniqueMitigationMapping`

8. Technique -> Detection Guidance mapping
- `TechniqueDetectionGuidanceMapping`

## ATT&CK import automation pipeline
- Service import entrypoint: `AttackBackboneService.import_from_reference(...)`
- CLI automation script: `VectorVue/scripts/import_attack_backbone.py`
- Supports optional metadata enrichment JSON for mapping blocks:
  - `tactics`
  - `platforms`
  - `data_sources`
  - `mitigations`
  - `detection_guidance`

## Sync guarantees
- Idempotent sync semantics (set-backed mapping tables).
- Sub-techniques auto-link to parent technique.
- Default tactic inference for known technique families (`T1059`, `T1021`, etc.) when metadata is absent.
