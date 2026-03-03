# Phase 2 Sprint 2.1 Summary

## Sprint objective
- Build a relational ATT&CK backbone with import automation and mapping coverage.

## Architectural decisions
- Implemented ATT&CK relational layer as a dedicated VectorVue service (`services/attack_backbone.py`) to avoid further monolith expansion in `vv_core.py`.
- Modeled ATT&CK tables and many-to-many mappings explicitly using typed records and set-backed idempotent indexes.
- Added import CLI script for repeatable synchronization from `mitre_reference.txt` plus optional metadata enrichment.

## Risk considerations
- In-memory service is not persisted to DB yet.
  - Mitigation: explicit typed relational contracts and sync summary enable straightforward persistence adapter in a later sprint.
- Default tactic inference is heuristic for techniques without metadata.
  - Mitigation: metadata file can override/expand mappings during import.
