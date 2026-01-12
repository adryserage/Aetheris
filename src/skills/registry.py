"""
Skill Registry for Aetheris (v3.0)

Manages registration and lookup of skills.
Supports built-in and custom skills.
"""

import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from src.skills.base_skill import (
    SandboxValidator,
    Skill,
    SkillParameter,
    SkillResult,
    SkillResultStatus,
)
from src.skills.file_skills import ReadFileSkill, WriteFileSkill, SearchFilesSkill
from src.skills.shell_skill import ExecuteCommandSkill


@dataclass
class CustomSkill(Skill):
    """A custom skill defined via YAML configuration"""

    name: str = ""
    description: str = ""
    parameters: List[SkillParameter] = field(default_factory=list)
    requires_confirmation: bool = False
    command_template: Optional[str] = None

    async def execute(self, arguments: Dict[str, Any]) -> SkillResult:
        """Execute custom skill via command template"""
        if not self.command_template:
            return SkillResult(
                status=SkillResultStatus.ERROR,
                error="Custom skill has no command template",
            )

        # Substitute arguments into command template
        command = self.command_template
        for name, value in arguments.items():
            command = command.replace(f"{{{name}}}", str(value))

        # Check for unsubstituted placeholders
        import re

        remaining = re.findall(r"\{(\w+)\}", command)
        if remaining:
            return SkillResult(
                status=SkillResultStatus.ERROR,
                error=f"Missing arguments: {', '.join(remaining)}",
            )

        # Execute via shell
        import asyncio

        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=60,
            )

            stdout_str = stdout.decode("utf-8", errors="replace")
            stderr_str = stderr.decode("utf-8", errors="replace")

            if process.returncode == 0:
                return SkillResult(
                    status=SkillResultStatus.SUCCESS,
                    output=stdout_str,
                    data={"command": command, "return_code": 0},
                )
            else:
                return SkillResult(
                    status=SkillResultStatus.ERROR,
                    output=stderr_str or stdout_str,
                    error=f"Command failed with exit code {process.returncode}",
                )

        except asyncio.TimeoutError:
            return SkillResult(
                status=SkillResultStatus.ERROR,
                error="Command timed out",
            )
        except Exception as e:
            return SkillResult(
                status=SkillResultStatus.ERROR,
                error=f"Failed to execute: {e}",
            )


class SkillRegistry:
    """Registry for managing skills"""

    def __init__(self, sandbox_root: Optional[Path] = None) -> None:
        self._skills: Dict[str, Skill] = {}
        self._enabled: Dict[str, bool] = {}  # Skill name -> enabled status
        self._sandbox = SandboxValidator(sandbox_root) if sandbox_root else SandboxValidator()
        self._register_builtin_skills()

    def _register_builtin_skills(self) -> None:
        """Register built-in skills"""
        builtins: List[Skill] = [
            ReadFileSkill(sandbox=self._sandbox),
            WriteFileSkill(sandbox=self._sandbox),
            SearchFilesSkill(sandbox=self._sandbox),
            ExecuteCommandSkill(sandbox=self._sandbox),
        ]

        for skill in builtins:
            self.register(skill)

    def register(self, skill: Skill, enabled: bool = True) -> None:
        """Register a skill"""
        self._skills[skill.name] = skill
        self._enabled[skill.name] = enabled

    def unregister(self, name: str) -> bool:
        """Unregister a skill. Returns True if skill existed."""
        if name in self._skills:
            del self._skills[name]
            del self._enabled[name]
            return True
        return False

    def get(self, name: str) -> Optional[Skill]:
        """Get a skill by name"""
        skill = self._skills.get(name)
        if skill and self._enabled.get(name, False):
            return skill
        return None

    def get_all(self, include_disabled: bool = False) -> List[Skill]:
        """Get all registered skills"""
        if include_disabled:
            return list(self._skills.values())
        return [s for s in self._skills.values() if self._enabled.get(s.name, False)]

    def enable(self, name: str) -> bool:
        """Enable a skill. Returns True if skill exists."""
        if name in self._skills:
            self._enabled[name] = True
            return True
        return False

    def disable(self, name: str) -> bool:
        """Disable a skill. Returns True if skill exists."""
        if name in self._skills:
            self._enabled[name] = False
            return True
        return False

    def is_enabled(self, name: str) -> bool:
        """Check if a skill is enabled"""
        return self._enabled.get(name, False)

    def load_custom_skills(self, path: Path) -> List[str]:
        """Load custom skills from a YAML file. Returns list of loaded skill names."""
        if not path.exists():
            return []

        loaded: List[str] = []

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if not isinstance(data, dict) or "skills" not in data:
                return []

            for skill_def in data["skills"]:
                skill = self._parse_custom_skill(skill_def)
                if skill:
                    self.register(skill)
                    loaded.append(skill.name)

        except Exception:
            # Log error but don't crash
            pass

        return loaded

    def _parse_custom_skill(self, skill_def: Dict[str, Any]) -> Optional[CustomSkill]:
        """Parse a custom skill definition from YAML"""
        if not isinstance(skill_def, dict):
            return None

        name = skill_def.get("name")
        description = skill_def.get("description", "")
        command = skill_def.get("command")

        if not name:
            return None

        parameters: List[SkillParameter] = []
        for param_def in skill_def.get("parameters", []):
            if isinstance(param_def, dict):
                parameters.append(
                    SkillParameter(
                        name=param_def.get("name", ""),
                        description=param_def.get("description", ""),
                        param_type=param_def.get("type", "string"),
                        required=param_def.get("required", False),
                        default=param_def.get("default"),
                        enum=param_def.get("enum"),
                    )
                )

        return CustomSkill(
            name=name,
            description=description,
            parameters=parameters,
            requires_confirmation=skill_def.get("requires_confirmation", False),
            command_template=command,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Export registry state to dictionary"""
        return {
            "skills": [
                {
                    "name": s.name,
                    "description": s.description,
                    "enabled": self._enabled.get(s.name, False),
                    "requires_confirmation": s.requires_confirmation,
                }
                for s in self._skills.values()
            ]
        }
