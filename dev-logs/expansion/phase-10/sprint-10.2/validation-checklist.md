# Validation Checklist

- [x] `scripts/seed_demo_runtime.py` compiles.
- [x] Demo-seed writes contract file for VectorVue ingestion.
- [x] Make target order ensures contract exists before VectorVue seed ingestion step.
- [x] Full end-to-end `make demo-seed` completed in running federation stack.
- [x] SpectraStrike UI build passes after campaign/default alignment changes.
- [ ] Live RabbitMQ bridge to VectorVue API still needs container-network endpoint fix (`127.0.0.1:443` from Spectra app container is unreachable).
