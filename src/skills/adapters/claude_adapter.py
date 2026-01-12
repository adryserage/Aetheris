"""
Claude Skill Adapter for Aetheris (v3.0)

Converts skills to Claude Tool Use format and parses responses.

Claude Tool Use format:
{
    "name": "skill_name",
    "description": "...",
    "input_schema": {
        "type": "object",
        "properties": {...},
        "required": [...]
    }
}
"""

from typing import Any, Dict, List, Optional

from src.skills.adapters.base_adapter import SkillAdapter
from src.skills.base_skill import Skill, SkillCall, SkillResult, SkillResultStatus


class ClaudeAdapter(SkillAdapter):
    """Adapter for Claude Tool Use format"""

    def to_api_format(self, skills: List[Skill]) -> List[Dict[str, Any]]:
        """Convert skills to Claude tool definitions"""
        tools: List[Dict[str, Any]] = []

        for skill in skills:
            tool = {
                "name": skill.name,
                "description": skill.description,
                "input_schema": self._build_input_schema(skill),
            }
            tools.append(tool)

        return tools

    def _build_input_schema(self, skill: Skill) -> Dict[str, Any]:
        """Build JSON Schema for skill parameters"""
        properties: Dict[str, Any] = {}
        required: List[str] = []

        for param in skill.parameters:
            prop: Dict[str, Any] = {
                "type": self._param_type_to_json_schema(param.param_type),
                "description": param.description,
            }

            if param.enum:
                prop["enum"] = param.enum

            if param.default is not None:
                prop["default"] = param.default

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

    def parse_response(self, response: Any) -> List[SkillCall]:
        """Parse Claude response to extract tool use blocks"""
        calls: List[SkillCall] = []

        # Handle different response formats
        if isinstance(response, dict):
            content = response.get("content", [])
        elif hasattr(response, "content"):
            content = response.content
        else:
            return calls

        # Extract tool_use blocks
        for block in content:
            if isinstance(block, dict):
                block_type = block.get("type")
                if block_type == "tool_use":
                    calls.append(
                        SkillCall(
                            skill_name=block.get("name", ""),
                            arguments=block.get("input", {}),
                            call_id=block.get("id"),
                        )
                    )
            elif hasattr(block, "type") and block.type == "tool_use":
                calls.append(
                    SkillCall(
                        skill_name=getattr(block, "name", ""),
                        arguments=getattr(block, "input", {}),
                        call_id=getattr(block, "id", None),
                    )
                )

        return calls

    def format_result(self, call: SkillCall, result: SkillResult) -> Dict[str, Any]:
        """Format result as Claude tool_result"""
        is_error = result.status != SkillResultStatus.SUCCESS

        content: str
        if result.status == SkillResultStatus.SUCCESS:
            content = result.output or "Success"
        elif result.status == SkillResultStatus.DENIED:
            content = f"DENIED: {result.error}"
        else:
            content = f"ERROR: {result.error}"

        tool_result: Dict[str, Any] = {
            "type": "tool_result",
            "tool_use_id": call.call_id or "",
            "content": content,
        }

        if is_error:
            tool_result["is_error"] = True

        return tool_result

    def format_tool_results_message(
        self,
        results: List[tuple[SkillCall, SkillResult]],
    ) -> Dict[str, Any]:
        """Format multiple results as a user message with tool_result blocks"""
        content: List[Dict[str, Any]] = []

        for call, result in results:
            content.append(self.format_result(call, result))

        return {
            "role": "user",
            "content": content,
        }
