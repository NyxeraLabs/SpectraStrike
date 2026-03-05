# Technical Notes

- Contract schema version: `spectrastrike.demo.seed.v1`.
- Contract payload includes:
  - `tenant_id`
  - `events[]` with `request_id`, `event_uid`, `metadata_json` (envelope/signature/attestation/policy hashes)
  - `findings[]` with `finding_uid` and source linkage metadata.
- Export path resolution:
  - `SPECTRASTRIKE_VECTORVUE_SEED_EXPORT` env var override.
  - Default: sibling VectorVue repo `local_federation/seed/spectrastrike_seed_contract.json`.
- Deterministic IDs generated via UUIDv5 for reproducibility across repeated seeds.
- Campaign parity note:
  - Seed payload and workflow defaults now emit/use `OP_*_2026` campaign IDs to match VectorVue seeded campaign catalog.
