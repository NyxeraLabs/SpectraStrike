# Sprint 38: Campaign Architecture

## Domain model

### Campaign table (`CampaignRecord`)
- `campaign_id`
- `name`
- `created_by`
- `created_at`
- `configuration` (`CampaignConfiguration`)
- `status` (`CampaignStatus`)
- `scheduled_for`
- `started_at`
- `completed_at`
- `failure_reason`

### Campaign configuration model (`CampaignConfiguration`)
- `objective`
- `target_scope`
- `execution_window_start`
- `execution_window_end`
- `auto_start`
- `max_parallel_steps`
- `metadata`

### Campaign step table (`CampaignStepRecord`)
- `step_id`
- `campaign_id`
- `step_order`
- `name`
- `technique_id`
- `asset_selector`
- `status` (`StepStatus`)
- `correlation_key`

### Technique execution table (`TechniqueExecutionRecord`)
- `execution_id`
- `campaign_id`
- `step_id`
- `technique_id`
- `asset_id`
- `correlation_group_id`
- `status` (`ExecutionStatus`)
- `started_at`
- `stopped_at`
- `failure_reason`

## Lifecycle and scheduling
- Campaign lifecycle transitions are enforced by `ALLOWED_CAMPAIGN_STATUS_TRANSITIONS`.
- `schedule_campaign` moves draft campaigns to `scheduled` with a future timestamp.
- `set_campaign_status` enforces transition validity and sets lifecycle timestamps.

## Execution correlation
- `start_technique_execution` and `stop_technique_execution` persist execution lifecycle with start/stop timestamps.
- Cross-asset correlation index is maintained by `correlation_group_id`.
- `correlate_executions` returns grouped execution IDs and asset IDs for campaign-step correlation.

## Validation coverage
- Campaign lifecycle path (`draft -> scheduled -> running -> completed`).
- Step and technique execution lifecycle including failure reason tracking.
- Cross-asset execution correlation output.
- Invalid lifecycle transition rejection.
