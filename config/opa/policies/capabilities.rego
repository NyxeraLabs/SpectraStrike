package spectrastrike.capabilities

import data.spectrastrike.schema

# Capability policies are deny-by-default and require full tuple matching:
# [operator_id] + [tenant_id] + [tool_sha256] + [target_urn]
default allow := false

schema_contract := schema.capability_request_schema

input_contract_valid := schema.valid_capability_input

capability_bindings := [
  {
    "operator_id": "operator-a",
    "tenant_id": "tenant-a",
    "tool_sha256": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "target_urn_prefix": "urn:target:ip:10.0.0.",
    "actions": ["execute", "scan"],
  },
  {
    "operator_id": "operator-b",
    "tenant_id": "tenant-b",
    "tool_sha256": "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
    "target_urn": "urn:target:ip:10.1.10.5",
    "actions": ["execute"],
  },
]

allow if {
  input_contract_valid
  some i
  binding := capability_bindings[i]
  binding.operator_id == input.operator_id
  binding.tenant_id == input.tenant_id
  binding.tool_sha256 == input.tool_sha256
  action_allowed(binding.actions, input.action)
  target_allowed(binding, input.target_urn)
}

action_allowed(actions, action) if {
  some i
  lower(actions[i]) == lower(action)
}

target_allowed(binding, target_urn) if {
  binding.target_urn == target_urn
}

target_allowed(binding, target_urn) if {
  startswith(target_urn, binding.target_urn_prefix)
}
