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
