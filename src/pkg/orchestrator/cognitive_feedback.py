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

"""Cognitive feedback loop contracts for Phase 8 Sprint 31."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Protocol

from pkg.integration.vectorvue.models import ResponseEnvelope


@dataclass(slots=True, frozen=True)
class FeedbackAdjustment:
    """One policy-relevant adjustment received from VectorVue feedback."""

    tenant_id: str
    execution_fingerprint: str
    target_urn: str
    action: str
    confidence: float
    rationale: str
    attestation_measurement_hash: str
    control: str = "execution"
    ttl_seconds: int = 3600


@dataclass(slots=True, frozen=True)
class CognitiveLoopRunResult:
    """Summary of one cognitive feedback loop synchronization run."""

    graph_push_ok: bool
    feedback_items: int
    applied_adjustments: int


@dataclass(slots=True, frozen=True)
class DefensiveEffectivenessMetrics:
    """Aggregated defensive effectiveness KPIs for UI and reporting."""

    total_events: int
    blocked_events: int
    successful_events: int
    detection_rate: float
    prevention_rate: float
    feedback_coverage: float
    applied_adjustments: int


class VectorVueCognitiveClient(Protocol):
    """VectorVue client capability surface required by cognitive loop sync."""

    def send_execution_graph_metadata(
        self, graph: dict[str, Any]
    ) -> ResponseEnvelope:
        """Push execution graph metadata to VectorVue."""

    def fetch_feedback_adjustments(
        self, tenant_id: str, limit: int = 100
    ) -> ResponseEnvelope:
        """Fetch cognitive feedback adjustments from VectorVue."""


class FeedbackPolicyEngine:
    """In-memory policy binding for cognitive feedback adjustments."""

    def __init__(self) -> None:
        self._adjustments: dict[tuple[str, str], FeedbackAdjustment] = {}

    def apply_adjustments(self, adjustments: list[FeedbackAdjustment]) -> int:
        applied = 0
        for adjustment in adjustments:
            key = (adjustment.tenant_id, adjustment.target_urn)
            self._adjustments[key] = adjustment
            applied += 1
        return applied

    def policy_context(self, tenant_id: str, target_urn: str) -> dict[str, Any]:
        adjustment = self._adjustments.get((tenant_id, target_urn))
        if adjustment is None:
            return {"feedback_bound": False}
        return {
            "feedback_bound": True,
            "feedback_action": adjustment.action,
            "feedback_confidence": adjustment.confidence,
            "feedback_control": adjustment.control,
            "feedback_rationale": adjustment.rationale,
            "feedback_ttl_seconds": adjustment.ttl_seconds,
            "feedback_attestation_measurement_hash": adjustment.attestation_measurement_hash,
        }

    def evaluate_allow(self, tenant_id: str, target_urn: str, base_allow: bool) -> bool:
        """Evaluate allow decision with feedback-bound policy adjustments."""
        adjustment = self._adjustments.get((tenant_id, target_urn))
        if adjustment is None:
            return base_allow
        action = adjustment.action.strip().lower()
        if action == "deny":
            return False
        if action == "tighten" and adjustment.confidence >= 0.8:
            return False
        return base_allow


@dataclass(slots=True)
class CognitiveFeedbackLoopService:
    """Coordinates graph export, feedback sync, and policy binding."""

    client: VectorVueCognitiveClient
    policy_engine: FeedbackPolicyEngine

    def push_execution_graph_metadata(self, graph: dict[str, Any]) -> ResponseEnvelope:
        return self.client.send_execution_graph_metadata(graph)

    @staticmethod
    def _extract_execution_fingerprints(execution_graph: dict[str, Any]) -> set[str]:
        anchors: set[str] = set()
        root = str(execution_graph.get("execution_fingerprint", "")).strip().lower()
        if len(root) == 64:
            anchors.add(root)
        nodes = execution_graph.get("nodes", [])
        if isinstance(nodes, list):
            for node in nodes:
                if not isinstance(node, dict):
                    continue
                candidate = str(node.get("execution_fingerprint", "")).strip().lower()
                if len(candidate) == 64:
                    anchors.add(candidate)
        return anchors

    @staticmethod
    def _extract_attestation_hashes(execution_graph: dict[str, Any]) -> set[str]:
        anchors: set[str] = set()
        root = str(
            execution_graph.get("attestation_measurement_hash", "")
        ).strip().lower()
        if re.fullmatch(r"^[a-f0-9]{64}$", root):
            anchors.add(root)
        nodes = execution_graph.get("nodes", [])
        if isinstance(nodes, list):
            for node in nodes:
                if not isinstance(node, dict):
                    continue
                candidate = str(
                    node.get("attestation_measurement_hash", "")
                ).strip().lower()
                if re.fullmatch(r"^[a-f0-9]{64}$", candidate):
                    anchors.add(candidate)
        return anchors

    def sync_feedback_adjustments(
        self, tenant_id: str, limit: int = 100
    ) -> list[FeedbackAdjustment]:
        response = self.client.fetch_feedback_adjustments(tenant_id, limit=limit)
        if not response.verified:
            raise ValueError("unsigned_or_unverified_feedback_response")
        raw = response.data if isinstance(response.data, list) else []
        parsed: list[FeedbackAdjustment] = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            item_tenant_id = str(item.get("tenant_id", tenant_id)).strip()
            if item_tenant_id != tenant_id:
                continue
            execution_fingerprint = str(
                item.get("execution_fingerprint", "")
            ).strip().lower()
            if len(execution_fingerprint) != 64:
                continue
            item_timestamp = int(item.get("timestamp", 0))
            item_schema = str(item.get("schema_version", "")).strip()
            attestation_hash = str(
                item.get("attestation_measurement_hash", "")
            ).strip().lower()
            if (
                item_timestamp <= 0
                or not item_schema
                or not re.fullmatch(r"^[a-f0-9]{64}$", attestation_hash)
            ):
                continue
            parsed.append(
                FeedbackAdjustment(
                    tenant_id=item_tenant_id,
                    execution_fingerprint=execution_fingerprint,
                    target_urn=str(item.get("target_urn", "unknown")),
                    action=str(item.get("action", "observe")),
                    confidence=float(item.get("confidence", 0.0)),
                    rationale=str(item.get("rationale", "unspecified")),
                    attestation_measurement_hash=attestation_hash,
                    control=str(item.get("control", "execution")),
                    ttl_seconds=int(item.get("ttl_seconds", 3600)),
                )
            )
        return parsed

    def run_cognitive_loop(
        self,
        *,
        tenant_id: str,
        execution_graph: dict[str, Any],
        feedback_limit: int = 100,
    ) -> CognitiveLoopRunResult:
        graph_result = self.push_execution_graph_metadata(execution_graph)
        adjustments = self.sync_feedback_adjustments(tenant_id, limit=feedback_limit)
        anchors = self._extract_execution_fingerprints(execution_graph)
        attestation_anchors = self._extract_attestation_hashes(execution_graph)
        if anchors:
            adjustments = [
                item
                for item in adjustments
                if item.execution_fingerprint in anchors
            ]
        if attestation_anchors:
            adjustments = [
                item
                for item in adjustments
                if item.attestation_measurement_hash in attestation_anchors
            ]
        applied = self.policy_engine.apply_adjustments(adjustments)
        return CognitiveLoopRunResult(
            graph_push_ok=graph_result.ok,
            feedback_items=len(adjustments),
            applied_adjustments=applied,
        )

    @staticmethod
    def compute_defensive_effectiveness_metrics(
        events: list[dict[str, Any]],
        adjustments: list[FeedbackAdjustment],
    ) -> DefensiveEffectivenessMetrics:
        total = len(events)
        blocked = sum(1 for event in events if str(event.get("status")) == "blocked")
        success = sum(1 for event in events if str(event.get("status")) == "success")
        detected = sum(
            1 for event in events if bool(event.get("threat_detected", False))
        )
        detection_rate = detected / total if total else 0.0
        prevention_rate = blocked / total if total else 0.0
        feedback_coverage = (
            min(len(adjustments), total) / total if total else 0.0
        )
        return DefensiveEffectivenessMetrics(
            total_events=total,
            blocked_events=blocked,
            successful_events=success,
            detection_rate=round(detection_rate, 4),
            prevention_rate=round(prevention_rate, 4),
            feedback_coverage=round(feedback_coverage, 4),
            applied_adjustments=len(adjustments),
        )
