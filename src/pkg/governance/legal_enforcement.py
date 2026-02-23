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

"""Local legal-governance enforcement for Python CLI surfaces."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DeploymentEnvironment = str

LEGAL_VERSIONS = {
    "eula": "2026.1",
    "aup": "2026.1",
    "privacy": "2026.1",
}


@dataclass(slots=True)
class LegalDecision:
    environment: DeploymentEnvironment
    is_compliant: bool
    reason: str | None = None


def detect_environment() -> DeploymentEnvironment:
    value = os.getenv("SPECTRASTRIKE_ENV", "self-hosted").strip()
    if value in {"self-hosted", "enterprise", "saas"}:
        return value
    return "self-hosted"


def _acceptance_path() -> Path:
    configured = os.getenv(
        "SPECTRASTRIKE_LEGAL_ACCEPTANCE_PATH", ".spectrastrike/legal/acceptance.json"
    )
    return Path(configured).expanduser().resolve()


def _required_docs(environment: DeploymentEnvironment) -> tuple[str, ...]:
    if environment == "saas":
        return ("eula", "aup", "privacy")
    if (
        environment == "enterprise"
        and os.getenv("SPECTRASTRIKE_ENTERPRISE_REQUIRE_PER_USER_ACCEPTANCE", "false")
        == "true"
    ):
        return ("eula", "aup", "privacy")
    return ("eula", "aup")


def _load_self_hosted_acceptance() -> dict[str, Any] | None:
    path = _acceptance_path()
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def evaluate_cli_legal_acceptance() -> LegalDecision:
    environment = detect_environment()
    if environment != "self-hosted":
        return LegalDecision(environment=environment, is_compliant=True)

    acceptance = _load_self_hosted_acceptance()
    if not acceptance:
        return LegalDecision(
            environment=environment,
            is_compliant=False,
            reason="LEGAL_ACCEPTANCE_REQUIRED: missing local acceptance.json",
        )

    accepted_documents = acceptance.get("accepted_documents", {})
    if not isinstance(accepted_documents, dict):
        return LegalDecision(
            environment=environment,
            is_compliant=False,
            reason="LEGAL_ACCEPTANCE_REQUIRED: malformed accepted_documents payload",
        )

    for doc in _required_docs(environment):
        expected = LEGAL_VERSIONS[doc]
        if accepted_documents.get(doc) != expected:
            return LegalDecision(
                environment=environment,
                is_compliant=False,
                reason=(
                    "LEGAL_ACCEPTANCE_REQUIRED: outdated or missing "
                    f"{doc} version (expected {expected})"
                ),
            )

    return LegalDecision(environment=environment, is_compliant=True)


def assert_cli_legal_acceptance() -> None:
    decision = evaluate_cli_legal_acceptance()
    if decision.is_compliant:
        return
    raise RuntimeError(decision.reason or "LEGAL_ACCEPTANCE_REQUIRED")
