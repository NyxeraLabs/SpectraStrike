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

"""Adversary graph modeling and reconstruction engine (Phase 5 Sprint 5.2)."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import UTC, datetime
from threading import Lock
from typing import Any
from uuid import uuid4

from .campaign_engine import CampaignEngine


class AdversaryGraphError(ValueError):
    """Raised when graph modeling operations fail."""


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


@dataclass(slots=True, frozen=True)
class TechniqueLinkRecord:
    """TechniqueLink edge table row."""

    technique_link_id: str
    campaign_id: str
    source_technique_id: str
    target_technique_id: str
    relation: str
    weight: float
    created_at: datetime


@dataclass(slots=True, frozen=True)
class AttackPathRecord:
    """AttackPath table row."""

    attack_path_id: str
    campaign_id: str
    path_type: str
    node_path: tuple[str, ...]
    edge_path: tuple[str, ...]
    risk_score: float
    created_at: datetime
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class IdentityCompromiseChain:
    """Identity compromise chain model."""

    campaign_id: str
    identity_id: str
    principal: str
    source_asset_id: str
    compromised: bool
    credential_material_refs: tuple[str, ...]
    privilege_levels: tuple[str, ...]
    pivot_assets: tuple[str, ...]
    escalation_execution_ids: tuple[str, ...]


@dataclass(slots=True, frozen=True)
class CampaignGraphReconstruction:
    """Full campaign graph reconstruction output."""

    campaign_id: str
    attack_paths: tuple[AttackPathRecord, ...]
    technique_links: tuple[TechniqueLinkRecord, ...]
    identity_chains: tuple[IdentityCompromiseChain, ...]
    generated_at: datetime


class AdversaryGraphEngine:
    """Thread-safe graph engine for campaign reconstruction and traversal."""

    def __init__(self) -> None:
        self._attack_path_table: dict[str, AttackPathRecord] = {}
        self._technique_link_table: dict[str, TechniqueLinkRecord] = {}
        self._lock = Lock()

    def add_technique_link(
        self,
        *,
        campaign_id: str,
        source_technique_id: str,
        target_technique_id: str,
        relation: str = "sequence",
        weight: float = 1.0,
    ) -> TechniqueLinkRecord:
        if not source_technique_id.strip() or not target_technique_id.strip():
            raise AdversaryGraphError("source_technique_id and target_technique_id are required")
        row = TechniqueLinkRecord(
            technique_link_id=f"tlnk-{uuid4()}",
            campaign_id=campaign_id,
            source_technique_id=source_technique_id.strip().upper(),
            target_technique_id=target_technique_id.strip().upper(),
            relation=relation.strip() or "sequence",
            weight=_clamp(float(weight), 0.0, 1.0),
            created_at=datetime.now(UTC),
        )
        with self._lock:
            key = f"{campaign_id}|{row.source_technique_id}|{row.target_technique_id}|{row.relation}"
            existing = self._technique_link_table.get(key)
            if existing is not None:
                return existing
            self._technique_link_table[key] = row
        return row

    def add_attack_path(
        self,
        *,
        campaign_id: str,
        path_type: str,
        node_path: tuple[str, ...],
        edge_path: tuple[str, ...] = tuple(),
        risk_score: float,
        metadata: dict[str, Any] | None = None,
    ) -> AttackPathRecord:
        if not node_path:
            raise AdversaryGraphError("node_path is required")
        row = AttackPathRecord(
            attack_path_id=f"apth-{uuid4()}",
            campaign_id=campaign_id,
            path_type=path_type.strip() or "generic",
            node_path=node_path,
            edge_path=edge_path,
            risk_score=_clamp(float(risk_score), 0.0, 1.0),
            created_at=datetime.now(UTC),
            metadata=dict(metadata or {}),
        )
        with self._lock:
            self._attack_path_table[row.attack_path_id] = row
        return row

    def traverse_lateral_paths(
        self,
        *,
        campaign_id: str,
        lateral_edges: list[tuple[str, str, str]],
        start_asset_id: str,
        target_asset_id: str,
        max_depth: int = 6,
    ) -> list[AttackPathRecord]:
        if max_depth < 1:
            raise AdversaryGraphError("max_depth must be >= 1")
        adjacency: dict[str, list[tuple[str, str]]] = defaultdict(list)
        for edge_id, src, dst in lateral_edges:
            adjacency[src].append((edge_id, dst))

        queue: deque[tuple[str, tuple[str, ...], tuple[str, ...]]] = deque(
            [(start_asset_id, (start_asset_id,), tuple())]
        )
        found: list[AttackPathRecord] = []
        while queue:
            current, nodes, edges = queue.popleft()
            if len(nodes) > max_depth + 1:
                continue
            if current == target_asset_id:
                risk = _clamp((len(nodes) - 1) * 0.18, 0.05, 1.0)
                found.append(
                    self.add_attack_path(
                        campaign_id=campaign_id,
                        path_type="lateral_movement",
                        node_path=nodes,
                        edge_path=edges,
                        risk_score=risk,
                        metadata={"start_asset_id": start_asset_id, "target_asset_id": target_asset_id},
                    )
                )
                continue
            for edge_id, nxt in adjacency.get(current, []):
                if nxt in nodes:
                    continue
                queue.append((nxt, nodes + (nxt,), edges + (edge_id,)))
        return found

    def model_privilege_escalation_paths(
        self,
        *,
        campaign_id: str,
        identity_id: str,
        escalation_levels: list[str],
        escalation_execution_ids: list[str],
    ) -> AttackPathRecord:
        if not escalation_levels:
            raise AdversaryGraphError("escalation_levels cannot be empty")
        unique_levels: list[str] = []
        for level in escalation_levels:
            token = level.strip().lower()
            if token and (not unique_levels or unique_levels[-1] != token):
                unique_levels.append(token)
        risk = _clamp(0.15 + len(unique_levels) * 0.2, 0.0, 1.0)
        return self.add_attack_path(
            campaign_id=campaign_id,
            path_type="privilege_escalation",
            node_path=tuple(unique_levels),
            edge_path=tuple(escalation_execution_ids),
            risk_score=risk,
            metadata={"identity_id": identity_id},
        )

    def model_identity_compromise_chain(
        self,
        *,
        campaign_id: str,
        identity_id: str,
        principal: str,
        source_asset_id: str,
        compromised: bool,
        credential_material_refs: list[str],
        privilege_levels: list[str],
        pivot_assets: list[str],
        escalation_execution_ids: list[str],
    ) -> IdentityCompromiseChain:
        return IdentityCompromiseChain(
            campaign_id=campaign_id,
            identity_id=identity_id,
            principal=principal,
            source_asset_id=source_asset_id,
            compromised=compromised,
            credential_material_refs=tuple(credential_material_refs),
            privilege_levels=tuple(privilege_levels),
            pivot_assets=tuple(pivot_assets),
            escalation_execution_ids=tuple(escalation_execution_ids),
        )

    def reconstruct_campaign_graph(
        self,
        *,
        campaign_engine: CampaignEngine,
        campaign_id: str,
    ) -> CampaignGraphReconstruction:
        steps = campaign_engine.list_campaign_steps(campaign_id=campaign_id)
        executions = campaign_engine.list_campaign_executions(campaign_id=campaign_id)
        identities = campaign_engine.list_campaign_identities(campaign_id=campaign_id)
        lateral = campaign_engine.list_lateral_movement_edges(campaign_id=campaign_id)
        escalations = campaign_engine.list_campaign_escalations(campaign_id=campaign_id)

        step_technique: dict[str, str] = {step.step_id: step.technique_id for step in steps}
        ordered_exec = sorted(executions, key=lambda row: row.started_at)
        for prev, nxt in zip(ordered_exec, ordered_exec[1:]):
            src = step_technique.get(prev.step_id, prev.technique_id)
            dst = step_technique.get(nxt.step_id, nxt.technique_id)
            self.add_technique_link(
                campaign_id=campaign_id,
                source_technique_id=src,
                target_technique_id=dst,
                relation="sequence",
                weight=0.8,
            )

        identity_chains: list[IdentityCompromiseChain] = []
        for identity in identities:
            creds = campaign_engine.list_identity_credentials(
                campaign_id=campaign_id,
                identity_id=identity.identity_id,
            )
            id_escalations = [
                row for row in escalations if row.identity_id == identity.identity_id
            ]
            id_edges = [
                row for row in lateral if row.identity_id == identity.identity_id
            ]
            pivot = campaign_engine.reconstruct_pivot_chain(
                campaign_id=campaign_id,
                identity_id=identity.identity_id,
            )
            levels = [identity.privilege_level.value]
            levels.extend(row.to_level.value for row in id_escalations)
            if id_escalations:
                self.model_privilege_escalation_paths(
                    campaign_id=campaign_id,
                    identity_id=identity.identity_id,
                    escalation_levels=levels,
                    escalation_execution_ids=[row.execution_id for row in id_escalations],
                )

            for edge in id_edges:
                self.add_technique_link(
                    campaign_id=campaign_id,
                    source_technique_id="T1021",
                    target_technique_id="T1021",
                    relation="lateral_transition",
                    weight=0.7,
                )

            chain = self.model_identity_compromise_chain(
                campaign_id=campaign_id,
                identity_id=identity.identity_id,
                principal=identity.principal,
                source_asset_id=identity.source_asset_id,
                compromised=identity.compromised,
                credential_material_refs=[row.material_ref for row in creds],
                privilege_levels=levels,
                pivot_assets=list(pivot.asset_path),
                escalation_execution_ids=[row.execution_id for row in id_escalations],
            )
            identity_chains.append(chain)

            if len(pivot.asset_path) > 1:
                self.add_attack_path(
                    campaign_id=campaign_id,
                    path_type="identity_pivot",
                    node_path=pivot.asset_path,
                    edge_path=pivot.edge_ids,
                    risk_score=_clamp(0.20 + (len(pivot.asset_path) - 1) * 0.16, 0.0, 1.0),
                    metadata={"identity_id": identity.identity_id},
                )

        # Build lateral paths across all edges from first to last known node.
        if lateral:
            edges_simple = [
                (row.edge_id, row.source_asset_id, row.target_asset_id)
                for row in lateral
            ]
            first = edges_simple[0][1]
            last = edges_simple[-1][2]
            self.traverse_lateral_paths(
                campaign_id=campaign_id,
                lateral_edges=edges_simple,
                start_asset_id=first,
                target_asset_id=last,
                max_depth=8,
            )

        attack_paths = tuple(
            sorted(
                [row for row in self._attack_path_table.values() if row.campaign_id == campaign_id],
                key=lambda row: row.created_at,
            )
        )
        technique_links = tuple(
            sorted(
                [row for row in self._technique_link_table.values() if row.campaign_id == campaign_id],
                key=lambda row: row.created_at,
            )
        )
        return CampaignGraphReconstruction(
            campaign_id=campaign_id,
            attack_paths=attack_paths,
            technique_links=technique_links,
            identity_chains=tuple(identity_chains),
            generated_at=datetime.now(UTC),
        )

