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

"""Playbook framework and simulation engine (Phase 5 Sprint 5.1)."""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from threading import Lock
from typing import Any
from uuid import uuid4


class PlaybookEngineError(ValueError):
    """Raised when playbook modeling or execution simulation fails."""


class PlaybookStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"


class StepExecutionStatus(str, Enum):
    PENDING = "pending"
    SKIPPED = "skipped"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass(slots=True, frozen=True)
class PlaybookRecord:
    """Playbook table row."""

    playbook_id: str
    name: str
    description: str
    created_by: str
    created_at: datetime
    status: PlaybookStatus = PlaybookStatus.DRAFT
    default_variables: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class WrapperTemplateRecord:
    """Wrapper template registry row."""

    wrapper_template_id: str
    name: str
    command_template: str
    rollback_template: str | None = None
    runtime: str = "shell"


@dataclass(slots=True, frozen=True)
class TechniqueModuleRecord:
    """Reusable technique module row."""

    technique_module_id: str
    name: str
    technique_id: str
    default_command_template: str
    default_rollback_template: str | None = None
    default_variables: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class PlaybookStepRecord:
    """PlaybookStep table row."""

    step_id: str
    playbook_id: str
    step_order: int
    name: str
    technique_module_id: str
    variables: dict[str, Any] = field(default_factory=dict)
    command_template: str | None = None
    rollback_template: str | None = None
    wrapper_template_id: str | None = None
    condition_expression: str | None = None
    next_on_success: str | None = None
    next_on_failure: str | None = None


@dataclass(slots=True, frozen=True)
class StepSimulationRecord:
    """Single step simulation result."""

    step_id: str
    status: StepExecutionStatus
    rendered_command: str | None = None
    rendered_rollback: str | None = None
    error: str | None = None


@dataclass(slots=True, frozen=True)
class PlaybookSimulationResult:
    """Complex multi-step simulation output."""

    playbook_id: str
    status: StepExecutionStatus
    step_results: tuple[StepSimulationRecord, ...]
    rollback_results: tuple[StepSimulationRecord, ...]
    variables_final: dict[str, Any]


class _SafeConditionEvaluator(ast.NodeVisitor):
    def __init__(self, variables: dict[str, Any]) -> None:
        self._variables = variables

    def evaluate(self, expression: str) -> bool:
        node = ast.parse(expression, mode="eval")
        return bool(self.visit(node.body))

    def visit_Name(self, node: ast.Name) -> Any:  # noqa: N802
        if node.id not in self._variables:
            raise PlaybookEngineError(f"unknown variable in condition: {node.id}")
        return self._variables[node.id]

    def visit_Constant(self, node: ast.Constant) -> Any:  # noqa: N802
        return node.value

    def visit_Compare(self, node: ast.Compare) -> Any:  # noqa: N802
        left = self.visit(node.left)
        for op, comparator in zip(node.ops, node.comparators):
            right = self.visit(comparator)
            if isinstance(op, ast.Eq):
                ok = left == right
            elif isinstance(op, ast.NotEq):
                ok = left != right
            elif isinstance(op, ast.Gt):
                ok = left > right
            elif isinstance(op, ast.GtE):
                ok = left >= right
            elif isinstance(op, ast.Lt):
                ok = left < right
            elif isinstance(op, ast.LtE):
                ok = left <= right
            elif isinstance(op, ast.In):
                ok = left in right
            elif isinstance(op, ast.NotIn):
                ok = left not in right
            else:
                raise PlaybookEngineError("unsupported comparison operator")
            if not ok:
                return False
            left = right
        return True

    def visit_BoolOp(self, node: ast.BoolOp) -> Any:  # noqa: N802
        values = [bool(self.visit(item)) for item in node.values]
        if isinstance(node.op, ast.And):
            return all(values)
        if isinstance(node.op, ast.Or):
            return any(values)
        raise PlaybookEngineError("unsupported boolean operator")

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Any:  # noqa: N802
        if isinstance(node.op, ast.Not):
            return not bool(self.visit(node.operand))
        raise PlaybookEngineError("unsupported unary operator")

    def generic_visit(self, node: ast.AST) -> Any:
        raise PlaybookEngineError(f"unsupported expression node: {type(node).__name__}")


