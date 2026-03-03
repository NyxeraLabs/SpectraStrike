# Changes - Phase 8 Sprint 8.5

## File-by-file changes
- `SpectraStrike/ui/web/app/lib/global-ui.ts`
  - Added global UX contract for themes, role capabilities, keyboard shortcuts, accessibility checks, and render budgeting.

- `SpectraStrike/ui/web/app/components/global-ui-controls.tsx`
  - Added global feedback controls: role switch, theme toggle, health indicator, notifications, keyboard shortcuts, power mode, and workspace recovery.

- `SpectraStrike/ui/web/app/components/top-nav.tsx`
  - Integrated global UI controls into SpectraStrike navigation shell.

- `SpectraStrike/ui/web/app/dashboard/layout.tsx`
  - Added responsive shell wrapper class.

- `SpectraStrike/ui/web/app/globals.css`
  - Added design token expansion, light theme variables, focus visibility, and responsive shell utility.

- `SpectraStrike/ui/web/tests/unit/global-ui-accessibility-performance.test.ts`
  - Added WCAG-focused and rendering-budget benchmark validations.

- `VectorVue/portal/lib/global-ui.mjs`
  - Added portal global UX utility contract (theme, role policy, shortcuts, persistence helpers, accessibility checks).

- `VectorVue/portal/components/layout/topbar.tsx`
  - Integrated global controls for role/theme/health/notifications/shortcuts/power mode/workspace recovery.

- `VectorVue/portal/app/globals.css`
  - Added light theme variables, focus visibility, and responsive shell utility.

- `VectorVue/portal/tests/global-ui-accessibility-performance.test.mjs`
  - Added accessibility baseline and rendering benchmark tests for portal global UX utilities.

- `SpectraStrike/docs/ROADMAP_EXPANSION.md`
  - Marked Sprint 57 checklist completed.

## Reason for each change
- Fulfill Sprint 57 commitments for shared enterprise-grade UX maturity while preserving current architecture and navigation patterns.
