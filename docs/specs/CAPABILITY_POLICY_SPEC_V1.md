<!--
Copyright (c) 2026 NyxeraLabs
Author: José María Micoli
Licensed under BSL 1.1
Change Date: 2033-02-22 -> Apache-2.0
-->

# Capability Policy Specification v1

Version: `1.0.0`
Status: Published (Sprint 33)

## 1. Purpose

Define the stable input contract used by SpectraStrike when delegating execution authorization to OPA.

## 2. Policy Input Contract

Required input fields:
- `operator_id` (string, non-empty)
- `tenant_id` (string, non-empty)
- `tool_sha256` (`sha256:<64 lowercase hex>`)
- `target_urn` (`urn:<nid>:<nss>`)
- `action` (string, non-empty)

Reference code path:
- `pkg.orchestrator.opa.OPAExecutionAuthorizer`
- `pkg.orchestrator.opa.OPAAAAPolicyAdapter`

## 3. Decision Endpoints

OPA queries:
- Input contract validation: `/v1/data/spectrastrike/capabilities/input_contract_valid`
- Allow decision: `/v1/data/spectrastrike/capabilities/allow`

Authorization sequence:
1. Validate input contract endpoint returns `result: true`.
2. Validate allow endpoint returns `result: true`.
3. Any false response MUST deny execution pre-sign.

## 4. Security Semantics

- Authorization is policy-driven, not hardcoded in business logic.
- Capability tuple combines identity and execution context.
- OPA transport/response failures MUST fail closed.

## 5. Compatibility Rules

- New optional fields MAY be added without breaking v1.
- Existing required field semantics MUST remain stable for major version `1`.
