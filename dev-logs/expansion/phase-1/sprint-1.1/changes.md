# Phase 1 Sprint 1.1 Changes

## File-by-file change explanation

### `SpectraStrike/src/pkg/orchestrator/campaign_engine.py`
- Added `CampaignConfiguration` model and campaign lifecycle enums.
- Added `CampaignRecord` (campaign table), `CampaignStepRecord` (campaign step table), and `TechniqueExecutionRecord` (technique execution table).
- Added scheduling support via `schedule_campaign`.
- Added status tracking via `set_campaign_status` and transition validator.
- Added technique execution start/stop tracking with timestamps and failure reasons.
- Added cross-asset execution correlation index and `correlate_executions` output model.

### `SpectraStrike/src/pkg/orchestrator/__init__.py`
- Exported campaign engine models/services for package-level consumption.

### `SpectraStrike/tests/unit/test_campaign_engine.py`
- Added campaign lifecycle tests including schedule/status progression.
- Added step/execution lifecycle tests with failure reason and stop timestamp checks.
- Added cross-asset correlation validation tests.
- Added invalid lifecycle transition rejection test.

### `SpectraStrike/docs/expansion/phase-1/sprint-1.1/campaign_architecture.md`
- Added architecture reference for campaign/configuration/step/execution data model and lifecycle constraints.

### `SpectraStrike/docs/ROADMAP_EXPANSION.md`
- Marked Sprint 38 checklist items complete.

## Reason for each change
- Fulfill Sprint 38 campaign architecture deliverables end-to-end with typed domain models and tests.
