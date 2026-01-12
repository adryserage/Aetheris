"""
Command Registry for CLI Interactive Mode (v3.0)

Manages command registration for built-in and provider-specific commands.
Supports autocomplete and command discovery.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Optional


class Provider(Enum):
    """Supported AI providers"""

    GEMINI = "gemini"
    CLAUDE = "claude"
    OPENAI = "openai"
    ALL = "all"  # Provider-agnostic commands


@dataclass
class CommandArgument:
    """Definition of a command argument"""

    name: str
    description: str
    required: bool = False
    default: Optional[str] = None
    choices: Optional[List[str]] = None


@dataclass
class Command:
    """Definition of a CLI command"""

    name: str
    description: str
    provider: Provider = Provider.ALL
    arguments: List[CommandArgument] = field(default_factory=list)
    handler: Optional[Callable] = None
    aliases: List[str] = field(default_factory=list)


class CommandRegistry:
    """Registry for CLI commands supporting multiple providers"""

    def __init__(self) -> None:
        self._commands: Dict[str, Command] = {}
        self._aliases: Dict[str, str] = {}  # alias -> command name
        self._register_builtin_commands()

    def _register_builtin_commands(self) -> None:
        """Register Aetheris built-in commands"""
        builtins = [
            Command(
                name="analysis",
                description="Run code analysis on the project",
                provider=Provider.ALL,
                arguments=[
                    CommandArgument(
                        "--preset",
                        "Use a predefined preset",
                        choices=[
                            "full",
                            "core",
                            "security-audit",
                            "performance-review",
                            "quick-scan",
                        ],
                    ),
                    CommandArgument("--agents", "Comma-separated list of agents to run"),
                    CommandArgument("--profile", "Safety profile", choices=["safe", "ci", "yolo"]),
                    CommandArgument("--timeout", "Analysis timeout (e.g., 30m, 2h)"),
                    CommandArgument("--reanalyze", "Only analyze changed files"),
                ],
                aliases=["analyze", "scan"],
            ),
            Command(
                name="fix",
                description="Apply fixes to identified issues",
                provider=Provider.ALL,
                arguments=[
                    CommandArgument("--auto", "Auto-apply fixes without confirmation"),
                    CommandArgument("--category", "Fix specific category only"),
                    CommandArgument("--analyze-first", "Run analysis before fixing"),
                ],
            ),
            Command(
                name="pr",
                description="Create analysis for pull request",
                provider=Provider.ALL,
                arguments=[
                    CommandArgument("--number", "PR number to analyze", required=True),
                ],
            ),
            Command(
                name="issues",
                description="Create GitHub issues from analysis",
                provider=Provider.ALL,
                arguments=[
                    CommandArgument("--dry-run", "Show issues without creating"),
                ],
            ),
            Command(
                name="stats",
                description="Show analysis statistics",
                provider=Provider.ALL,
            ),
            Command(
                name="settings",
                description="Open settings UI",
                provider=Provider.ALL,
            ),
            Command(
                name="help",
                description="Show available commands",
                provider=Provider.ALL,
                aliases=["?"],
            ),
            Command(
                name="exit",
                description="Exit interactive mode",
                provider=Provider.ALL,
                aliases=["quit", "q"],
            ),
            Command(
                name="clear",
                description="Clear the screen",
                provider=Provider.ALL,
                aliases=["cls"],
            ),
            Command(
                name="provider",
                description="Switch or show current AI provider",
                provider=Provider.ALL,
                arguments=[
                    CommandArgument(
                        "name", "Provider name", choices=["gemini", "claude", "openai"]
                    ),
                ],
            ),
        ]

        for cmd in builtins:
            self.register(cmd)

    def register(self, command: Command) -> None:
        """Register a command"""
        self._commands[command.name] = command
        for alias in command.aliases:
            self._aliases[alias] = command.name

    def register_claude_commands(self) -> None:
        """Register Claude Code CLI specific commands"""
        claude_commands = [
            Command(
                name="commit",
                description="Create a git commit with AI-generated message",
                provider=Provider.CLAUDE,
            ),
            Command(
                name="review",
                description="Review code changes",
                provider=Provider.CLAUDE,
            ),
            Command(
                name="explain",
                description="Explain code or error",
                provider=Provider.CLAUDE,
            ),
            Command(
                name="refactor",
                description="Suggest code refactoring",
                provider=Provider.CLAUDE,
            ),
            Command(
                name="test",
                description="Generate tests for code",
                provider=Provider.CLAUDE,
            ),
        ]

        for cmd in claude_commands:
            self.register(cmd)

    def register_gemini_commands(self) -> None:
        """Register Gemini CLI specific commands"""
        gemini_commands = [
            Command(
                name="chat",
                description="Start a chat session with Gemini",
                provider=Provider.GEMINI,
            ),
            Command(
                name="code",
                description="Generate code with Gemini",
                provider=Provider.GEMINI,
            ),
            Command(
                name="plan",
                description="Create execution plan with Conductor",
                provider=Provider.GEMINI,
            ),
        ]

        for cmd in gemini_commands:
            self.register(cmd)

    def get(self, name: str) -> Optional[Command]:
        """Get command by name or alias"""
        # Check direct name
        if name in self._commands:
            return self._commands[name]
        # Check aliases
        if name in self._aliases:
            return self._commands[self._aliases[name]]
        return None

    def get_commands(self, provider: Optional[Provider] = None) -> List[Command]:
        """Get all commands, optionally filtered by provider"""
        if provider is None:
            return list(self._commands.values())

        return [
            cmd
            for cmd in self._commands.values()
            if cmd.provider == Provider.ALL or cmd.provider == provider
        ]

    def get_command_names(self, provider: Optional[Provider] = None) -> List[str]:
        """Get all command names (including aliases) for autocomplete"""
        commands = self.get_commands(provider)
        names: List[str] = []
        for cmd in commands:
            names.append(cmd.name)
            names.extend(cmd.aliases)
        return sorted(names)
