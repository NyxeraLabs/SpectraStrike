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

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_opa_schema_defines_standard_capability_fields() -> None:
    schema_path = REPO_ROOT / "config/opa/policies/schema.rego"
    content = schema_path.read_text(encoding="utf-8")

    assert "package spectrastrike.schema" in content
    assert '"operator_id"' in content
    assert '"tenant_id"' in content
    assert '"tool_sha256"' in content
    assert '"target_urn"' in content
    assert '"action"' in content
    assert "valid_capability_input" in content


def test_capabilities_policy_wires_schema_contract() -> None:
    capabilities_path = REPO_ROOT / "config/opa/policies/capabilities.rego"
    content = capabilities_path.read_text(encoding="utf-8")

    assert "import data.spectrastrike.schema" in content
    assert "schema_contract :=" in content
    assert "input_contract_valid :=" in content
