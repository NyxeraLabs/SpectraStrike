# Changes

## Scope
Critical cross-platform seed parity fix: SpectraStrike demo-seed now exports deterministic federation seed artifacts consumed by VectorVue.

## Implemented
- Added contract export support in `scripts/seed_demo_runtime.py`:
  - Generates per-tenant seeded events/findings from actual seeded task submissions.
  - Writes contract JSON to `VectorVue/local_federation/seed/spectrastrike_seed_contract.json` by default.
- Updated `Makefile` `demo-seed` order:
  - Seed SpectraStrike runtime first.
  - Then trigger VectorVue seed so it can ingest SpectraStrike contract.

## Outcome
Demo seed produces cross-platform federation artifacts with tenant-scoped event/finding references suitable for VectorVue TUI and portal timeline parity.

## 2026-03-05 Addendum
- Unified campaign IDs with VectorVue canonical names:
  - `OP_ACME_REDWOLF_2026`
  - `OP_ACME_NIGHTGLASS_2026`
  - `OP_GLOBEX_REDWOLF_2026`
  - `OP_GLOBEX_NIGHTGLASS_2026`
- Updated SpectraStrike defaults in:
  - `scripts/seed_demo_runtime.py`
  - `ui/web/app/components/workflow-workbench.tsx`
  - `ui/web/app/api/execution/context/route.ts`
- Expanded contract findings generation from subset sampling to all seeded wrappers per tenant (24 findings total across 2 tenants in latest run).
