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

## Decision 5: Workflow Picker Becomes Queryable + Filterable
- Added text search, category filter, and collapsible category sections.
- Rationale: reduce picker density and improve wrapper discoverability at scale.

## Decision 6: ASM Picker Uses Domain-Oriented Categories
- Category taxonomy aligned to requested ASM domains/surfaces/exposure/integration structure.
- Rationale: support graph construction from clean empty state with predictable asset grouping.

## Decision 7: Remove Demo-Query UX from Nexus
- Removed web UI demo-step panel and query-triggered alternate branch.
- Rationale: avoid overlap between seeded guided flows and first-run configuration paths.

## Decision 8: Fail-Closed on Malformed UI API Arrays
- Workflow/ASM/Telemetry render paths now ignore malformed/null array items rather than assuming object shape.
- Rationale: prevent route-level client exceptions from partial/legacy backend payloads and preserve page availability.

## Decision 9: Remove Dead Spotlight Styling Branches
- Workflow panel spotlight class checks removed where no spotlight state exists.
- Rationale: eliminate stale conditional code and keep route compile/runtime behavior deterministic.

## Decision 10: Runtime Scripts Must Not Depend on Removed UI Demo Auth
- Demo seed/reset scripts now authenticate using bootstrap login route only.
- Rationale: Part 1 removed UI demo route/buttons; runtime operations must follow the same contract.

## Decision 11: Failures Should Be Endpoint-Diagnostic
- Reset auth failures now return candidate-by-candidate endpoint results.
- Rationale: avoid misleading "last attempted endpoint" errors and reduce triage time when a service is down.

## Decision 12: Campaign Selection Is Explicit in Workflow UI
- Added explicit campaign selector for seeded multi-tenant context switching.
- Rationale: prevent hidden tenant context and allow deterministic ACME/Globex graph editing in seeded mode.

## Decision 13: Seed Commands Must Emit Operator Login Credentials
- `make demo-seed` now prints SpectraStrike login credentials directly.
- Rationale: match VectorVue credential visibility and reduce onboarding friction.

## Decision 14: Timeline Visibility Must Be Operator-Controlled
- Added explicit load/unload controls for campaign timeline steps in workflow UI.
- Rationale: allow fast narrowing or full expansion of campaign timeline without mutating the underlying graph.

## Decision 15: Tenant Selection and Campaign Selection Are Separate Controls
- Workflow now separates tenant scope from campaign selection.
- Rationale: one tenant can own many campaigns; campaign selection must be contextual to selected tenant.

## Decision 16: Tenant Visibility Is Role-Scoped
- Context route returns one/many/all tenants based on assigned roles and configured role-to-tenant mapping.
- Rationale: align SpectraStrike UX with permission-based tenant visibility expected in VectorVue.
