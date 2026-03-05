# Validation Checklist

- [x] `scripts/seed_demo_runtime.py` compiles.
- [x] Demo-seed writes contract file for VectorVue ingestion.
- [x] Make target order ensures contract exists before VectorVue seed ingestion step.
- [x] Full end-to-end `make demo-seed` completed in running federation stack.
- [x] SpectraStrike UI build passes after campaign/default alignment changes.
- [x] Live RabbitMQ bridge no longer fails on endpoint routing (`vectorvue.local` + local federation network attachment).
- [x] Live RabbitMQ bridge queue bootstrap is idempotent (no `queue not found` failure path).
- [x] Campaign-scoped playbook retrieval validated:
  - ACME/Globex seeded campaigns each return populated Node-Link graphs.
- [x] ASM campaign timeline bar parity validated (`Load All`/`Unload` + range control).
- [x] UI quality gates pass:
  - `npm --prefix ui/web run test:unit`
  - `npm --prefix ui/web run build`
  - `npm --prefix ui/web run lint` (non-interactive CI-safe command)

## 2026-03-05 Final Addendum
- [x] `npm --prefix ui/web run build`
- [x] `npm --prefix ui/web run test:unit`
- [x] Workflow canvas dark/light map + node switch validated in build/test output.
- [x] ASM canvas dark/light map + node switch validated in build/test output.
