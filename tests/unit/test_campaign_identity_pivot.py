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

"""Unit tests for campaign identity, escalation, and pivot chain modeling."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from pkg.orchestrator.campaign_engine import (
    CampaignConfiguration,
    CampaignEngine,
    CampaignStatus,
    CredentialMaterialType,
    ExecutionStatus,
    PrivilegeLevel,
)


def _config() -> CampaignConfiguration:
    now = datetime.now(UTC)
    return CampaignConfiguration(
        objective="identity pivot validation",
        target_scope=("host-a", "host-b", "host-c"),
        execution_window_start=now + timedelta(minutes=10),
        execution_window_end=now + timedelta(hours=1),
        max_parallel_steps=2,
    )


def _running_campaign(engine: CampaignEngine):
    campaign = engine.create_campaign(
        name="identity-pivot-campaign",
        created_by="alice",
        configuration=_config(),
    )
    engine.set_campaign_status(campaign_id=campaign.campaign_id, status=CampaignStatus.RUNNING)
    step = engine.add_campaign_step(
        campaign_id=campaign.campaign_id,
        step_order=1,
        name="credential replay",
        technique_id="T1078",
        asset_selector=("host-a", "host-b", "host-c"),
    )
    return campaign, step


def test_identity_credential_escalation_and_pivot_chain_reconstruction() -> None:
    engine = CampaignEngine()
    campaign, step = _running_campaign(engine)
    identity = engine.add_identity(
        campaign_id=campaign.campaign_id,
        principal="corp\\alice",
        source_asset_id="host-a",
        privilege_level=PrivilegeLevel.USER,
    )

    exec_a = engine.start_technique_execution(
        campaign_id=campaign.campaign_id,
        step_id=step.step_id,
        asset_id="host-a",
        correlation_group_id="pivot-1",
    )
    engine.record_credential_material(
        campaign_id=campaign.campaign_id,
        identity_id=identity.identity_id,
        material_type=CredentialMaterialType.HASH,
        material_ref="ntlm:8846f7eaee8fb117ad06bdd830b7586c",
        source_execution_id=exec_a.execution_id,
    )
    engine.record_privilege_escalation(
        campaign_id=campaign.campaign_id,
        identity_id=identity.identity_id,
        to_level=PrivilegeLevel.LOCAL_ADMIN,
        execution_id=exec_a.execution_id,
        asset_id="host-a",
    )
    engine.add_lateral_movement_edge(
        campaign_id=campaign.campaign_id,
        identity_id=identity.identity_id,
        source_asset_id="host-a",
        target_asset_id="host-b",
        execution_id=exec_a.execution_id,
    )
    engine.stop_technique_execution(
        execution_id=exec_a.execution_id,
        status=ExecutionStatus.SUCCEEDED,
    )

    exec_b = engine.start_technique_execution(
        campaign_id=campaign.campaign_id,
        step_id=step.step_id,
        asset_id="host-b",
        correlation_group_id="pivot-1",
    )
    engine.record_privilege_escalation(
        campaign_id=campaign.campaign_id,
        identity_id=identity.identity_id,
        to_level=PrivilegeLevel.DOMAIN_ADMIN,
        execution_id=exec_b.execution_id,
        asset_id="host-b",
    )
    engine.add_lateral_movement_edge(
        campaign_id=campaign.campaign_id,
        identity_id=identity.identity_id,
        source_asset_id="host-b",
        target_asset_id="host-c",
        execution_id=exec_b.execution_id,
    )
    engine.stop_technique_execution(
        execution_id=exec_b.execution_id,
        status=ExecutionStatus.SUCCEEDED,
    )

    credentials = engine.list_identity_credentials(
        campaign_id=campaign.campaign_id,
        identity_id=identity.identity_id,
    )
    escalations = engine.list_identity_escalations(
        campaign_id=campaign.campaign_id,
        identity_id=identity.identity_id,
    )
    chain = engine.reconstruct_pivot_chain(
        campaign_id=campaign.campaign_id,
        identity_id=identity.identity_id,
    )

    assert len(credentials) == 1
    assert credentials[0].material_type == CredentialMaterialType.HASH
    assert len(escalations) == 2
    assert escalations[0].to_level == PrivilegeLevel.LOCAL_ADMIN
    assert escalations[1].to_level == PrivilegeLevel.DOMAIN_ADMIN
    assert chain.asset_path == ("host-a", "host-b", "host-c")
    assert len(chain.edge_ids) == 2
