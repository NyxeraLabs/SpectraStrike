# Sprint 47: Playbook Framework

## Playbook and step models
- Added `PlaybookRecord` (`Playbook` table abstraction).
- Added `PlaybookStepRecord` (`PlaybookStep` table abstraction).
- Added status and simulation models:
  - `PlaybookStatus`
  - `StepExecutionStatus`
  - `StepSimulationRecord`
  - `PlaybookSimulationResult`

## Step ordering logic
- Enforced per-playbook unique `step_order`.
- Simulation runs in deterministic order unless explicit branch targets override flow.

## Conditional branching support
- Added per-step:
  - `condition_expression`
  - `next_on_success`
  - `next_on_failure`
- Conditions are validated through restricted AST evaluation.
- Branch loops are rejected during simulation.

## Variable injection support
- Added template rendering with layered context:
  - playbook defaults
  - runtime variables
  - technique-module defaults
  - step variables
- Missing template variables raise `PlaybookEngineError`.

## Wrapper template registry
- Added `WrapperTemplateRecord`.
- Wrapper templates can encapsulate payload commands and rollback commands.

## Reusable technique modules
- Added `TechniqueModuleRecord`.
- Playbook steps reference module IDs and inherit command/rollback defaults.

## Execution rollback handling
- On terminal failure (without `next_on_failure` branch), previously succeeded steps are rolled back in reverse order.
- Rollback commands are rendered with the same resolved variable context.

## Validation
- Added complex multi-step unit tests covering:
  - ordering constraints
  - branch continuation behavior
  - variable injection
  - wrapper rendering
  - failure rollback behavior
