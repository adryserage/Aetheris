"""
Executor for Aetheris Conductor (v3.0)

Executes plans step by step with progress tracking.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from rich.console import Console
from rich.live import Live
from rich.table import Table

from src.conductor.cycle_detector import CycleDetector, ExecutionState
from src.conductor.planner import ExecutionPlan, PlanStep
from src.skills.base_skill import SkillResult, SkillResultStatus
from src.skills.registry import SkillRegistry


class StepStatus(Enum):
    """Status of a plan step"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ExecutionResult:
    """Result of plan execution"""

    success: bool
    completed_steps: int
    total_steps: int
    outputs: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    cycle_detected: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "completed_steps": self.completed_steps,
            "total_steps": self.total_steps,
            "outputs": self.outputs,
            "errors": self.errors,
            "cycle_detected": self.cycle_detected,
        }


class Executor:
    """Executes plans step by step"""

    def __init__(
        self,
        skill_registry: SkillRegistry,
        console: Optional[Console] = None,
        verbose: bool = True,
    ) -> None:
        self._registry = skill_registry
        self._console = console or Console()
        self._verbose = verbose
        self._cycle_detector = CycleDetector()
        self._step_outputs: Dict[str, Any] = {}
        self._confirmation_callback: Optional[Callable[[str], bool]] = None

    def set_confirmation_callback(
        self,
        callback: Callable[[str], bool],
    ) -> None:
        """Set callback for confirmation prompts"""
        self._confirmation_callback = callback

    async def execute_plan(
        self,
        plan: ExecutionPlan,
    ) -> ExecutionResult:
        """Execute a plan and return results"""
        self._cycle_detector.reset()
        self._step_outputs.clear()

        # Validate plan first
        errors = plan.validate()
        if errors:
            return ExecutionResult(
                success=False,
                completed_steps=0,
                total_steps=len(plan.steps),
                errors=errors,
            )

        # Get execution order
        execution_order = plan.get_execution_order()

        completed = 0
        result_errors: List[str] = []

        # Execute with live progress display if verbose
        if self._verbose:
            with Live(
                self._create_progress_table(plan, execution_order),
                console=self._console,
                refresh_per_second=4,
            ) as live:
                for i, step_id in enumerate(execution_order):
                    step = plan.get_step(step_id)
                    if not step:
                        continue

                    # Check for cycle
                    state = ExecutionState(
                        step_id=step_id,
                        step_number=i,
                        arguments=step.arguments,
                        previous_outputs=dict(self._step_outputs),
                    )
                    if self._cycle_detector.check_state(state):
                        cycle_info = self._cycle_detector.get_cycle_info()
                        result_errors.append(f"Cycle detected at step {step_id}: " f"{cycle_info}")
                        return ExecutionResult(
                            success=False,
                            completed_steps=completed,
                            total_steps=len(plan.steps),
                            outputs=self._step_outputs,
                            errors=result_errors,
                            cycle_detected=True,
                        )

                    # Update status to running
                    step.status = StepStatus.RUNNING.value
                    live.update(self._create_progress_table(plan, execution_order))

                    # Execute step
                    step_result = await self._execute_step(step)

                    if step_result.status == SkillResultStatus.SUCCESS:
                        step.status = StepStatus.COMPLETED.value
                        step.result = step_result.output
                        self._step_outputs[step_id] = step_result.output
                        completed += 1
                    elif step_result.status == SkillResultStatus.DENIED:
                        step.status = StepStatus.SKIPPED.value
                        step.error = step_result.error
                        result_errors.append(f"Step {step_id} denied: {step_result.error}")
                    else:
                        step.status = StepStatus.FAILED.value
                        step.error = step_result.error
                        result_errors.append(f"Step {step_id} failed: {step_result.error}")
                        # Skip dependent steps
                        self._skip_dependents(plan, step_id, execution_order)

                    live.update(self._create_progress_table(plan, execution_order))
        else:
            # Non-verbose execution
            for i, step_id in enumerate(execution_order):
                step = plan.get_step(step_id)
                if not step:
                    continue

                if step.status == StepStatus.SKIPPED.value:
                    continue

                # Check for cycle
                state = ExecutionState(
                    step_id=step_id,
                    step_number=i,
                    arguments=step.arguments,
                    previous_outputs=dict(self._step_outputs),
                )
                if self._cycle_detector.check_state(state):
                    return ExecutionResult(
                        success=False,
                        completed_steps=completed,
                        total_steps=len(plan.steps),
                        outputs=self._step_outputs,
                        errors=["Cycle detected"],
                        cycle_detected=True,
                    )

                step_result = await self._execute_step(step)

                if step_result.status == SkillResultStatus.SUCCESS:
                    self._step_outputs[step_id] = step_result.output
                    completed += 1
                else:
                    result_errors.append(f"Step {step_id} failed: {step_result.error}")
                    self._skip_dependents(plan, step_id, execution_order)

        success = completed == len(plan.steps) and not result_errors

        return ExecutionResult(
            success=success,
            completed_steps=completed,
            total_steps=len(plan.steps),
            outputs=self._step_outputs,
            errors=result_errors,
        )

    async def _execute_step(self, step: PlanStep) -> SkillResult:
        """Execute a single step"""
        # Get skill from registry
        skill = self._registry.get(step.skill)
        if not skill:
            return SkillResult(
                status=SkillResultStatus.ERROR,
                error=f"Unknown skill: {step.skill}",
            )

        # Resolve argument references
        resolved_args = self._resolve_arguments(step.arguments)

        # Check if confirmation needed
        if skill.requires_confirmation and self._confirmation_callback:
            prompt = (
                f"Step '{step.description}' wants to execute '{step.skill}' "
                f"with arguments: {resolved_args}"
            )
            if not self._confirmation_callback(prompt):
                return SkillResult(
                    status=SkillResultStatus.DENIED,
                    error="User denied execution",
                )

        # Execute skill
        try:
            return await skill.execute(resolved_args)
        except Exception as e:
            return SkillResult(
                status=SkillResultStatus.ERROR,
                error=str(e),
            )

    def _resolve_arguments(
        self,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Resolve references to previous step outputs in arguments"""
        resolved: Dict[str, Any] = {}

        for key, value in arguments.items():
            if isinstance(value, str):
                # Check for ${step_id.output} pattern
                resolved[key] = self._resolve_value(value)
            elif isinstance(value, dict):
                resolved[key] = self._resolve_arguments(value)
            elif isinstance(value, list):
                resolved[key] = [self._resolve_value(v) if isinstance(v, str) else v for v in value]
            else:
                resolved[key] = value

        return resolved

    def _resolve_value(self, value: str) -> Any:
        """Resolve a single value that may contain references"""
        # Pattern: ${step_id.output} or ${step_id.field}
        pattern = r"\$\{(\w+)\.(\w+)\}"

        def replacer(match: re.Match) -> str:
            step_id = match.group(1)
            field_name = match.group(2)

            output = self._step_outputs.get(step_id)
            if output is None:
                return match.group(0)  # Keep original if not found

            if field_name == "output":
                return str(output) if output else ""
            elif isinstance(output, dict):
                return str(output.get(field_name, match.group(0)))
            else:
                return str(output)

        return re.sub(pattern, replacer, value)

    def _skip_dependents(
        self,
        plan: ExecutionPlan,
        failed_step_id: str,
        execution_order: List[str],
    ) -> None:
        """Mark all steps depending on failed step as skipped"""
        to_skip = set()

        # Find all steps that depend on the failed step
        for step in plan.steps:
            if failed_step_id in step.depends_on:
                to_skip.add(step.id)

        # Transitively find steps depending on skipped steps
        changed = True
        while changed:
            changed = False
            for step in plan.steps:
                if step.id in to_skip:
                    continue
                for dep in step.depends_on:
                    if dep in to_skip:
                        to_skip.add(step.id)
                        changed = True
                        break

        # Mark as skipped
        for step in plan.steps:
            if step.id in to_skip:
                step.status = StepStatus.SKIPPED.value
                step.error = f"Skipped due to failed dependency: {failed_step_id}"

    def _create_progress_table(
        self,
        plan: ExecutionPlan,
        execution_order: List[str],
    ) -> Table:
        """Create a Rich table showing plan progress"""
        table = Table(title=f"Plan: {plan.goal}", show_lines=True)
        table.add_column("Step", style="cyan", width=10)
        table.add_column("Description", width=40)
        table.add_column("Skill", style="magenta", width=15)
        table.add_column("Status", width=12)

        status_styles = {
            "pending": "dim",
            "running": "yellow bold",
            "completed": "green",
            "failed": "red bold",
            "skipped": "dim strikethrough",
        }

        for step_id in execution_order:
            step = plan.get_step(step_id)
            if not step:
                continue

            status = step.status
            style = status_styles.get(status, "")

            status_display = status.upper()
            if status == "running":
                status_display = "⏳ RUNNING"
            elif status == "completed":
                status_display = "✅ DONE"
            elif status == "failed":
                status_display = "❌ FAILED"
            elif status == "skipped":
                status_display = "⏭️ SKIPPED"

            table.add_row(
                step.id,
                step.description[:38] + "..." if len(step.description) > 40 else step.description,
                step.skill,
                f"[{style}]{status_display}[/{style}]" if style else status_display,
            )

        return table
