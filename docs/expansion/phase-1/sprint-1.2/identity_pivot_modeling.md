# Sprint 39: Identity and Pivot Modeling

## Data model extensions

### Identity entity model (`IdentityRecord`)
- `identity_id`
- `campaign_id`
- `principal`
- `source_asset_id`
- `privilege_level`
- `compromised`
- `compromised_at`
- `compromised_by_execution_id`

### Credential material tracking (`CredentialMaterialRecord`)
- `credential_id`
- `campaign_id`
- `identity_id`
- `material_type`
- `material_ref`
- `captured_at`
- `source_execution_id`

### Privilege escalation event (`PrivilegeEscalationRecord`)
- `escalation_id`
- `campaign_id`
- `identity_id`
- `from_level`
- `to_level`
- `execution_id`
- `asset_id`
- `occurred_at`

### Lateral movement edge (`LateralMovementEdge`)
- `edge_id`
- `campaign_id`
- `identity_id`
- `source_asset_id`
- `target_asset_id`
- `execution_id`
- `occurred_at`
- `relation`

### Pivot graph persistence projection (`PivotChain`)
- `campaign_id`
- `identity_id`
- `asset_path`
- `edge_ids`

## Execution behavior
- Identity records are campaign-scoped and unique by principal within campaign.
- Escalation events update compromised attribution and effective privilege level.
- Lateral movement edges are persisted per identity and linked to concrete technique executions.
- Pivot chain reconstruction replays ordered lateral edges to produce asset traversal path.

## Reconstruction guarantees
- Asset path is deterministic from sorted edge timestamps.
- Chain starts from identity source asset even when no edges exist.
- Credential/escalation histories are queryable per identity.
