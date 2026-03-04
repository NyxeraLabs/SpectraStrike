# Sprint 10.1 Changes (Global Sprint 60)

## Scope
- SpectraStrike UI web only.
- Focused tranche from the multi-part directive:
  - Part 1: remove UI-level demo trigger/routes.
  - Part 2: shared fullscreen parity for Workflow + ASM canvases.

## Implemented
- Removed Demo Shell button and client-side demo auth call from login screen.
- Removed `app/api/v1/auth/demo/route.ts` (UI-exposed demo auth route).
- Removed workflow demo panel rendering from workflow workbench.
- Changed first-run message from demo language to configuration language.
- Added shared fullscreen controller hook:
  - `app/lib/fullscreen-controller.ts`
- Integrated fullscreen controller in:
  - `app/components/workflow-workbench.tsx`
  - `app/components/asm-workbench.tsx`
- Updated ASM dashboard page wrappers to hide top chrome in fullscreen mode.
- Updated roadmap expansion with Sprint 60 entry in `docs/ROADMAP_EXPANSION.md`.

## Not Included In This Tranche
- Full guided interaction engine implementation.
- Full playbook next-gen inspector/versioning/simulation system.
- VectorVue web timeline and guided TUI progression.
- Help drawer/manual indexing system.
