# Technical Notes

## Demo Surface Removal
- Login screen no longer invokes `/ui/api/v1/auth/demo`.
- API route `app/api/v1/auth/demo/route.ts` removed from UI service surface.
- Workflow component no longer renders the guided-demo panel block.

## Shared Fullscreen Controller
- New hook: `useFullscreenController(target?: HTMLElement | null)`
- Behavior:
  - Uses native Fullscreen API when available.
  - Falls back to CSS-driven fullscreen mode when native request fails.
  - Applies/removes global classes:
    - `document.body.classList.toggle('spectra-fullscreen-active', ...)`
    - `document.documentElement.classList.toggle('spectra-fullscreen-active', ...)`
  - Forces body overflow lock in fullscreen.
  - Handles ESC in fallback mode.

## Workflow Integration
- Workflow canvas now delegates fullscreen state and toggling to shared hook.
- Removed local fullscreen event wiring/DOM class management from workflow component.
- Workflow picker now supports local filtering and dynamic grouped rendering by wrapper bucket.
- Section collapse state is maintained client-side in `pickerSectionOpen`.

## ASM Integration
- ASM canvas now delegates fullscreen state/toggling to shared hook.
- Removed ASM-specific body overflow side-effect logic.
- Canvas fullscreen class normalized to `canvas-fullscreen` for parity with workflow.
- ASM picker now uses explicit section metadata (`domains`, `subdomains`, `ip_ranges`, `cloud_assets`, `surfaces`, `exposures`, `integrations`).
- Picker-to-canvas placement implemented via drag payload key `application/spectrastrike-asm-picker` and ReactFlow projection.
- Added graph reset action to support rebuild-from-zero workflows.

## Layout/Chrome Behavior
- ASM page now uses `spectra-fullscreen-hide` wrappers around top navigation and page intro panel.
- This aligns with existing workflow fullscreen chrome-hide behavior.

## Nexus UI Mode Separation
- Removed demo query branching and demo-step UI panel from Nexus workbench.
- VectorVue deep-link now always resolves through contextual deep-link builder rather than demo query toggles.

## Workflow Exception Remediation
- Added local `isRecord` runtime guards in workflow hydration paths to protect against null/non-object elements from:
  - `/ui/api/execution/queue`
  - `/ui/api/execution/playbook`
- In queue status mapping:
  - unknown/non-runtime statuses are skipped
  - non-object queue rows are skipped
  - non-object playbook node rows are skipped
- Removed stale `activeSpotlight` branch-condition class logic from workflow panel markup (no active spotlight state was driving it).

## Similar-Error Sweep (SpectraStrike UI)
- `asm-workbench.tsx`:
  - queue/telemetry arrays now pre-filter to object records before property access.
- `telemetry-feed.tsx`:
  - wrappers/telemetry item arrays now pre-filter to object records before mapping.
  - loaded-count message now reflects filtered/safe item count.

## Demo Runtime Auth Path Correction
- `reset_demo_runtime.py` no longer performs demo-auth probing as primary auth flow.
- New auth sequence for reset:
  1) `POST /v1/auth/login` with bootstrap credentials
  2) if `LEGAL_ACCEPTANCE_REQUIRED`, call `POST /v1/auth/legal/accept`
  3) retry `POST /v1/auth/login`
  4) use bearer token for `POST /execution/reset`
- Reset error output now includes endpoint-specific failure context across all candidate API bases.

## Seed Runtime Parity
- `seed_demo_runtime.py` token resolver now also uses bootstrap login-first with legal-accept retry.
- This prevents seed/reset divergence after removal of UI demo auth route.
