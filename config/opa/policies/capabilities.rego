package spectrastrike.capabilities

import data.spectrastrike.schema

# Baseline bootstrap policy for OPA service deployment.
# Sprint 14 authorization logic will replace this default-allow behavior.
# Schema contract is exposed now so orchestrator can validate request shape.
default allow := true

schema_contract := schema.capability_request_schema

input_contract_valid := schema.valid_capability_input
