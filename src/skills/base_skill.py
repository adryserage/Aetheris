"""
Base Skill Definitions for Aetheris (v3.0)

Abstract base class and data models for AI agent skills.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class SkillResultStatus(Enum):
    """Status of skill execution"""

    SUCCESS = "success"
    ERROR = "error"
    DENIED = "denied"  # Blocked by safety/sandbox


@dataclass
class SkillParameter:
    """Definition of a skill parameter"""

    name: str
    description: str
    param_type: str = "string"  # string, integer, boolean, array, object
    required: bool = False
    default: Optional[Any] = None
    enum: Optional[List[str]] = None  # Allowed values


@dataclass
class SkillResult:
    """Result of skill execution"""

    status: SkillResultStatus
    output: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class SkillCall:
    """Represents a call to a skill"""

    skill_name: str
    arguments: Dict[str, Any] = field(default_factory=dict)
    call_id: Optional[str] = None  # For tracking in multi-turn conversations


@dataclass
class Skill(ABC):
    """Abstract base class for all skills"""

    name: str
    description: str
    parameters: List[SkillParameter] = field(default_factory=list)
    requires_confirmation: bool = False  # If true, prompt user before execution

    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> SkillResult:
        """Execute the skill with given arguments"""
        pass

    def validate_arguments(self, arguments: Dict[str, Any]) -> Optional[str]:
        """Validate arguments against parameter definitions. Returns error message if invalid."""
        for param in self.parameters:
            if param.required and param.name not in arguments:
                return f"Missing required parameter: {param.name}"

            if param.name in arguments and param.enum:
                if arguments[param.name] not in param.enum:
                    return f"Invalid value for {param.name}: must be one of {param.enum}"

        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert skill definition to dictionary format"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": [
                {
                    "name": p.name,
                    "description": p.description,
                    "type": p.param_type,
                    "required": p.required,
                    "default": p.default,
                    "enum": p.enum,
                }
                for p in self.parameters
            ],
            "requires_confirmation": self.requires_confirmation,
        }


class SandboxValidator:
    """Validates paths and operations against sandbox rules"""

    def __init__(self, root_path: Optional[Path] = None) -> None:
        self.root_path = root_path or Path.cwd()
        self.allowed_paths: List[Path] = [self.root_path]

    def add_allowed_path(self, path: Path) -> None:
        """Add an additional allowed path"""
        self.allowed_paths.append(path.resolve())

    def is_path_allowed(self, path: Path) -> bool:
        """Check if a path is within allowed boundaries"""
        try:
            resolved = path.resolve()
            return any(self._is_subpath(resolved, allowed) for allowed in self.allowed_paths)
        except (OSError, ValueError):
            return False

    def _is_subpath(self, path: Path, parent: Path) -> bool:
        """Check if path is a subpath of parent"""
        try:
            path.relative_to(parent)
            return True
        except ValueError:
            return False

    def validate_path(self, path_str: str) -> Optional[str]:
        """Validate a path string. Returns error message if invalid."""
        try:
            path = Path(path_str)
            if not self.is_path_allowed(path):
                return f"Path '{path_str}' is outside the allowed sandbox"
            return None
        except (OSError, ValueError) as e:
            return f"Invalid path '{path_str}': {e}"
