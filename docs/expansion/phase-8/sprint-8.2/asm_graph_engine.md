# Sprint 54 (Phase 8 Sprint 8.2) - ASM Graph Engine

## Objective
Deliver graph-native ASM modeling in SpectraStrike UI with shared graph-core behavior and conversion into playbook actions.

## Architecture
- Reused shared graph-core reordering semantics by mapping ASM nodes through `workflow-graph.ts` utilities.
- Implemented ASM-specific graph model in `app/lib/asm-graph.ts` for assets, relationships, exposure mappings, and conversion helpers.
- Added route-level UI at `/dashboard/asm` using a dedicated `AsmWorkbench` component.

## Coverage Against Sprint Commits
- Asset graph visualization engine: SVG-based asset graph in workbench.
- Drag-and-drop asset relationship builder: draggable node list with graph-core reorder.
- Exposure-to-asset linking visualization: asset selector + mapped exposure panel.
- Vulnerability relationship mapping: relation count panel.
- External-to-internal pivot path visualization: pivot sequence panel.
- Cloud IAM & role relationship graph: IAM assume-role list.
- Exposure risk overlay scoring visualization: per-asset risk overlays.
- Convert exposure graph to playbook action: deterministic action list.
- Tests: large graph render test + exposure mapping integrity test.

## Validation
- Unit tests: ASM + workflow regression suite passed.
- Build: Next.js production build passed and `/dashboard/asm` generated successfully.
