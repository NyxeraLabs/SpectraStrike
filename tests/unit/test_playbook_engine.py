# Copyright (c) 2026 NyxeraLabs
# Licensed under BSL 1.1
# Change Date: 2033-02-22 -> Apache-2.0

"""Unit tests for playbook framework and complex simulation behavior."""

from __future__ import annotations

import pytest

from pkg.orchestrator.playbook_engine import (
    PlaybookEngine,
    PlaybookEngineError,
    StepExecutionStatus,
)


def test_playbook_tables_and_step_ordering() -> None:
    engine = PlaybookEngine()
    playbook = engine.create_playbook(
        name="External Edge Validation",
        description="Validate external exposure chain",
        created_by="alice",
        default_variables={"target_host": "edge-01", "operator": "alice"},
    )
    module = engine.register_technique_module(
        name="RDP Probe",
        technique_id="T1133",
        default_command_template="rdp_probe --target {target_host}",
    )
    engine.add_playbook_step(
        playbook_id=playbook.playbook_id,
        step_order=1,
        name="probe-edge",
        technique_module_id=module.technique_module_id,
    )
    with pytest.raises(PlaybookEngineError, match="duplicate step_order"):
        engine.add_playbook_step(
            playbook_id=playbook.playbook_id,
            step_order=1,
            name="probe-edge-duplicate",
            technique_module_id=module.technique_module_id,
        )


def test_complex_multistep_simulation_with_variable_injection_and_rollback() -> None:
    engine = PlaybookEngine()
    playbook = engine.create_playbook(
        name="Credential Abuse Chain",
        description="Complex branch/rollback simulation",
        created_by="alice",
        default_variables={"target_host": "dc-01", "domain": "corp.local", "operator": "alice"},
    )
    wrapper = engine.register_wrapper_template(
        name="sliver-shell",
        command_template="sliver exec --target {target_host} --cmd \"{payload}\"",
        rollback_template="sliver exec --target {target_host} --cmd \"{payload}\"",
    )
    access_mod = engine.register_technique_module(
        name="Valid Account Access",
        technique_id="T1078",
        default_command_template="auth_check --domain {domain} --user svc-{operator}",
        default_rollback_template="auth_revoke --domain {domain} --user svc-{operator}",
    )
    lateral_mod = engine.register_technique_module(
        name="SMB Lateral Move",
        technique_id="T1021.002",
        default_command_template="smb_exec --target {target_host} --op move",
        default_rollback_template="smb_cleanup --target {target_host}",
    )

    first = engine.add_playbook_step(
        playbook_id=playbook.playbook_id,
        step_order=1,
        name="initial-access",
        technique_module_id=access_mod.technique_module_id,
        wrapper_template_id=wrapper.wrapper_template_id,
    )
    second = engine.add_playbook_step(
        playbook_id=playbook.playbook_id,
        step_order=2,
        name="lateral",
        technique_module_id=lateral_mod.technique_module_id,
        wrapper_template_id=wrapper.wrapper_template_id,
        condition_expression="target_host == 'dc-01' and operator == 'alice'",
    )
    engine.add_playbook_step(
        playbook_id=playbook.playbook_id,
        step_order=3,
        name="collect",
        technique_module_id=lateral_mod.technique_module_id,
        command_template="collect_loot --target {target_host}",
        rollback_template="cleanup_loot --target {target_host}",
        wrapper_template_id=wrapper.wrapper_template_id,
    )

    result = engine.simulate_playbook(
        playbook_id=playbook.playbook_id,
        runtime_variables={"operator": "alice", "target_host": "dc-01"},
        fail_step_ids={second.step_id},
    )
    assert result.status == StepExecutionStatus.FAILED
    assert len(result.step_results) == 2
    assert result.step_results[0].status == StepExecutionStatus.SUCCEEDED
    assert result.step_results[1].status == StepExecutionStatus.FAILED
    assert "sliver exec" in (result.step_results[0].rendered_command or "")
    assert len(result.rollback_results) == 1
    assert result.rollback_results[0].status == StepExecutionStatus.ROLLED_BACK
    assert "auth_revoke" in (result.rollback_results[0].rendered_rollback or "")

    missing_var_playbook = engine.create_playbook(
        name="Missing Variable Validation",
        description="Template variable coverage check",
        created_by="alice",
    )
    bad_module = engine.register_technique_module(
        name="Bad Template",
        technique_id="T1059",
        default_command_template="run_bad --arg {undefined_var}",
    )
    engine.add_playbook_step(
        playbook_id=missing_var_playbook.playbook_id,
        step_order=1,
        name="bad-step",
        technique_module_id=bad_module.technique_module_id,
    )
    with pytest.raises(PlaybookEngineError, match="missing template variable"):
        engine.simulate_playbook(playbook_id=missing_var_playbook.playbook_id)

    assert first.step_id != second.step_id


def test_branching_next_on_failure_continues_without_terminal_rollback() -> None:
    engine = PlaybookEngine()
    playbook = engine.create_playbook(
        name="Failure Branch Handling",
        description="Use next_on_failure branch",
        created_by="alice",
        default_variables={"target_host": "srv-01"},
    )
    module = engine.register_technique_module(
        name="Generic Step",
        technique_id="T1059",
        default_command_template="run_step --target {target_host}",
        default_rollback_template="rollback_step --target {target_host}",
    )
    engine.add_playbook_step(
        playbook_id=playbook.playbook_id,
        step_order=1,
        name="step-1",
        technique_module_id=module.technique_module_id,
    )
    third = engine.add_playbook_step(
        playbook_id=playbook.playbook_id,
        step_order=3,
        name="remediation",
        technique_module_id=module.technique_module_id,
    )
    second = engine.add_playbook_step(
        playbook_id=playbook.playbook_id,
        step_order=2,
        name="step-2-fail",
        technique_module_id=module.technique_module_id,
        next_on_failure=third.step_id,
    )

    result = engine.simulate_playbook(
        playbook_id=playbook.playbook_id,
        runtime_variables={"target_host": "srv-01"},
        fail_step_ids={second.step_id},
    )
    assert result.status == StepExecutionStatus.SUCCEEDED
    assert len(result.rollback_results) == 0
