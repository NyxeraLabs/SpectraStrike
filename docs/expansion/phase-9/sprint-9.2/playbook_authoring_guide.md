# Playbook Authoring Guide - Phase 9 Sprint 9.2

## 1. Authoring Principles
- Model playbooks as deterministic graph paths (not ad hoc scripts).
- Use explicit ATT&CK technique references per step.
- Add branching conditions (`always`, `on_success`, `on_failure`) deliberately.
- Keep each step observable through telemetry-friendly labels and metadata.

## 2. Recommended Step Structure
- `step_id`
- `label`
- `technique_id`
- `node_type` (initial access, privilege escalation, lateral movement, c2, exfiltration)
- `preconditions`
- `expected_signal`
- `rollback_action`

## 3. Safety and Execution Controls
- Require approval gates for high-impact steps.
- Validate legal/policy acceptance before execution.
- Enforce tenant and role context for each run.
- Prefer idempotent step behavior for repeatable campaigns.

## 4. Quality Checks Before Promotion
1. Graph validates without orphan nodes.
2. Branch outcomes are deterministic under test.
3. Telemetry events are emitted for each major transition.
4. Rollback path exists for destructive phases.
5. Campaign to finding mapping is preserved for Nexus drill-down.

## 5. Versioning Guidance
- Use semantic versioning per playbook family.
- Capture execution behavior changes in changelog notes.
- Keep legacy versions available for historical replay/audit.
