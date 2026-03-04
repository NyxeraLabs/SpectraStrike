# Validation Checklist

## Static Validation
- [x] Demo route file removed from UI tree.
- [x] Login UI no longer renders Demo Shell trigger.
- [x] Shared fullscreen controller file present and imported by workflow + ASM.
- [x] ASM page top chrome wrapped with `spectra-fullscreen-hide`.

## Runtime Validation
- [x] Workflow fullscreen toggle enters and exits fullscreen.
- [x] ASM fullscreen toggle enters and exits fullscreen.
- [x] ESC exits fullscreen (native API and fallback mode).
- [x] Body scroll is disabled during fullscreen.

## Regression Spot Checks
- [x] Workflow page still mounts and loads wrappers/playbook/queue data.
- [x] ASM page still mounts and renders graph canvas.
- [ ] Full end-to-end guided flow validation (deferred to next tranche).

## Incremental Runtime Hardening Validation
- [x] `workflow-workbench` no longer assumes queue/playbook array item object shape.
- [x] `asm-workbench` no longer assumes queue/telemetry array item object shape.
- [x] `telemetry-feed` no longer assumes wrappers/telemetry array item object shape.
- [x] `vitest`: `tests/unit/workflow-workbench.test.tsx` passes after patch.
- [x] `vitest`: `tests/unit/asm-large-graph-render.test.tsx` and `tests/unit/nexus-workbench.test.tsx` pass after patch.
- [ ] Browser-console verification on `/ui/dashboard/workflow` pending user-side confirmation (sandbox cannot launch Chromium here).

## Demo Reset Auth Validation
- [x] Static check: `reset_demo_runtime.py` no longer references `/v1/auth/demo`.
- [x] Static check: `seed_demo_runtime.py` auth resolver no longer references `/v1/auth/demo`.
- [x] Static check: both scripts handle legal-accept retry through `/v1/auth/legal/accept`.
- [x] Syntax validation: `python -m py_compile scripts/reset_demo_runtime.py scripts/seed_demo_runtime.py`.
- [ ] Runtime validation pending: re-run `make demo-reset` in your environment.
