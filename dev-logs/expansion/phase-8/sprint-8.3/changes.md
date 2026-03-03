# Changes - Phase 8 Sprint 8.3

## File-by-file changes
- `VectorVue/portal/app/(portal)/portal/analytics/page.tsx`
  - Rebuilt analytics page into full telemetry intelligence dashboard with nine UI sections aligned to Sprint 55 commits.

- `VectorVue/portal/lib/intelligence-metrics.mjs`
  - Added deterministic transformation utilities for ATT&CK heatmap, confidence scoring, latency timeline, false-negative analytics, control matrix, SOC metrics, completeness, anomalies, evidence lifecycle, and render slicing.

- `VectorVue/portal/lib/intelligence-metrics.d.ts`
  - Added TypeScript declarations for JS analytics module imports.

- `VectorVue/portal/tests/telemetry-to-heatmap-integrity.test.mjs`
  - Added unit test validating bounded and stable telemetry-to-heatmap mapping.

- `VectorVue/portal/tests/dashboard-rendering-performance.test.mjs`
  - Added unit test validating large-dataset rendering preparation path and execution speed.

- `VectorVue/portal/package.json`
  - Added `test:unit` script using `node --test`.

- `SpectraStrike/docs/ROADMAP_EXPANSION.md`
  - Marked Sprint 55 checklist items as completed.

## Reason for each change
- Fulfill all Sprint 55 VectorVue UI and test commitments while preserving existing portal structure and minimizing new dependencies.
