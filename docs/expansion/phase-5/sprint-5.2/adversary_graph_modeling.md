# Sprint 48: Adversary Graph Modeling

## AttackPath and TechniqueLink models
- Added `AttackPathRecord` (`AttackPath` table abstraction).
- Added `TechniqueLinkRecord` (`TechniqueLink` edge table abstraction).
- Added `IdentityCompromiseChain` model for identity-centric compromise progression.

## Graph traversal engine
- Added `traverse_lateral_paths(...)`:
  - breadth-first traversal over lateral edges
  - cycle-safe path generation
  - depth-bounded exploration
  - emits `AttackPathRecord` paths

## Privilege escalation path modeling
- Added `model_privilege_escalation_paths(...)`.
- Converts ordered privilege levels and execution lineage into normalized escalation paths.

## Lateral movement path modeling
- Traversal and reconstruction now model ordered asset pivots using campaign lateral edges.
- Generated attack paths include edge lineage and bounded risk scoring.

## Identity compromise chain modeling
- Added `model_identity_compromise_chain(...)` with:
  - credential artifacts
  - privilege-level progression
  - pivot asset sequence
  - escalation execution references

## Full campaign graph reconstruction
- Added `reconstruct_campaign_graph(...)` that fuses:
  - campaign steps and executions
  - technique links from execution sequence
  - identity credentials/escalations
  - lateral movement edges and pivot chains
- Produces `CampaignGraphReconstruction` bundle.

## Validation
- Added unit tests for:
  - full campaign graph reconstruction
  - traversal engine path discovery
