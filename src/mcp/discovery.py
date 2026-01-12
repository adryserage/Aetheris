"""
MCP Discovery for Aetheris (v3.0)

Discovers and manages tools and resources from MCP servers.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from src.mcp.client import MCPClient

logger = logging.getLogger(__name__)


@dataclass
class MCPTool:
    """Represents a tool from an MCP server"""

    name: str
    description: str
    input_schema: Dict[str, Any]
    server_name: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any], server_name: str) -> "MCPTool":
        """Create from MCP tool definition"""
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            input_schema=data.get("inputSchema", {}),
            server_name=server_name,
        )


@dataclass
class MCPResource:
    """Represents a resource from an MCP server"""

    uri: str
    name: str
    description: str
    mime_type: Optional[str]
    server_name: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any], server_name: str) -> "MCPResource":
        """Create from MCP resource definition"""
        return cls(
            uri=data.get("uri", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            mime_type=data.get("mimeType"),
            server_name=server_name,
        )


@dataclass
class MCPDiscovery:
    """Discovers and manages MCP tools and resources"""

    _clients: Dict[str, MCPClient] = field(default_factory=dict)
    _tools: Dict[str, MCPTool] = field(default_factory=dict)
    _resources: Dict[str, MCPResource] = field(default_factory=dict)

    async def add_server(
        self,
        name: str,
        client: MCPClient,
    ) -> bool:
        """
        Add an MCP server and discover its tools/resources.

        Returns True if server was added successfully.
        """
        if name in self._clients:
            logger.warning(f"Server {name} already registered")
            return False

        if not client.is_connected:
            try:
                await client.connect()
            except Exception as e:
                logger.error(f"Failed to connect to server {name}: {e}")
                return False

        self._clients[name] = client

        # Discover tools and resources
        await self._discover_server(name, client)

        return True

    async def remove_server(self, name: str) -> bool:
        """Remove an MCP server"""
        if name not in self._clients:
            return False

        client = self._clients.pop(name)
        await client.disconnect()

        # Remove tools and resources from this server
        self._tools = {k: v for k, v in self._tools.items() if v.server_name != name}
        self._resources = {k: v for k, v in self._resources.items() if v.server_name != name}

        return True

    async def _discover_server(
        self,
        name: str,
        client: MCPClient,
    ) -> None:
        """Discover tools and resources from a server"""
        # Discover tools
        tools = await client.list_tools()
        for tool_data in tools:
            tool = MCPTool.from_dict(tool_data, name)
            # Use qualified name to avoid conflicts
            qualified_name = f"{name}:{tool.name}"
            self._tools[qualified_name] = tool
            logger.debug(f"Discovered tool: {qualified_name}")

        # Discover resources
        resources = await client.list_resources()
        for resource_data in resources:
            resource = MCPResource.from_dict(resource_data, name)
            self._resources[resource.uri] = resource
            logger.debug(f"Discovered resource: {resource.uri}")

        logger.info(
            f"Discovered {len(tools)} tools and {len(resources)} resources " f"from server {name}"
        )

    async def refresh_server(self, name: str) -> bool:
        """Refresh tools and resources from a specific server"""
        if name not in self._clients:
            return False

        client = self._clients[name]

        # Remove old entries
        self._tools = {k: v for k, v in self._tools.items() if v.server_name != name}
        self._resources = {k: v for k, v in self._resources.items() if v.server_name != name}

        # Re-discover
        await self._discover_server(name, client)
        return True

    async def refresh_all(self) -> None:
        """Refresh all servers"""
        for name in list(self._clients.keys()):
            await self.refresh_server(name)

    def get_tool(self, name: str) -> Optional[MCPTool]:
        """Get a tool by name (qualified or unqualified)"""
        # Try qualified name first
        if name in self._tools:
            return self._tools[name]

        # Try to find unqualified
        for qualified, tool in self._tools.items():
            if tool.name == name:
                return tool

        return None

    def get_resource(self, uri: str) -> Optional[MCPResource]:
        """Get a resource by URI"""
        return self._resources.get(uri)

    def list_tools(self, server: Optional[str] = None) -> List[MCPTool]:
        """List all discovered tools, optionally filtered by server"""
        if server:
            return [t for t in self._tools.values() if t.server_name == server]
        return list(self._tools.values())

    def list_resources(self, server: Optional[str] = None) -> List[MCPResource]:
        """List all discovered resources, optionally filtered by server"""
        if server:
            return [r for r in self._resources.values() if r.server_name == server]
        return list(self._resources.values())

    def list_servers(self) -> List[str]:
        """List connected server names"""
        return list(self._clients.keys())

    async def call_tool(
        self,
        name: str,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Call a tool by name"""
        tool = self.get_tool(name)
        if not tool:
            return {"error": f"Tool not found: {name}"}

        client = self._clients.get(tool.server_name)
        if not client:
            return {"error": f"Server not connected: {tool.server_name}"}

        return await client.call_tool(tool.name, arguments)

    async def read_resource(self, uri: str) -> Optional[Dict[str, Any]]:
        """Read a resource by URI"""
        resource = self.get_resource(uri)
        if not resource:
            logger.warning(f"Resource not found: {uri}")
            return None

        client = self._clients.get(resource.server_name)
        if not client:
            logger.warning(f"Server not connected: {resource.server_name}")
            return None

        return await client.read_resource(uri)

    async def disconnect_all(self) -> None:
        """Disconnect from all servers"""
        for client in self._clients.values():
            try:
                await client.disconnect()
            except Exception as e:
                logger.warning(f"Error disconnecting: {e}")

        self._clients.clear()
        self._tools.clear()
        self._resources.clear()

    def has_tool_conflict(
        self,
        builtin_names: List[str],
    ) -> List[str]:
        """Check if any MCP tools conflict with built-in skill names"""
        conflicts = []
        for tool in self._tools.values():
            if tool.name in builtin_names:
                conflicts.append(tool.name)
        return conflicts
