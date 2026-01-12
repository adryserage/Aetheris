"""
Base Skill Adapter for Aetheris (v3.0)

Abstract base class for provider-specific skill adapters.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from src.skills.base_skill import Skill, SkillCall, SkillResult


class SkillAdapter(ABC):
    """Abstract base class for skill adapters"""

    @abstractmethod
    def to_api_format(self, skills: List[Skill]) -> List[Dict[str, Any]]:
        """
        Convert skills to provider-specific API format.

        Args:
            skills: List of skills to convert

        Returns:
            List of tool/function definitions in provider format
        """
        pass

    @abstractmethod
    def parse_response(self, response: Any) -> List[SkillCall]:
        """
        Parse provider response to extract skill calls.

        Args:
            response: Provider-specific response object

        Returns:
            List of SkillCall objects to execute
        """
        pass

    @abstractmethod
    def format_result(self, call: SkillCall, result: SkillResult) -> Dict[str, Any]:
        """
        Format skill result for inclusion in conversation.

        Args:
            call: The original skill call
            result: The execution result

        Returns:
            Provider-specific format for tool result
        """
        pass

    def _param_type_to_json_schema(self, param_type: str) -> str:
        """Convert parameter type to JSON Schema type"""
        type_mapping = {
            "string": "string",
            "integer": "integer",
            "number": "number",
            "boolean": "boolean",
            "array": "array",
            "object": "object",
        }
        return type_mapping.get(param_type, "string")
