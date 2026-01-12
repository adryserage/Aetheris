"""
Planner for Aetheris Conductor (v3.0)

Creates execution plans for multi-step tasks.
"""

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from src.skills.base_skill import SkillCall

MAX_PLAN_STEPS = 20
PLANNING_PROMPT_TEMPLATE = """You are a task planning assistant. Given a user request, create an execution plan using the available skills.

Available skills:
{skills_list}

User request: {user_request}

Create a JSON execution plan with the following structure:
{{
    "goal": "Brief description of what we're trying to achieve",
    "steps": [
        {{
            "id": "step_1",
            "description": "What this step does",
            "skill": "skill_name",
            "arguments": {{}},
            "depends_on": []
        }}
    ]
}}

Rules:
1. Maximum {max_steps} steps
2. Each step must use one of the available skills
3. Steps can depend on previous steps using "depends_on" array
4. Arguments can reference previous step outputs using ${{step_id.output}}
5. Keep the plan focused and minimal

Respond ONLY with valid JSON, no additional text.
"""


@dataclass
class PlanStep:
    """A single step in an execution plan"""

    id: str
    description: str
    skill: str
    arguments: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)

    # Runtime fields (filled during execution)
    status: str = "pending"  # pending, running, completed, failed, skipped
    result: Optional[Any] = None
    error: Optional[str] = None

    def to_skill_call(self) -> SkillCall:
        """Convert to SkillCall for execution"""
        return SkillCall(
            skill_name=self.skill,
            arguments=self.arguments,
        )


@dataclass
class ExecutionPlan:
    """An execution plan with multiple steps"""

    goal: str
    steps: List[PlanStep] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> List[str]:
        """Validate the plan and return list of errors"""
        errors: List[str] = []

        # Check step count
        if len(self.steps) > MAX_PLAN_STEPS:
            errors.append(f"Plan exceeds maximum of {MAX_PLAN_STEPS} steps")

        # Check step IDs are unique
        step_ids = set()
        for step in self.steps:
            if step.id in step_ids:
                errors.append(f"Duplicate step ID: {step.id}")
            step_ids.add(step.id)

        # Check dependencies reference valid steps
        for step in self.steps:
            for dep in step.depends_on:
                if dep not in step_ids:
                    errors.append(f"Step {step.id} depends on unknown step: {dep}")
                # Check for self-dependency
                if dep == step.id:
                    errors.append(f"Step {step.id} depends on itself")

        # Check for circular dependencies
        if not errors:  # Only check if no other errors
            if self._has_circular_dependencies():
                errors.append("Plan contains circular dependencies")

        return errors

    def _has_circular_dependencies(self) -> bool:
        """Check for circular dependencies using DFS"""
        visited: set[str] = set()
        rec_stack: set[str] = set()

        def dfs(step_id: str) -> bool:
            visited.add(step_id)
            rec_stack.add(step_id)

            step = next((s for s in self.steps if s.id == step_id), None)
            if step:
                for dep in step.depends_on:
                    if dep not in visited:
                        if dfs(dep):
                            return True
                    elif dep in rec_stack:
                        return True

            rec_stack.remove(step_id)
            return False

        for step in self.steps:
            if step.id not in visited:
                if dfs(step.id):
                    return True

        return False

    def get_execution_order(self) -> List[str]:
        """Return step IDs in topological order (respecting dependencies)"""
        # Build dependency graph
        in_degree: Dict[str, int] = {step.id: 0 for step in self.steps}
        graph: Dict[str, List[str]] = {step.id: [] for step in self.steps}

        for step in self.steps:
            for dep in step.depends_on:
                if dep in graph:
                    graph[dep].append(step.id)
                    in_degree[step.id] += 1

        # Kahn's algorithm for topological sort
        queue = [step_id for step_id, degree in in_degree.items() if degree == 0]
        result: List[str] = []

        while queue:
            current = queue.pop(0)
            result.append(current)

            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        return result

    def get_step(self, step_id: str) -> Optional[PlanStep]:
        """Get a step by ID"""
        return next((s for s in self.steps if s.id == step_id), None)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "goal": self.goal,
            "steps": [
                {
                    "id": s.id,
                    "description": s.description,
                    "skill": s.skill,
                    "arguments": s.arguments,
                    "depends_on": s.depends_on,
                    "status": s.status,
                }
                for s in self.steps
            ],
            "metadata": self.metadata,
        }


class Planner:
    """Creates execution plans from user requests"""

    def __init__(self, ai_provider: Any) -> None:
        self._ai_provider = ai_provider

    async def create_plan(
        self,
        user_request: str,
        available_skills: List[Dict[str, Any]],
    ) -> ExecutionPlan:
        """Create an execution plan for the given request"""
        # Build skills list for prompt
        skills_list = "\n".join(
            f"- {s['name']}: {s.get('description', 'No description')}" for s in available_skills
        )

        prompt = PLANNING_PROMPT_TEMPLATE.format(
            skills_list=skills_list,
            user_request=user_request,
            max_steps=MAX_PLAN_STEPS,
        )

        # Call AI provider
        response = await self._ai_provider.generate(prompt)

        # Parse response
        return self._parse_plan_response(response)

    def _parse_plan_response(self, response: str) -> ExecutionPlan:
        """Parse AI response into ExecutionPlan"""
        # Extract JSON from response (handle markdown code blocks)
        json_str = response.strip()
        if json_str.startswith("```"):
            lines = json_str.split("\n")
            json_lines = []
            in_block = False
            for line in lines:
                if line.startswith("```") and not in_block:
                    in_block = True
                    continue
                elif line.startswith("```") and in_block:
                    break
                elif in_block:
                    json_lines.append(line)
            json_str = "\n".join(json_lines)

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            # Return empty plan on parse error
            return ExecutionPlan(
                goal="Failed to parse plan",
                metadata={"error": str(e), "raw_response": response},
            )

        # Build plan
        goal = data.get("goal", "Unknown goal")
        steps: List[PlanStep] = []

        for step_data in data.get("steps", []):
            step = PlanStep(
                id=step_data.get("id", f"step_{len(steps) + 1}"),
                description=step_data.get("description", ""),
                skill=step_data.get("skill", ""),
                arguments=step_data.get("arguments", {}),
                depends_on=step_data.get("depends_on", []),
            )
            steps.append(step)

        plan = ExecutionPlan(goal=goal, steps=steps)

        # Validate
        errors = plan.validate()
        if errors:
            plan.metadata["validation_errors"] = errors

        return plan

    def create_simple_plan(
        self,
        skill_name: str,
        arguments: Dict[str, Any],
        description: str = "",
    ) -> ExecutionPlan:
        """Create a simple single-step plan"""
        step = PlanStep(
            id="step_1",
            description=description or f"Execute {skill_name}",
            skill=skill_name,
            arguments=arguments,
        )
        return ExecutionPlan(
            goal=description or f"Execute {skill_name}",
            steps=[step],
        )