class PlaybookEngine:
    """Thread-safe playbook registry and deterministic simulation runtime."""

    def __init__(self) -> None:
        self._playbook_table: dict[str, PlaybookRecord] = {}
        self._playbook_step_table: dict[str, PlaybookStepRecord] = {}
        self._wrapper_template_table: dict[str, WrapperTemplateRecord] = {}
        self._technique_module_table: dict[str, TechniqueModuleRecord] = {}
        self._lock = Lock()

    def create_playbook(
        self,
        *,
        name: str,
        description: str,
        created_by: str,
        default_variables: dict[str, Any] | None = None,
    ) -> PlaybookRecord:
        if not name.strip():
            raise PlaybookEngineError("playbook name is required")
        if not created_by.strip():
            raise PlaybookEngineError("created_by is required")
        row = PlaybookRecord(
            playbook_id=f"pb-{uuid4()}",
            name=name.strip(),
            description=description.strip(),
            created_by=created_by.strip(),
            created_at=datetime.now(UTC),
            default_variables=dict(default_variables or {}),
        )
        with self._lock:
            if any(item.name == row.name for item in self._playbook_table.values()):
                raise PlaybookEngineError("playbook name already exists")
            self._playbook_table[row.playbook_id] = row
        return row

    def register_wrapper_template(
        self,
        *,
        name: str,
        command_template: str,
        rollback_template: str | None = None,
        runtime: str = "shell",
    ) -> WrapperTemplateRecord:
        if not command_template.strip():
            raise PlaybookEngineError("wrapper command_template is required")
        row = WrapperTemplateRecord(
            wrapper_template_id=f"wtmp-{uuid4()}",
            name=name.strip(),
            command_template=command_template.strip(),
            rollback_template=rollback_template.strip() if rollback_template else None,
            runtime=runtime.strip() or "shell",
        )
        with self._lock:
            self._wrapper_template_table[row.wrapper_template_id] = row
        return row

    def register_technique_module(
        self,
        *,
        name: str,
        technique_id: str,
        default_command_template: str,
        default_rollback_template: str | None = None,
        default_variables: dict[str, Any] | None = None,
    ) -> TechniqueModuleRecord:
        if not technique_id.strip():
            raise PlaybookEngineError("technique_id is required")
        if not default_command_template.strip():
            raise PlaybookEngineError("default_command_template is required")
        row = TechniqueModuleRecord(
            technique_module_id=f"tmod-{uuid4()}",
            name=name.strip(),
            technique_id=technique_id.strip().upper(),
            default_command_template=default_command_template.strip(),
            default_rollback_template=default_rollback_template.strip()
            if default_rollback_template
            else None,
            default_variables=dict(default_variables or {}),
        )
        with self._lock:
            self._technique_module_table[row.technique_module_id] = row
        return row

    def add_playbook_step(
        self,
        *,
        playbook_id: str,
        step_order: int,
        name: str,
        technique_module_id: str,
        variables: dict[str, Any] | None = None,
        command_template: str | None = None,
        rollback_template: str | None = None,
        wrapper_template_id: str | None = None,
        condition_expression: str | None = None,
        next_on_success: str | None = None,
        next_on_failure: str | None = None,
    ) -> PlaybookStepRecord:
        with self._lock:
            if playbook_id not in self._playbook_table:
                raise PlaybookEngineError("playbook not found")
            if technique_module_id not in self._technique_module_table:
                raise PlaybookEngineError("technique module not found")
            if wrapper_template_id and wrapper_template_id not in self._wrapper_template_table:
                raise PlaybookEngineError("wrapper template not found")
            existing_orders = [
                step.step_order
                for step in self._playbook_step_table.values()
                if step.playbook_id == playbook_id
            ]
            if step_order in existing_orders:
                raise PlaybookEngineError("duplicate step_order for playbook")
            row = PlaybookStepRecord(
                step_id=f"pbs-{uuid4()}",
                playbook_id=playbook_id,
                step_order=step_order,
                name=name.strip(),
                technique_module_id=technique_module_id,
                variables=dict(variables or {}),
                command_template=command_template.strip() if command_template else None,
                rollback_template=rollback_template.strip() if rollback_template else None,
                wrapper_template_id=wrapper_template_id,
                condition_expression=condition_expression.strip() if condition_expression else None,
                next_on_success=next_on_success,
                next_on_failure=next_on_failure,
            )
            self._playbook_step_table[row.step_id] = row
        return row

    def simulate_playbook(
        self,
        *,
        playbook_id: str,
        runtime_variables: dict[str, Any] | None = None,
        fail_step_ids: set[str] | None = None,
    ) -> PlaybookSimulationResult:
        playbook = self._playbook_table.get(playbook_id)
        if playbook is None:
            raise PlaybookEngineError("playbook not found")
        ordered = self._ordered_steps(playbook_id=playbook_id)
        if not ordered:
            raise PlaybookEngineError("playbook has no steps")

        steps_by_id = {step.step_id: step for step in ordered}
        order_index = {step.step_id: index for index, step in enumerate(ordered)}
        fail_step_ids = set(fail_step_ids or set())
        variables: dict[str, Any] = {**playbook.default_variables, **dict(runtime_variables or {})}
        executed: list[PlaybookStepRecord] = []
        step_results: list[StepSimulationRecord] = []
        rollback_results: list[StepSimulationRecord] = []
        terminal_failure = False

        current_step_id = ordered[0].step_id
        visited: set[str] = set()
        while current_step_id:
            if current_step_id in visited:
                raise PlaybookEngineError("loop detected in playbook branch graph")
            visited.add(current_step_id)
            step = steps_by_id.get(current_step_id)
            if step is None:
                raise PlaybookEngineError("branch step target not found")

            if not self._evaluate_condition(step.condition_expression, variables):
                step_results.append(
                    StepSimulationRecord(
                        step_id=step.step_id,
                        status=StepExecutionStatus.SKIPPED,
                    )
                )
                current_step_id = self._resolve_next_step_id(step, succeeded=True, ordered=ordered, order_index=order_index)
                continue

            command, rollback_command = self._render_step(step=step, variables=variables)
            if step.step_id in fail_step_ids:
                step_results.append(
                    StepSimulationRecord(
                        step_id=step.step_id,
                        status=StepExecutionStatus.FAILED,
                        rendered_command=command,
                        rendered_rollback=rollback_command,
                        error="simulated step failure",
                    )
                )
                if step.next_on_failure:
                    current_step_id = step.next_on_failure
                    continue
                terminal_failure = True
                break

            executed.append(step)
            step_results.append(
                StepSimulationRecord(
                    step_id=step.step_id,
                    status=StepExecutionStatus.SUCCEEDED,
                    rendered_command=command,
                    rendered_rollback=rollback_command,
                )
            )
            variables[f"step_{step.step_order}_status"] = "succeeded"
            variables[f"step_{step.step_order}_command"] = command
            current_step_id = self._resolve_next_step_id(step, succeeded=True, ordered=ordered, order_index=order_index)

        if terminal_failure:
            for step in reversed(executed):
                _, rollback_command = self._render_step(step=step, variables=variables)
                if rollback_command:
                    rollback_results.append(
                        StepSimulationRecord(
                            step_id=step.step_id,
                            status=StepExecutionStatus.ROLLED_BACK,
                            rendered_rollback=rollback_command,
                        )
                    )
            overall = StepExecutionStatus.FAILED
        else:
            overall = StepExecutionStatus.SUCCEEDED

        return PlaybookSimulationResult(
            playbook_id=playbook_id,
            status=overall,
            step_results=tuple(step_results),
            rollback_results=tuple(rollback_results),
            variables_final=variables,
        )

    def _ordered_steps(self, *, playbook_id: str) -> list[PlaybookStepRecord]:
        rows = [step for step in self._playbook_step_table.values() if step.playbook_id == playbook_id]
        return sorted(rows, key=lambda item: item.step_order)

    def _resolve_next_step_id(
        self,
        step: PlaybookStepRecord,
        *,
        succeeded: bool,
        ordered: list[PlaybookStepRecord],
        order_index: dict[str, int],
    ) -> str | None:
        branch = step.next_on_success if succeeded else step.next_on_failure
        if branch:
            return branch
        idx = order_index[step.step_id]
        next_idx = idx + 1
        if next_idx >= len(ordered):
            return None
        return ordered[next_idx].step_id

    def _render_step(self, *, step: PlaybookStepRecord, variables: dict[str, Any]) -> tuple[str, str | None]:
        module = self._technique_module_table[step.technique_module_id]
        context = {**module.default_variables, **variables, **step.variables}
        base_command_template = step.command_template or module.default_command_template
        base_rollback_template = step.rollback_template or module.default_rollback_template
        command = self._format_template(base_command_template, context)
        rollback_command = (
            self._format_template(base_rollback_template, context)
            if base_rollback_template
            else None
        )
        if step.wrapper_template_id:
            wrapper = self._wrapper_template_table[step.wrapper_template_id]
            command = self._format_template(
                wrapper.command_template,
                {**context, "payload": command},
            )
            if rollback_command and wrapper.rollback_template:
                rollback_command = self._format_template(
                    wrapper.rollback_template,
                    {**context, "payload": rollback_command},
                )
        return command, rollback_command

    def _format_template(self, template: str | None, context: dict[str, Any]) -> str:
        if template is None:
            raise PlaybookEngineError("template not defined")
        try:
            return template.format(**context)
        except KeyError as exc:
            raise PlaybookEngineError(f"missing template variable: {exc.args[0]}") from exc

    def _evaluate_condition(self, expression: str | None, variables: dict[str, Any]) -> bool:
        if not expression:
            return True
        evaluator = _SafeConditionEvaluator(variables=variables)
        return evaluator.evaluate(expression)

