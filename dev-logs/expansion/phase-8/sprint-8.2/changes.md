# Changes - Phase 8 Sprint 8.2

## File-by-file changes
- `ui/web/app/lib/asm-graph.ts`
  - Added ASM graph model/types, default graph, risk overlays, mapping integrity validation, large graph builder, and playbook conversion logic.
  - Reused graph-core via `reorderNodes` from `workflow-graph.ts` to keep drag behavior consistent.

- `ui/web/app/components/asm-workbench.tsx`
  - Added ASM graph UI panels for visualization, DnD builder, exposure links, vulnerability mapping, pivot paths, IAM graph, risk overlays, and playbook conversion.

- `ui/web/app/dashboard/asm/page.tsx`
  - Added new ASM page route integrating `TopNav` and `AsmWorkbench`.

- `ui/web/app/components/top-nav.tsx`
  - Added `ASM` navigation item pointing to `/dashboard/asm`.

- `ui/web/tests/unit/asm-large-graph-render.test.tsx`
  - Added large graph rendering/performance-oriented validation test.

- `ui/web/tests/unit/asm-exposure-mapping-integrity.test.ts`
  - Added coverage/integrity test for exposure mappings and playbook conversion ordering.

- `docs/expansion/phase-8/sprint-8.2/asm_graph_engine.md`
  - Added sprint architecture and validation document.

## Reason for each change
- Deliver all Sprint 54 ASM UI commits with explicit graph-core reuse and verifiable integrity/performance behavior.
