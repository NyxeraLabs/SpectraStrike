# UI Decisions

## Decision 1: Remove UI Demo Entry Point
- Demo-trigger button removed from login UI.
- Rationale: enforce CLI-seeded environment flows and prevent mixed mode initiation from UI.

## Decision 2: Keep First-Run Wizard as Configuration Surface
- Workflow first-run path now uses configuration messaging, not demo messaging.
- Rationale: align with Mode B semantics (DB-zero setup flow).

## Decision 3: Single Fullscreen Runtime Pattern
- Workflow and ASM both consume the same fullscreen controller hook.
- Rationale: identical UX behavior and reduced drift from duplicated fullscreen logic.

## Decision 4: Fullscreen Chrome Suppression by Shared CSS Contract
- Reuse `spectra-fullscreen-active` + `spectra-fullscreen-hide` contract.
- Rationale: avoid per-page fullscreen hacks and ensure no partial expansion.
