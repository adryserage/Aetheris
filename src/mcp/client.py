"""
MCP Client for Aetheris (v3.0)

Handles connections to MCP servers via JSON-RPC over stdio.
"""

import asyncio
import json
import logging
import subprocess
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MCPConnectionError(Exception):
    """Error connecting to MCP server"""

    pass


@dataclass
class MCPCapabilities:
    """Capabilities reported by an MCP server"""

    tools: bool = False
    resources: bool = False
    prompts: bool = False
    logging: bool = False
    experimental: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MCPClient:
    """Client for communicating with MCP servers"""

    command: str
    args: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    connection_timeout: float = 2.0
    request_timeout: float = 30.0

    # Internal state
    _process: Optional[subprocess.Popen] = field(default=None, repr=False)
    _request_id: int = field(default=0, repr=False)
    _capabilities: Optional[MCPCapabilities] = field(default=None, repr=False)
    _connected: bool = field(default=False, repr=False)

    async def connect(self) -> bool:
        """
        Connect to the MCP server.

        Returns True if connection successful, False otherwise.
        Raises MCPConnectionError on timeout or connection failure.
        """
        try:
            # Spawn server process
            self._process = subprocess.Popen(
                [self.command] + self.args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={**dict(__import__("os").environ), **self.env},
            )

            # Send initialize request
            init_request = {
                "jsonrpc": "2.0",
                "id": self._next_id(),
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "aetheris",
                        "version": "3.0.0",
                    },
                },
            }

            response = await asyncio.wait_for(
                self._send_request(init_request),
                timeout=self.connection_timeout,
            )

            if "error" in response:
                raise MCPConnectionError(f"Initialize failed: {response['error']}")

            # Parse capabilities
            result = response.get("result", {})
            caps = result.get("capabilities", {})
            self._capabilities = MCPCapabilities(
                tools="tools" in caps,
                resources="resources" in caps,
                prompts="prompts" in caps,
                logging="logging" in caps,
                experimental=caps.get("experimental", {}),
            )

            # Send initialized notification
            await self._send_notification(
                {
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized",
                }
            )

            self._connected = True
            logger.info(f"Connected to MCP server: {self.command}")
            return True

        except asyncio.TimeoutError:
            self._cleanup()
            raise MCPConnectionError(f"Connection timeout after {self.connection_timeout}s")
        except Exception as e:
            self._cleanup()
            raise MCPConnectionError(f"Connection failed: {e}")

    async def disconnect(self) -> None:
        """Disconnect from the MCP server"""
        if self._connected:
            try:
                # Send shutdown request
                await self._send_request(
                    {
                        "jsonrpc": "2.0",
                        "id": self._next_id(),
                        "method": "shutdown",
                    }
                )
            except Exception:
                pass

        self._cleanup()
        self._connected = False

    def _cleanup(self) -> None:
        """Clean up process resources"""
        if self._process:
            try:
                self._process.terminate()
                self._process.wait(timeout=1)
            except Exception:
                try:
                    self._process.kill()
                except Exception:
                    pass
            self._process = None

    async def call_tool(
        self,
        name: str,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Call a tool on the MCP server"""
        if not self._connected:
            raise MCPConnectionError("Not connected")

        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": arguments,
            },
        }

        response = await asyncio.wait_for(
            self._send_request(request),
            timeout=self.request_timeout,
        )

        if "error" in response:
            return {"error": response["error"]}

        return response.get("result", {})

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools from the MCP server"""
        if not self._connected:
            return []

        if not self._capabilities or not self._capabilities.tools:
            return []

        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/list",
        }

        try:
            response = await asyncio.wait_for(
                self._send_request(request),
                timeout=self.request_timeout,
            )
            result = response.get("result", {})
            return result.get("tools", [])
        except Exception as e:
            logger.warning(f"Failed to list tools: {e}")
            return []

    async def list_resources(self) -> List[Dict[str, Any]]:
        """List available resources from the MCP server"""
        if not self._connected:
            return []

        if not self._capabilities or not self._capabilities.resources:
            return []

        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "resources/list",
        }

        try:
            response = await asyncio.wait_for(
                self._send_request(request),
                timeout=self.request_timeout,
            )
            result = response.get("result", {})
            return result.get("resources", [])
        except Exception as e:
            logger.warning(f"Failed to list resources: {e}")
            return []

    async def read_resource(self, uri: str) -> Optional[Dict[str, Any]]:
        """Read a resource from the MCP server"""
        if not self._connected:
            return None

        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "resources/read",
            "params": {"uri": uri},
        }

        try:
            response = await asyncio.wait_for(
                self._send_request(request),
                timeout=self.request_timeout,
            )
            if "error" in response:
                logger.warning(f"Failed to read resource {uri}: {response['error']}")
                return None
            return response.get("result")
        except Exception as e:
            logger.warning(f"Failed to read resource {uri}: {e}")
            return None

    @property
    def is_connected(self) -> bool:
        """Check if connected to server"""
        return self._connected

    @property
    def capabilities(self) -> Optional[MCPCapabilities]:
        """Get server capabilities"""
        return self._capabilities

    def _next_id(self) -> int:
        """Get next request ID"""
        self._request_id += 1
        return self._request_id

    async def _send_request(
        self,
        request: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Send JSON-RPC request and wait for response"""
        if not self._process or not self._process.stdin or not self._process.stdout:
            raise MCPConnectionError("Process not running")

        # Write request
        request_bytes = (json.dumps(request) + "\n").encode("utf-8")
        self._process.stdin.write(request_bytes)
        self._process.stdin.flush()

        # Read response
        loop = asyncio.get_event_loop()
        response_line = await loop.run_in_executor(
            None,
            self._process.stdout.readline,
        )

        if not response_line:
            raise MCPConnectionError("Server closed connection")

        return json.loads(response_line.decode("utf-8"))

    async def _send_notification(
        self,
        notification: Dict[str, Any],
    ) -> None:
        """Send JSON-RPC notification (no response expected)"""
        if not self._process or not self._process.stdin:
            return

        notification_bytes = (json.dumps(notification) + "\n").encode("utf-8")
        self._process.stdin.write(notification_bytes)
        self._process.stdin.flush()


async def connect_with_retry(
    client: MCPClient,
    max_retries: int = 3,
    base_delay: float = 1.0,
) -> bool:
    """
    Connect to MCP server with exponential backoff retry.

    Returns True if connected, False if all retries failed.
    """
    delay = base_delay

    for attempt in range(max_retries):
        try:
            return await client.connect()
        except MCPConnectionError as e:
            logger.warning(f"MCP connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(delay)
                delay *= 2

    return False
