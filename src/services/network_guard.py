"""
Network Guard for Safe Mode (v2.12)

Provides network access control for safe mode, blocking auxiliary network
calls while allowing AI provider connections.
"""

import socket
from contextlib import contextmanager
from typing import List, Optional, Set

from src.core.logger import log_print

# AI provider hosts that should always be allowed
ALLOWED_AI_HOSTS = {
    # Gemini / Google AI
    "generativelanguage.googleapis.com",
    "aiplatform.googleapis.com",
    "*.googleapis.com",
    # OpenAI
    "api.openai.com",
    # Anthropic / Claude
    "api.anthropic.com",
    # OpenRouter
    "openrouter.ai",
    "api.openrouter.ai",
}

# Additional allowed hosts for core functionality
ALLOWED_CORE_HOSTS = {
    # OSV vulnerability database
    "api.osv.dev",
    # PyPI for dependency info
    "pypi.org",
    "files.pythonhosted.org",
    # npm for dependency info
    "registry.npmjs.org",
}


class NetworkGuard:
    """
    Context manager for network access control in safe mode

    When enabled, blocks network connections to non-AI hosts by patching
    the socket module. AI provider connections are always allowed.
    """

    def __init__(
        self,
        enabled: bool = True,
        allow_ai: bool = True,
        allow_core: bool = True,
        additional_allowed: Optional[List[str]] = None,
    ):
        """
        Initialize network guard

        Args:
            enabled: Whether network blocking is enabled
            allow_ai: Allow AI provider connections
            allow_core: Allow core functionality connections (OSV, PyPI)
            additional_allowed: Additional hosts to allow
        """
        self.enabled = enabled
        self.allow_ai = allow_ai
        self.allow_core = allow_core
        self.additional_allowed = set(additional_allowed or [])
        self.blocked_connections: List[str] = []
        self._original_socket_connect = None
        self._original_getaddrinfo = None

    def _get_allowed_hosts(self) -> Set[str]:
        """Get the set of allowed hosts"""
        allowed = set()
        if self.allow_ai:
            allowed.update(ALLOWED_AI_HOSTS)
        if self.allow_core:
            allowed.update(ALLOWED_CORE_HOSTS)
        allowed.update(self.additional_allowed)
        return allowed

    def _is_host_allowed(self, host: str) -> bool:
        """Check if a host is allowed"""
        allowed = self._get_allowed_hosts()

        # Direct match
        if host in allowed:
            return True

        # Wildcard match (*.googleapis.com)
        for pattern in allowed:
            if pattern.startswith("*."):
                suffix = pattern[1:]  # .googleapis.com
                if host.endswith(suffix):
                    return True

        # Localhost is always allowed
        if host in ("localhost", "127.0.0.1", "::1"):
            return True

        return False

    def _create_blocking_connect(self, original_connect):
        """Create a patched connect function that blocks non-allowed hosts"""
        guard = self

        def blocking_connect(self_socket, address):
            try:
                host = address[0] if isinstance(address, tuple) else str(address)
                # Try to resolve the host name
                if not guard._is_host_allowed(host):
                    guard.blocked_connections.append(host)
                    log_print(f"🛡️  Safe mode blocked network connection to: {host}")
                    raise ConnectionRefusedError(f"Network access blocked by safe mode: {host}")
            except (IndexError, TypeError):
                pass
            return original_connect(self_socket, address)

        return blocking_connect

    def _create_blocking_getaddrinfo(self, original_getaddrinfo):
        """Create a patched getaddrinfo that blocks non-allowed hosts"""
        guard = self

        def blocking_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
            if not guard._is_host_allowed(host):
                guard.blocked_connections.append(host)
                log_print(f"🛡️  Safe mode blocked DNS lookup for: {host}")
                raise socket.gaierror(f"Network access blocked by safe mode: {host}")
            return original_getaddrinfo(host, port, family, type, proto, flags)

        return blocking_getaddrinfo

    def __enter__(self):
        if not self.enabled:
            return self

        # Store original functions
        self._original_socket_connect = socket.socket.connect
        self._original_getaddrinfo = socket.getaddrinfo

        # Apply patches
        socket.socket.connect = self._create_blocking_connect(self._original_socket_connect)
        socket.getaddrinfo = self._create_blocking_getaddrinfo(self._original_getaddrinfo)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.enabled:
            return

        # Restore original functions
        if self._original_socket_connect:
            socket.socket.connect = self._original_socket_connect
        if self._original_getaddrinfo:
            socket.getaddrinfo = self._original_getaddrinfo

        # Log blocked connections summary
        if self.blocked_connections:
            unique_blocked = set(self.blocked_connections)
            log_print(f"🛡️  Safe mode blocked {len(unique_blocked)} unique host(s)")

    def get_blocked_count(self) -> int:
        """Get count of blocked connection attempts"""
        return len(set(self.blocked_connections))


@contextmanager
def network_guard(
    profile_type: str,
    allow_ai: bool = True,
    allow_core: bool = True,
):
    """
    Convenience context manager for network guarding based on profile

    Args:
        profile_type: Safety profile type (safe, ci, yolo)
        allow_ai: Allow AI provider connections
        allow_core: Allow core functionality connections

    Yields:
        NetworkGuard instance
    """
    from src.core.profiles import ProfileType, get_profile_config

    profile = ProfileType.from_string(profile_type)
    config = get_profile_config(profile)

    # Network is blocked for auxiliary calls in safe mode
    enabled = not config.network_allowed

    guard = NetworkGuard(
        enabled=enabled,
        allow_ai=allow_ai,
        allow_core=allow_core,
    )

    with guard:
        yield guard


def is_network_allowed(profile_type: str) -> bool:
    """
    Check if auxiliary network access is allowed for the given profile

    Args:
        profile_type: Safety profile type

    Returns:
        True if network access is allowed
    """
    from src.core.profiles import ProfileType, get_profile_config

    profile = ProfileType.from_string(profile_type)
    config = get_profile_config(profile)
    return config.network_allowed
