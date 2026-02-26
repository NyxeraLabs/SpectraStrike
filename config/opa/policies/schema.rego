package spectrastrike.schema

# Standard operator capability request contract consumed by OPA policies.
capability_request_schema := {
  "required": [
    "operator_id",
    "tenant_id",
    "tool_sha256",
    "target_urn",
    "action",
  ],
  "patterns": {
    "tool_sha256": "^sha256:[0-9a-f]{64}$",
    "target_urn": "^urn:[a-z0-9][a-z0-9-]{0,31}:[^\\s]+$",
    "id": "^[A-Za-z0-9][A-Za-z0-9._:-]{2,127}$",
    "action": "^[a-z][a-z0-9_.:-]{2,63}$",
  },
}

required_fields := capability_request_schema.required

missing_fields[field] {
  some i
  field := required_fields[i]
  object.get(input, field, "") == ""
}

has_required_fields {
  count(missing_fields) == 0
}

has_valid_operator_id {
  regex.match(capability_request_schema.patterns.id, input.operator_id)
}

has_valid_tenant_id {
  regex.match(capability_request_schema.patterns.id, input.tenant_id)
}

has_valid_tool_sha256 {
  regex.match(capability_request_schema.patterns.tool_sha256, input.tool_sha256)
}

has_valid_target_urn {
  regex.match(capability_request_schema.patterns.target_urn, input.target_urn)
}

has_valid_action {
  regex.match(capability_request_schema.patterns.action, lower(input.action))
}

valid_capability_input {
  has_required_fields
  has_valid_operator_id
  has_valid_tenant_id
  has_valid_tool_sha256
  has_valid_target_urn
  has_valid_action
}
