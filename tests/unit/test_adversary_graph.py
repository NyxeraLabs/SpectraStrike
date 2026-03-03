# Copyright (c) 2026 NyxeraLabs
# Licensed under BSL 1.1
# Change Date: 2033-02-22 -> Apache-2.0

"""Unit tests for adversary graph modeling and campaign reconstruction."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from pkg.orchestrator.adversary_graph import AdversaryGraphEngine
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
        objective="graph reconstruction validation",
        target_scope=("host-a", "host-b", "host-c"),
        execution_window_start=now + timedelta(minutes=1),
        execution_window_end=now + timedelta(hours=1),
        max_parallel_steps=2,
    )


def _seed_campaign() -> tuple[CampaignEngine, str]:
    engine = CampaignEngine()
    campaign = engine.create_campaign(
        name="adversary-graph-campaign",
        created_by="alice",
        configuration=_config(),
    )
    engine.set_campaign_status(campaign_id=campaign.campaign_id, status=CampaignStatus.RUNNING)
    step1 = engine.add_campaign_step(
        campaign_id=campaign.campaign_id,
        step_order=1,
        name="initial-valid-account",
        technique_id="T1078",
        asset_selector=("host-a",),
    )
    step2 = engine.add_campaign_step(
        campaign_id=campaign.campaign_id,
        step_order=2,
        name="lateral-service",
        technique_id="T1021.002",
        asset_selector=("host-b", "host-c"),
    )

    identity = engine.add_identity(
        campaign_id=campaign.campaign_id,
        principal="corp\\alice",
        source_asset_id="host-a",
        privilege_level=PrivilegeLevel.USER,
    )

    exec1 = engine.start_technique_execution(
        campaign_id=campaign.campaign_id,
        step_id=step1.step_id,
        asset_id="host-a",
        correlation_group_id="grp-1",
    )
    engine.record_credential_material(
        campaign_id=campaign.campaign_id,
        identity_id=identity.identity_id,
        material_type=CredentialMaterialType.HASH,
        material_ref="ntlm:11223344556677889900aabbccddeeff",
        source_execution_id=exec1.execution_id,
    )
    engine.record_privilege_escalation(
        campaign_id=campaign.campaign_id,
        identity_id=identity.identity_id,
        to_level=PrivilegeLevel.LOCAL_ADMIN,
        execution_id=exec1.execution_id,
        asset_id="host-a",
    )
    engine.add_lateral_movement_edge(
        campaign_id=campaign.campaign_id,
        identity_id=identity.identity_id,
        source_asset_id="host-a",
        target_asset_id="host-b",
        execution_id=exec1.execution_id,
    )
    engine.stop_technique_execution(execution_id=exec1.execution_id, status=ExecutionStatus.SUCCEEDED)

    exec2 = engine.start_technique_execution(
        campaign_id=campaign.campaign_id,
        step_id=step2.step_id,
        asset_id="host-b",
        correlation_group_id="grp-1",
    )
    engine.record_privilege_escalation(
        campaign_id=campaign.campaign_id,
        identity_id=identity.identity_id,
        to_level=PrivilegeLevel.DOMAIN_ADMIN,
        execution_id=exec2.execution_id,
        asset_id="host-b",
    )
    engine.add_lateral_movement_edge(
        campaign_id=campaign.campaign_id,
        identity_id=identity.identity_id,
        source_asset_id="host-b",
        target_asset_id="host-c",
        execution_id=exec2.execution_id,
    )
    engine.stop_technique_execution(execution_id=exec2.execution_id, status=ExecutionStatus.SUCCEEDED)
    return engine, campaign.campaign_id


def test_graph_reconstruction_validation() -> None:
    campaign_engine, campaign_id = _seed_campaign()
    graph = AdversaryGraphEngine()

    reconstructed = graph.reconstruct_campaign_graph(
        campaign_engine=campaign_engine,
        campaign_id=campaign_id,
    )
    assert reconstructed.campaign_id == campaign_id
    assert len(reconstructed.identity_chains) == 1
    assert len(reconstructed.technique_links) >= 1
    assert len(reconstructed.attack_paths) >= 2

    identity_chain = reconstructed.identity_chains[0]
    assert identity_chain.compromised is True
    assert identity_chain.pivot_assets == ("host-a", "host-b", "host-c")
    assert "local_admin" in identity_chain.privilege_levels
    assert "domain_admin" in identity_chain.privilege_levels

    lateral_paths = [row for row in reconstructed.attack_paths if row.path_type == "lateral_movement"]
    assert len(lateral_paths) >= 1
    assert lateral_paths[0].node_path[0] == "host-a"
    assert lateral_paths[0].node_path[-1] == "host-c"


def test_graph_traversal_engine_finds_path() -> None:
    graph = AdversaryGraphEngine()
    paths = graph.traverse_lateral_paths(
        campaign_id="cmp-x",
        lateral_edges=[
            ("e1", "a", "b"),
            ("e2", "b", "c"),
            ("e3", "a", "d"),
        ],
        start_asset_id="a",
        target_asset_id="c",
        max_depth=4,
    )
    assert len(paths) == 1
    assert paths[0].node_path == ("a", "b", "c")
