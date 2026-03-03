# Phase 4 Sprint 4.1 Changes

## File-by-file change explanation

### `VectorVue/services/asm_asset_discovery.py`
- Added `AssetInventory` core table model.
- Added domain discovery module.
- Added subdomain brute-force module.
- Added IP range ingestion module.
- Added ASN lookup integration.
- Added certificate transparency ingestion.
- Added DNS record normalization.
- Added cloud metadata ingestion for AWS, Azure, and GCP.
- Added asset ownership tagging.
- Added asset criticality classification.
- Added deduplicating upsert semantics across ingestion sources.

### `VectorVue/tests/unit/test_phase4_sprint41_asset_discovery.py`
- Added asset deduplication validation test.
- Added DNS normalization regression test.
- Added cloud metadata ingestion + ASN + ownership/criticality test.

### `SpectraStrike/docs/expansion/phase-4/sprint-4.1/asset_discovery_engine.md`
- Added Sprint 44 design and behavior documentation.

### `SpectraStrike/docs/ROADMAP_EXPANSION.md`
- Marked Sprint 44 checklist items complete.

## Reason for each change
- Fulfill Sprint 44 requirements for ASM inventory foundations and source-normalized discovery ingestion.
