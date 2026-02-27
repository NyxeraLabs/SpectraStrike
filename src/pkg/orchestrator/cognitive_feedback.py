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

from dataclasses import dataclass, field
from typing import Any, Protocol

from pkg.integration.vectorvue.models import ResponseEnvelope


@dataclass(slots=True, frozen=True)
class FeedbackAdjustment:
    """One policy-relevant adjustment received from VectorVue feedback."""

    tenant_id: str
    target_urn: str
    action: str
    confidence: float
    rationale: str
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

    def sync_feedback_adjustments(
        self, tenant_id: str, limit: int = 100
    ) -> list[FeedbackAdjustment]:
        response = self.client.fetch_feedback_adjustments(tenant_id, limit=limit)
        raw = response.data if isinstance(response.data, list) else []
        parsed: list[FeedbackAdjustment] = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            parsed.append(
                FeedbackAdjustment(
                    tenant_id=str(item.get("tenant_id", tenant_id)),
                    target_urn=str(item.get("target_urn", "unknown")),
                    action=str(item.get("action", "observe")),
                    confidence=float(item.get("confidence", 0.0)),
                    rationale=str(item.get("rationale", "unspecified")),
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
