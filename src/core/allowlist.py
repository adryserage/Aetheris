"""
Command Allowlist for Safe Mode (v2.12)

Validates commands against an allowlist to prevent unsafe operations in safe mode.
Supports glob patterns for flexible matching.
"""

import fnmatch
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from src.core.logger import log_print


@dataclass
class AllowlistConfig:
    """Command allowlist configuration for safe mode"""

    version: str = "1.0"
    patterns: List[str] = field(default_factory=list)
    exact: List[str] = field(default_factory=list)
    blocked_patterns: List[str] = field(default_factory=list)
    user_additions: List[str] = field(default_factory=list)

    def is_allowed(self, command: str) -> bool:
        """
        Check if command matches allowlist

        Args:
            command: Command string to validate

        Returns:
            True if command is allowed
        """
        command = command.strip()

        # First check if command matches any blocked pattern
        for blocked in self.blocked_patterns:
            if fnmatch.fnmatch(command, blocked):
                return False

        # Check exact matches first (faster)
        if command in self.exact:
            return True

        # Check user additions
        for pattern in self.user_additions:
            if fnmatch.fnmatch(command, pattern):
                return True

        # Check glob patterns
        for pattern in self.patterns:
            if fnmatch.fnmatch(command, pattern):
                return True

        return False

    def get_reason(self, command: str) -> str:
        """
        Get reason for allowing or blocking a command

        Args:
            command: Command to check

        Returns:
            Human-readable reason
        """
        command = command.strip()

        # Check blocked patterns
        for blocked in self.blocked_patterns:
            if fnmatch.fnmatch(command, blocked):
                return f"Command matches blocked pattern: {blocked}"

        # Check exact matches
        if command in self.exact:
            return "Command is in exact allowlist"

        # Check user additions
        for pattern in self.user_additions:
            if fnmatch.fnmatch(command, pattern):
                return f"Command matches user-added pattern: {pattern}"

        # Check glob patterns
        for pattern in self.patterns:
            if fnmatch.fnmatch(command, pattern):
                return f"Command matches allowlist pattern: {pattern}"

        return "Command not in allowlist"


def get_default_allowlist_path() -> Path:
    """Get path to default allowlist JSON file"""
    # First try package config directory
    package_path = Path(__file__).parent.parent.parent / "config" / "default_allowlist.json"
    if package_path.exists():
        return package_path

    # Fallback to current working directory
    cwd_path = Path.cwd() / "config" / "default_allowlist.json"
    if cwd_path.exists():
        return cwd_path

    return package_path  # Return default even if doesn't exist


def load_allowlist(
    custom_patterns: Optional[List[str]] = None,
    allowlist_path: Optional[Path] = None,
) -> AllowlistConfig:
    """
    Load allowlist from default file and merge with user customizations

    Args:
        custom_patterns: Additional patterns from config.json
        allowlist_path: Optional path to custom allowlist file

    Returns:
        AllowlistConfig with merged patterns
    """
    config = AllowlistConfig()

    # Load default allowlist
    default_path = allowlist_path or get_default_allowlist_path()
    if default_path.exists():
        try:
            with open(default_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                config.version = data.get("version", "1.0")
                config.patterns = data.get("patterns", [])
                config.exact = data.get("exact", [])
                config.blocked_patterns = data.get("blocked_patterns", [])
        except (json.JSONDecodeError, IOError) as e:
            log_print(f"⚠️  Warning: Could not load allowlist from {default_path}: {e}")
            log_print("   Using empty allowlist (all commands blocked in safe mode)")
    else:
        log_print(f"⚠️  Warning: Allowlist file not found at {default_path}")
        log_print("   Using empty allowlist (all commands blocked in safe mode)")
        # Provide minimal safe defaults
        config.patterns = [
            "git *",
            "pytest *",
            "python -m pytest *",
        ]
        config.exact = [
            "git status",
            "git diff",
            "git log",
        ]

    # Add user customizations
    if custom_patterns:
        config.user_additions = custom_patterns

    return config


def validate_command(
    command: str,
    allowlist: AllowlistConfig,
    log_blocked: bool = True,
) -> tuple:
    """
    Validate a command against the allowlist

    Args:
        command: Command to validate
        allowlist: AllowlistConfig to check against
        log_blocked: Whether to log blocked commands

    Returns:
        Tuple of (is_allowed: bool, reason: str)
    """
    is_allowed = allowlist.is_allowed(command)
    reason = allowlist.get_reason(command)

    if not is_allowed and log_blocked:
        log_print(f"🛡️  Safe mode blocked command: {command}")
        log_print(f"   Reason: {reason}")

    return (is_allowed, reason)


class AllowlistGuard:
    """Context manager for command validation in safe mode"""

    def __init__(
        self,
        enabled: bool = True,
        custom_patterns: Optional[List[str]] = None,
    ):
        """
        Initialize allowlist guard

        Args:
            enabled: Whether allowlist enforcement is enabled
            custom_patterns: Additional patterns from config.json
        """
        self.enabled = enabled
        self.allowlist = load_allowlist(custom_patterns) if enabled else None
        self.blocked_commands: List[str] = []

    def check(self, command: str) -> bool:
        """
        Check if command is allowed

        Args:
            command: Command to check

        Returns:
            True if allowed (or guard disabled)
        """
        if not self.enabled or self.allowlist is None:
            return True

        is_allowed, reason = validate_command(command, self.allowlist)
        if not is_allowed:
            self.blocked_commands.append(command)
        return is_allowed

    def get_blocked_count(self) -> int:
        """Get count of blocked commands"""
        return len(self.blocked_commands)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
