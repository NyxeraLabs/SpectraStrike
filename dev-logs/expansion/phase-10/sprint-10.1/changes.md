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
- Added workflow picker capabilities:
  - search
  - category filter
  - per-section collapse/expand
- Added ASM picker capabilities:
  - categories: Domains, Subdomains, IP Ranges, Cloud Assets, Surfaces, Exposures, Integrations
  - search + category filter
  - drag-and-drop from picker onto canvas
  - reset graph from zero action
- Removed Nexus demo-query panel and demo-step controls from web UI flow.
- Updated ASM dashboard page wrappers to hide top chrome in fullscreen mode.
- Updated roadmap expansion with Sprint 60 entry in `docs/ROADMAP_EXPANSION.md`.

## Not Included In This Tranche
- Full guided interaction engine implementation.
- Full playbook next-gen inspector/versioning/simulation system.
- VectorVue web timeline and guided TUI progression.
- Help drawer/manual indexing system.

## Incremental Fix - Workflow Client Exception (Runtime Hardening)
- Fixed workflow runtime hydration path to safely ignore malformed/null `queue` and `playbook.nodes` items from backend APIs.
- Removed stale spotlight conditional comparisons that were type-invalid and no longer backed by runtime state.
- Searched and fixed similar unsafe list-hydration patterns in SpectraStrike UI:
  - `app/components/asm-workbench.tsx`
  - `app/components/telemetry-feed.tsx`
- Added record-guard filtering before object property access on API item arrays.
- Validated workflow unit test path after changes.

## Incremental Fix - Demo Reset Authentication Failure
- Fixed `scripts/reset_demo_runtime.py` to authenticate via `/v1/auth/login` (bootstrap operator credentials) instead of removed `/v1/auth/demo`.
- Added legal-accept retry handling during bootstrap login (`LEGAL_ACCEPTANCE_REQUIRED` path).
- Added per-candidate endpoint error aggregation in reset failures to improve root-cause visibility.
- Aligned `scripts/seed_demo_runtime.py` with the same login-first authentication strategy and legal-accept retry behavior.

## Incremental UX + Seeding Improvements
- Added campaign selection in workflow UI to switch tenant-scoped playbook context:
  - ACME (`10000000-0000-0000-0000-000000000001`)
  - Globex (`20000000-0000-0000-0000-000000000002`)
- Wired selected campaign into:
  - playbook load (`GET /ui/api/execution/playbook?tenant_id=...`)
  - playbook persistence (`PUT /ui/api/execution/playbook` with `tenant_id`)
  - task execution (`POST /ui/api/actions/tasks` with `tenant_id`)
- Updated `make demo-seed` output to print SpectraStrike web login credentials and URL.

## Incremental UX - Campaign Timeline Load/Unload Bar
- Added timeline control bar to Workflow Playbook Builder:
  - range slider from `0..N` steps
  - `Load All` button
  - `Unload` button
- Timeline list now renders only the loaded subset (`nodes.slice(0, loadedCount)`).
- Added empty-state hint when timeline is explicitly unloaded while nodes exist.

## Incremental UX - Permission-Scoped Tenant + Campaign Selectors
- Replaced static workflow campaign dropdown with:
  - Tenant selector (role/permission scoped)
  - Campaign selector scoped to selected tenant
- Added new API route `GET /ui/api/execution/context` to supply visible tenants and their campaigns.
- Updated workflow playbook load/save to send both `tenant_id` and `campaign_id`.
- Updated task execution payload to keep `tenant_id` explicit and include `campaign_id` in parameters.
