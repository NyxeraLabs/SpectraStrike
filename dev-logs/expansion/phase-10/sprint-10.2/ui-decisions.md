# UI Decisions

- No SpectraStrike UI rendering logic changed in this sprint.
- Decision: keep SpectraStrike as producer of demo federation truth and avoid dual seed-authority in web UI.
- Cross-platform parity is enforced by exporting runtime-seeded telemetry contract for VectorVue consumers.
- Workflow default campaign dropdown values now mirror VectorVue campaign naming (`OP_*_2026`) to avoid cross-platform label drift.
- Node-Link execution UX decision:
  - campaign selection is now the primary scope key for seeded graph retrieval, and each seeded campaign receives a dedicated graph (6 nodes / 5 edges / 6 queued tasks in latest seed run).
- Visual consistency decision:
  - ASM and Workflow canvases share dark-node styling for a consistent operator visual language across graph engines.
- Timeline UX parity decision:
  - ASM campaign timeline controls now mirror Workflow (`range` bar + `Load All` + `Unload`).

## 2026-03-05 Final Addendum
- Canvas visual policy:
  - Dark mode prioritizes deep-map contrast for prolonged operator sessions.
  - Light mode keeps graph readability with high-contrast node borders and softer shadows.
- Workflow and ASM remain visually synchronized by sharing the same node/map token set.
