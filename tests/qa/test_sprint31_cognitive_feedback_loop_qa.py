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

"""Sprint 31 QA checks for cognitive feedback loop artifacts."""

from __future__ import annotations

from pathlib import Path

from pkg.integration.vectorvue.models import ResponseEnvelope
from pkg.orchestrator.cognitive_feedback import (
    CognitiveFeedbackLoopService,
    FeedbackPolicyEngine,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


class _QAClient:
    def send_execution_graph_metadata(self, graph: dict[str, object]) -> ResponseEnvelope:
        assert "nodes" in graph
        return ResponseEnvelope(
            request_id="qa-graph-1",
            status="accepted",
            data={"graph_synced": True},
            errors=[],
            http_status=202,
        )

    def fetch_feedback_adjustments(
        self, tenant_id: str, limit: int = 100
    ) -> ResponseEnvelope:
        del limit
        return ResponseEnvelope(
            request_id="qa-feedback-1",
            status="accepted",
            data=[
                {
                    "tenant_id": tenant_id,
                    "execution_fingerprint": "b" * 64,
                    "target_urn": "urn:target:ip:10.0.0.42",
                    "action": "deny",
                    "confidence": 0.97,
                    "rationale": "beacon behavior anomaly",
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


def test_roadmap_marks_sprint31_complete_except_commit() -> None:
    content = (REPO_ROOT / "docs/ROADMAP.md").read_text(encoding="utf-8")
    section_title = "## Sprint 31 (Week 59-60): Cognitive Feedback Loop"
    section_start = content.index(section_title)
    next_section = content.find("\n\n# Phase 9", section_start)
    section = content[section_start:next_section]

    required_checked = [
        "- [x] Push execution graph metadata to VectorVue",
        "- [x] Implement VectorVue → SpectraStrike feedback sync",
        "- [x] Bind feedback adjustments to policy engine",
        "- [x] Display defensive effectiveness metrics in UI",
        "- [x] Validate end-to-end cognitive loop",
    ]
    for line in required_checked:
        assert line in section
    assert "Commit Sprint 31 Cognitive Feedback Loop" in section


def test_sprint31_contracts_exist() -> None:
    content = (REPO_ROOT / "src/pkg/orchestrator/cognitive_feedback.py").read_text(
        encoding="utf-8"
    )
    required = [
        "class FeedbackAdjustment",
        "class FeedbackPolicyEngine",
        "class CognitiveFeedbackLoopService",
        "compute_defensive_effectiveness_metrics",
    ]
    for symbol in required:
        assert symbol in content


def test_sprint31_end_to_end_cognitive_loop_validation() -> None:
    policy = FeedbackPolicyEngine()
    service = CognitiveFeedbackLoopService(client=_QAClient(), policy_engine=policy)

    result = service.run_cognitive_loop(
        tenant_id="tenant-a",
        execution_graph={
            "graph_id": "qa-graph",
            "tenant_id": "tenant-a",
            "execution_fingerprint": "b" * 64,
            "nodes": [
                {"id": "n1", "type": "task", "execution_fingerprint": "b" * 64}
            ],
            "edges": [{"from": "n1", "to": "n1"}],
        },
    )

    assert result.graph_push_ok
    assert result.feedback_items == 1
    assert result.applied_adjustments == 1
    assert policy.evaluate_allow("tenant-a", "urn:target:ip:10.0.0.42", base_allow=True) is False
