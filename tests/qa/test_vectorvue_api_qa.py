# Copyright (c) 2026 NyxeraLabs
# Author: José María Micoli
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

"""Sprint 5 QA tests for live VectorVue endpoint validation hooks."""

from __future__ import annotations

import os

import pytest

from pkg.integration.vectorvue.config import VectorVueConfig
from pkg.integration.vectorvue.qa_smoke import run_smoke


def _live_config() -> VectorVueConfig:
    return VectorVueConfig(
        base_url=os.getenv("VECTORVUE_BASE_URL", "https://127.0.0.1"),
        username=os.getenv("VECTORVUE_USERNAME", "acme_viewer"),
        password=os.getenv("VECTORVUE_PASSWORD", "AcmeView3r!"),
        tenant_id=os.getenv("VECTORVUE_TENANT_ID", "10000000-0000-0000-0000-000000000001"),
        timeout_seconds=float(os.getenv("VECTORVUE_TIMEOUT_SECONDS", "5")),
        verify_tls=os.getenv("VECTORVUE_VERIFY_TLS", "0") == "1",
        max_retries=1,
        backoff_seconds=0,
    )


def test_qa_tls_configuration_defaults_secure() -> None:
    cfg = _live_config()
    assert cfg.base_url.startswith("https://")
    assert cfg.require_https is True


@pytest.mark.skipif(
    os.getenv("VECTORVUE_QA_LIVE", "0") != "1",
    reason="set VECTORVUE_QA_LIVE=1 to run live Sprint 5 QA checks",
)
def test_qa_live_endpoint_encrypted_and_telemetry_delivery() -> None:
    result = run_smoke(_live_config())
    assert result.login_ok is True
    assert result.event_status in {"accepted", "replayed"}
    assert result.finding_status in {"accepted", "replayed"}
    assert result.status_poll_status in {"accepted", "partial"}
