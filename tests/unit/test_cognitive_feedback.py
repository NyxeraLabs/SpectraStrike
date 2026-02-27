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

"""Unit tests for Sprint 31 cognitive feedback loop service."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pkg.integration.vectorvue.models import ResponseEnvelope
from pkg.orchestrator.cognitive_feedback import (
    CognitiveFeedbackLoopService,
    FeedbackAdjustment,
    FeedbackPolicyEngine,
)


@dataclass
class _FakeCognitiveClient:
    graph_ok: bool = True

    def send_execution_graph_metadata(self, graph: dict[str, Any]) -> ResponseEnvelope:
        assert graph["graph_id"] == "graph-1"
        return ResponseEnvelope(
            request_id="graph-req-1",
            status="accepted" if self.graph_ok else "failed",
            data={"received": True},
            errors=[] if self.graph_ok else [{"message": "failed"}],
            http_status=202 if self.graph_ok else 500,
        )

    def fetch_feedback_adjustments(
        self, tenant_id: str, limit: int = 100
    ) -> ResponseEnvelope:
        assert tenant_id == "tenant-a"
        assert limit == 10
        return ResponseEnvelope(
            request_id="feedback-req-1",
            status="accepted",
            data=[
                {
                    "tenant_id": "tenant-a",
                    "execution_fingerprint": "a" * 64,
                    "target_urn": "urn:target:ip:10.0.0.5",
                    "action": "tighten",
                    "confidence": 0.91,
                    "rationale": "repeated suspicious process injection",
                    "control": "execution",
                    "ttl_seconds": 1800,
                    "timestamp": 1760000000,
                    "schema_version": "feedback.adjustment.v1",
                }
            ],
            errors=[],
            verified=True,
            http_status=200,
        )


def test_run_cognitive_loop_pushes_syncs_and_applies() -> None:
    policy = FeedbackPolicyEngine()
    service = CognitiveFeedbackLoopService(
        client=_FakeCognitiveClient(),
        policy_engine=policy,
    )

    result = service.run_cognitive_loop(
        tenant_id="tenant-a",
        execution_graph={
            "graph_id": "graph-1",
            "tenant_id": "tenant-a",
            "nodes": [{"id": "n1", "type": "task"}],
            "edges": [],
        },
        feedback_limit=10,
    )

    assert result.graph_push_ok
    assert result.feedback_items == 1
    assert result.applied_adjustments == 1
    context = policy.policy_context("tenant-a", "urn:target:ip:10.0.0.5")
    assert context["feedback_bound"] is True
    assert context["feedback_action"] == "tighten"
    assert policy.evaluate_allow("tenant-a", "urn:target:ip:10.0.0.5", base_allow=True) is False


def test_compute_defensive_effectiveness_metrics() -> None:
    events = [
        {"status": "success", "threat_detected": True},
        {"status": "blocked", "threat_detected": True},
        {"status": "blocked", "threat_detected": False},
        {"status": "success", "threat_detected": False},
    ]
    adjustments = [
        FeedbackAdjustment(
            tenant_id="tenant-a",
            target_urn="urn:target:ip:10.0.0.5",
            action="tighten",
            confidence=0.9,
            rationale="risk cluster",
        )
    ]

    metrics = CognitiveFeedbackLoopService.compute_defensive_effectiveness_metrics(
        events=events,
        adjustments=adjustments,
    )

    assert metrics.total_events == 4
    assert metrics.blocked_events == 2
    assert metrics.successful_events == 2
    assert metrics.detection_rate == 0.5
    assert metrics.prevention_rate == 0.5
    assert metrics.feedback_coverage == 0.25


def test_rejects_unsigned_feedback_response() -> None:
    class _UnsignedClient(_FakeCognitiveClient):
        def fetch_feedback_adjustments(
            self, tenant_id: str, limit: int = 100
        ) -> ResponseEnvelope:
            response = super().fetch_feedback_adjustments(tenant_id, limit)
            response.verified = False
            return response

    service = CognitiveFeedbackLoopService(
        client=_UnsignedClient(),
        policy_engine=FeedbackPolicyEngine(),
    )
    try:
        service.sync_feedback_adjustments("tenant-a", limit=10)
        assert False, "expected unsigned feedback response to be rejected"
    except ValueError as exc:
        assert str(exc) == "unsigned_or_unverified_feedback_response"
