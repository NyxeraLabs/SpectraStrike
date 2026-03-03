# Phase 5 Sprint 5.2 Summary

## Sprint objective
- Implement adversary graph modeling primitives and full campaign graph reconstruction from orchestrator state.

## Architectural decisions
- Added dedicated module `src/pkg/orchestrator/adversary_graph.py`.
- Reused `CampaignEngine` records and newly added read APIs for identities/lateral edges/escalations to avoid duplicating state.
- Modeled graph entities with immutable typed records (`AttackPathRecord`, `TechniqueLinkRecord`, `IdentityCompromiseChain`).
- Used deterministic BFS traversal for lateral path discovery.

## Risk considerations
- Current graph persistence is in-memory.
  - Mitigation: table-like typed models support later relational persistence with minimal adaptation.
- Technique-link derivation currently prioritizes ordered execution sequence and lateral relations.
  - Mitigation: relation types and weights are explicit and extensible for future calibration.
