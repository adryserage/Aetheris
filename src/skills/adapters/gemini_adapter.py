"""
Gemini Skill Adapter for Aetheris (v3.0)

Converts skills to Gemini Function Calling format and parses responses.

Gemini Function Declaration format:
{
    "name": "skill_name",
    "description": "...",
    "parameters": {
        "type": "object",
        "properties": {...},
        "required": [...]
    }
}
"""

from typing import Any, Dict, List, Optional

from src.skills.adapters.base_adapter import SkillAdapter
from src.skills.base_skill import Skill, SkillCall, SkillResult, SkillResultStatus


class GeminiAdapter(SkillAdapter):
    """Adapter for Gemini Function Calling format"""

    def to_api_format(self, skills: List[Skill]) -> List[Dict[str, Any]]:
        """Convert skills to Gemini function declarations"""
        functions: List[Dict[str, Any]] = []

        for skill in skills:
            func = {
                "name": skill.name,
                "description": skill.description,
                "parameters": self._build_parameters_schema(skill),
            }
            functions.append(func)

        return functions

    def _build_parameters_schema(self, skill: Skill) -> Dict[str, Any]:
        """Build parameters schema for Gemini"""
        properties: Dict[str, Any] = {}
        required: List[str] = []

        for param in skill.parameters:
            prop: Dict[str, Any] = {
                "type": self._param_type_to_json_schema(param.param_type),
                "description": param.description,
            }

            if param.enum:
                prop["enum"] = param.enum

            properties[param.name] = prop

            if param.required:
                required.append(param.name)

        schema: Dict[str, Any] = {
            "type": "object",
            "properties": properties,
        }

        if required:
            schema["required"] = required

        return schema

    def to_tools_config(self, skills: List[Skill]) -> Dict[str, Any]:
        """Create tools configuration for Gemini API"""
        return {"tools": [{"function_declarations": self.to_api_format(skills)}]}

    def parse_response(self, response: Any) -> List[SkillCall]:
        """Parse Gemini response to extract function calls"""
        calls: List[SkillCall] = []

        # Handle different response formats
        candidates = None
        if isinstance(response, dict):
            candidates = response.get("candidates", [])
        elif hasattr(response, "candidates"):
            candidates = response.candidates
        else:
            return calls

        if not candidates:
            return calls

        # Get content from first candidate
        candidate = candidates[0]
        content = None
        if isinstance(candidate, dict):
            content = candidate.get("content", {})
        elif hasattr(candidate, "content"):
            content = candidate.content

        if not content:
            return calls

        # Get parts from content
        parts = None
        if isinstance(content, dict):
            parts = content.get("parts", [])
        elif hasattr(content, "parts"):
            parts = content.parts

        if not parts:
            return calls

        # Extract function calls from parts
        for part in parts:
            function_call = None
            if isinstance(part, dict):
                function_call = part.get("function_call") or part.get("functionCall")
            elif hasattr(part, "function_call"):
                function_call = part.function_call

            if function_call:
                name = None
                args = {}

                if isinstance(function_call, dict):
                    name = function_call.get("name")
                    args = function_call.get("args", {})
                elif hasattr(function_call, "name"):
                    name = function_call.name
                    args = getattr(function_call, "args", {})

                if name:
                    calls.append(
                        SkillCall(
                            skill_name=name,
                            arguments=args if isinstance(args, dict) else dict(args),
                        )
                    )

        return calls

    def format_result(self, call: SkillCall, result: SkillResult) -> Dict[str, Any]:
        """Format result as Gemini function response"""
        response_data: Dict[str, Any]

        if result.status == SkillResultStatus.SUCCESS:
            response_data = {
                "result": result.output or "Success",
            }
            if result.data:
                response_data["data"] = result.data
        elif result.status == SkillResultStatus.DENIED:
            response_data = {
                "error": True,
                "error_type": "denied",
                "message": result.error or "Access denied",
            }
        else:
            response_data = {
                "error": True,
                "error_type": "error",
                "message": result.error or "Unknown error",
            }

        return {
            "function_response": {
                "name": call.skill_name,
                "response": response_data,
            }
        }

    def format_function_response_part(
        self,
        call: SkillCall,
        result: SkillResult,
    ) -> Dict[str, Any]:
        """Format as a content part for the conversation"""
        return self.format_result(call, result)
