# Copyright (c) 2026 NyxeraLabs
# Author: Jose Maria Micoli
# Licensed under BSL 1.1
# Change Date: 2033-02-22 -> Apache-2.0
#
# You may:
# Study
# Modify
# Use for internal security testing
#
# You may NOT:
# Offer as a commercial service
# Sell derived competing products

"""Unit tests for campaign architecture lifecycle and execution correlation."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from pkg.orchestrator.campaign_engine import (
    CampaignConfiguration,
    CampaignEngine,
    CampaignEngineError,
    CampaignStatus,
    ExecutionStatus,
    StepStatus,
)


def _config() -> CampaignConfiguration:
    now = datetime.now(UTC)
    return CampaignConfiguration(
        objective="validate segmented AD pivot path",
        target_scope=("host-01", "host-02"),
        execution_window_start=now + timedelta(minutes=5),
        execution_window_end=now + timedelta(hours=2),
        auto_start=False,
        max_parallel_steps=2,
        metadata={"playbook": "lateral-movement"},
    )


def test_campaign_lifecycle_with_schedule_and_status_tracking() -> None:
    engine = CampaignEngine()
    campaign = engine.create_campaign(
        name="Q1-AD-Lateral-Chain",
        created_by="alice",
        configuration=_config(),
    )
    assert campaign.status == CampaignStatus.DRAFT

    scheduled_for = datetime.now(UTC) + timedelta(minutes=30)
    scheduled = engine.schedule_campaign(
        campaign_id=campaign.campaign_id,
        scheduled_for=scheduled_for,
    )
    assert scheduled.status == CampaignStatus.SCHEDULED
    assert scheduled.scheduled_for == scheduled_for

    running = engine.set_campaign_status(
        campaign_id=campaign.campaign_id,
        status=CampaignStatus.RUNNING,
    )
    assert running.status == CampaignStatus.RUNNING
    assert running.started_at is not None

    completed = engine.set_campaign_status(
        campaign_id=campaign.campaign_id,
        status=CampaignStatus.COMPLETED,
    )
    assert completed.status == CampaignStatus.COMPLETED
    assert completed.completed_at is not None


def test_campaign_step_and_technique_execution_tracks_timestamps_and_failure_reason() -> None:
    engine = CampaignEngine()
    campaign = engine.create_campaign(
        name="Q1-Privilege-Escalation",
        created_by="alice",
        configuration=_config(),
    )
    engine.set_campaign_status(campaign_id=campaign.campaign_id, status=CampaignStatus.RUNNING)
    step = engine.add_campaign_step(
        campaign_id=campaign.campaign_id,
        step_order=1,
        name="token impersonation",
        technique_id="T1134.001",
        asset_selector=("host-01",),
        correlation_key="phase-1",
    )
    assert step.status == StepStatus.PENDING

    execution = engine.start_technique_execution(
        campaign_id=campaign.campaign_id,
        step_id=step.step_id,
        asset_id="host-01",
        correlation_group_id="corr-01",
    )
    assert execution.status == ExecutionStatus.RUNNING
    assert execution.started_at is not None

    failed = engine.stop_technique_execution(
        execution_id=execution.execution_id,
        status=ExecutionStatus.FAILED,
        failure_reason="blocked_by_edr",
    )
    assert failed.status == ExecutionStatus.FAILED
    assert failed.stopped_at is not None
    assert failed.failure_reason == "blocked_by_edr"


def test_cross_asset_execution_correlation() -> None:
    engine = CampaignEngine()
    campaign = engine.create_campaign(
        name="Q1-Cross-Asset-Chain",
        created_by="alice",
        configuration=_config(),
    )
    engine.set_campaign_status(campaign_id=campaign.campaign_id, status=CampaignStatus.RUNNING)
    step = engine.add_campaign_step(
        campaign_id=campaign.campaign_id,
        step_order=1,
        name="remote service execution",
        technique_id="T1021.002",
        asset_selector=("host-01", "host-02"),
    )

    first = engine.start_technique_execution(
        campaign_id=campaign.campaign_id,
        step_id=step.step_id,
        asset_id="host-01",
        correlation_group_id="corr-lateral-01",
    )
    second = engine.start_technique_execution(
        campaign_id=campaign.campaign_id,
        step_id=step.step_id,
        asset_id="host-02",
        correlation_group_id="corr-lateral-01",
    )
    engine.stop_technique_execution(
        execution_id=first.execution_id,
        status=ExecutionStatus.SUCCEEDED,
    )
    engine.stop_technique_execution(
        execution_id=second.execution_id,
        status=ExecutionStatus.SUCCEEDED,
    )

    correlation = engine.correlate_executions(correlation_group_id="corr-lateral-01")
    assert correlation.campaign_id == campaign.campaign_id
    assert set(correlation.asset_ids) == {"host-01", "host-02"}
    assert len(correlation.execution_ids) == 2


def test_invalid_status_transition_is_rejected() -> None:
    engine = CampaignEngine()
    campaign = engine.create_campaign(
        name="Q1-Invalid-Transition",
        created_by="alice",
        configuration=_config(),
    )
    with pytest.raises(CampaignEngineError, match="invalid campaign status transition"):
        engine.set_campaign_status(
            campaign_id=campaign.campaign_id,
            status=CampaignStatus.COMPLETED,
        )
