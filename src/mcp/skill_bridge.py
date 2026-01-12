"""
MCP Tool Bridge for Aetheris (v3.0)

Bridges MCP tools to Aetheris Skill interface.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from src.mcp.client import MCPClient
from src.mcp.discovery import MCPDiscovery, MCPTool
from src.skills.base_skill import (
    Skill,
    SkillParameter,
    SkillResult,
    SkillResultStatus,
)

logger = logging.getLogger(__name__)


@dataclass
class MCPSkill(Skill):
    """A skill that wraps an MCP tool"""

    name: str = ""
    description: str = ""
    parameters: List[SkillParameter] = field(default_factory=list)
    requires_confirmation: bool = False

    # MCP-specific fields
    mcp_tool: Optional[MCPTool] = None
    mcp_discovery: Optional[MCPDiscovery] = None

    async def execute(self, arguments: Dict[str, Any]) -> SkillResult:
        """Execute the MCP tool"""
        if not self.mcp_tool or not self.mcp_discovery:
            return SkillResult(
                status=SkillResultStatus.ERROR,
                error="MCP tool not configured",
            )

        try:
            result = await self.mcp_discovery.call_tool(
                f"{self.mcp_tool.server_name}:{self.mcp_tool.name}",
                arguments,
            )

            if "error" in result:
                return SkillResult(
                    status=SkillResultStatus.ERROR,
                    error=str(result["error"]),
                )

            # Extract content from MCP response
            content = result.get("content", [])
            output_parts = []
            for item in content:
                if isinstance(item, dict):
                    if item.get("type") == "text":
                        output_parts.append(item.get("text", ""))
                    elif item.get("type") == "image":
                        output_parts.append(f"[Image: {item.get('mimeType', 'image')}]")
                    elif item.get("type") == "resource":
                        output_parts.append(f"[Resource: {item.get('uri', '')}]")
                elif isinstance(item, str):
                    output_parts.append(item)

            return SkillResult(
                status=SkillResultStatus.SUCCESS,
                output="\n".join(output_parts) if output_parts else "Success",
                data=result,
            )

        except Exception as e:
            logger.error(f"MCP tool execution failed: {e}")
            return SkillResult(
                status=SkillResultStatus.ERROR,
                error=str(e),
            )


class MCPToolBridge:
    """Bridges MCP tools to Aetheris Skills"""

    def __init__(
        self,
        discovery: MCPDiscovery,
        override_builtins: bool = False,
    ) -> None:
        self._discovery = discovery
        self._override_builtins = override_builtins
        self._builtin_names: List[str] = []

    def set_builtin_names(self, names: List[str]) -> None:
        """Set the list of built-in skill names for conflict detection"""
        self._builtin_names = names

    def tool_to_skill(self, tool: MCPTool) -> MCPSkill:
        """Convert an MCP tool to an Aetheris Skill"""
        # Parse input schema to parameters
        parameters = self._parse_input_schema(tool.input_schema)

        return MCPSkill(
            name=f"mcp:{tool.server_name}:{tool.name}",
            description=tool.description or f"MCP tool: {tool.name}",
            parameters=parameters,
            requires_confirmation=False,  # MCP tools don't require confirmation by default
            mcp_tool=tool,
            mcp_discovery=self._discovery,
        )

    def _parse_input_schema(
        self,
        schema: Dict[str, Any],
    ) -> List[SkillParameter]:
        """Parse JSON Schema to SkillParameters"""
        parameters: List[SkillParameter] = []

        if not schema or schema.get("type") != "object":
            return parameters

        properties = schema.get("properties", {})
        required = schema.get("required", [])

        for name, prop in properties.items():
            param_type = self._json_type_to_skill_type(prop.get("type", "string"))

            param = SkillParameter(
                name=name,
                description=prop.get("description", ""),
                param_type=param_type,
                required=name in required,
                default=prop.get("default"),
                enum=prop.get("enum"),
            )
            parameters.append(param)

        return parameters

    def _json_type_to_skill_type(self, json_type: str) -> str:
        """Convert JSON Schema type to skill parameter type"""
        type_mapping = {
            "string": "string",
            "integer": "integer",
            "number": "number",
            "boolean": "boolean",
            "array": "array",
            "object": "object",
        }
        return type_mapping.get(json_type, "string")

    def get_all_skills(self) -> List[MCPSkill]:
        """Get all MCP tools as skills"""
        skills: List[MCPSkill] = []

        for tool in self._discovery.list_tools():
            # Check for conflict with built-in
            if tool.name in self._builtin_names and not self._override_builtins:
                logger.debug(f"Skipping MCP tool {tool.name} due to conflict with built-in")
                continue

            skill = self.tool_to_skill(tool)
            skills.append(skill)

        return skills

    def get_skill(self, name: str) -> Optional[MCPSkill]:
        """Get a specific MCP tool as a skill"""
        # Handle different name formats
        # - Full: mcp:server:tool
        # - Qualified: server:tool
        # - Simple: tool

        tool = None

        if name.startswith("mcp:"):
            # Full format: mcp:server:tool
            parts = name.split(":", 2)
            if len(parts) == 3:
                qualified = f"{parts[1]}:{parts[2]}"
                tool = self._discovery.get_tool(qualified)
        elif ":" in name:
            # Qualified format: server:tool
            tool = self._discovery.get_tool(name)
        else:
            # Simple format: tool
            tool = self._discovery.get_tool(name)

        if tool:
            return self.tool_to_skill(tool)

        return None

    def get_conflicts(self) -> List[str]:
        """Get list of tool names that conflict with built-ins"""
        return self._discovery.has_tool_conflict(self._builtin_names)

    async def refresh(self) -> None:
        """Refresh MCP tool discovery"""
        await self._discovery.refresh_all()
