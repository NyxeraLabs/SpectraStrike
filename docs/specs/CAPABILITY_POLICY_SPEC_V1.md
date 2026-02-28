<!-- NYXERA_BRANDING_HEADER_START -->
<p align="center">
  <img src="https://docs.nyxera.cloud/assets/img/product-logo.png" alt="SpectraStrike" width="220" />
</p>

<p align="center">
  <a href="https://docs.nyxera.cloud">Docs</a> |
  <a href="https://spectrastrike.nyxera.cloud">SpectraStrike</a> |
  <a href="https://nexus.nyxera.cloud">Nexus</a> |
  <a href="https://nyxera.cloud">Nyxera Labs</a>
</p>
<!-- NYXERA_BRANDING_HEADER_END -->

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

<!-- NYXERA_BRANDING_FOOTER_START -->

---

<p align="center">
  <img src="https://docs.nyxera.cloud/assets/img/nyxera-logo.png" alt="Nyxera Labs" width="110" />
</p>

<p align="center">
  2026 SpectraStrike by Nyxera Labs. All rights reserved.
</p>

<p align="center">
  <a href="https://docs.nyxera.cloud">Docs</a> |
  <a href="https://spectrastrike.nyxera.cloud">SpectraStrike</a> |
  <a href="https://nexus.nyxera.cloud">Nexus</a> |
  <a href="https://nyxera.cloud">Nyxera Labs</a>
</p>
<!-- NYXERA_BRANDING_FOOTER_END -->
