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

## ASM Integration
- ASM canvas now delegates fullscreen state/toggling to shared hook.
- Removed ASM-specific body overflow side-effect logic.
- Canvas fullscreen class normalized to `canvas-fullscreen` for parity with workflow.

## Layout/Chrome Behavior
- ASM page now uses `spectra-fullscreen-hide` wrappers around top navigation and page intro panel.
- This aligns with existing workflow fullscreen chrome-hide behavior.
