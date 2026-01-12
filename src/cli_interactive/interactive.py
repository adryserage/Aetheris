"""
Interactive Session for CLI Interactive Mode (v3.0)

Provides the main REPL interface with:
- Provider-aware prompt
- Command parsing and execution
- Graceful exit handling
- History support
"""

import os
import shlex
import subprocess
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.cli_interactive.autocomplete import CommandCompleter
from src.cli_interactive.command_registry import Command, CommandRegistry, Provider
from src.core.config import load_env_file


@dataclass
class SessionState:
    """State for the interactive session"""

    provider: Provider = Provider.GEMINI
    running: bool = True
    last_result: Optional[str] = None
    history: List[str] = field(default_factory=list)


class InteractiveSession:
    """Interactive REPL session for Aetheris"""

    def __init__(
        self,
        initial_provider: Optional[str] = None,
        history_file: Optional[str] = None,
    ) -> None:
        self.console = Console()
        self.registry = CommandRegistry()
        self.state = SessionState()

        # Set initial provider
        if initial_provider:
            self.state.provider = Provider(initial_provider.lower())

        # Register provider-specific commands
        self.registry.register_claude_commands()
        self.registry.register_gemini_commands()

        # Setup autocomplete
        self.completer = CommandCompleter(self.registry, self.state.provider)

        # Setup prompt session with history
        history_path = history_file or os.path.expanduser("~/.aetheris_history")
        self.prompt_session: PromptSession = PromptSession(
            history=FileHistory(history_path),
            completer=self.completer,
            style=self._get_prompt_style(),
        )

        # Command handlers
        self._handlers: Dict[str, Callable] = {
            "exit": self._handle_exit,
            "quit": self._handle_exit,
            "q": self._handle_exit,
            "help": self._handle_help,
            "?": self._handle_help,
            "clear": self._handle_clear,
            "cls": self._handle_clear,
            "provider": self._handle_provider,
            "analysis": self._handle_analysis,
            "analyze": self._handle_analysis,
            "scan": self._handle_analysis,
            "fix": self._handle_fix,
            "stats": self._handle_stats,
            "settings": self._handle_settings,
        }

    def _get_prompt_style(self) -> Style:
        """Get prompt style"""
        return Style.from_dict(
            {
                "prompt": "ansicyan bold",
                "provider": "ansigreen",
            }
        )

    def _get_prompt(self) -> str:
        """Generate prompt with current provider"""
        provider_name = self.state.provider.value
        return f"aetheris[{provider_name}]> "

    def run(self) -> None:
        """Run the interactive session"""
        self._show_welcome()

        while self.state.running:
            try:
                # Get input with autocomplete
                user_input = self.prompt_session.prompt(self._get_prompt())

                if not user_input.strip():
                    continue

                # Parse and execute
                self._execute(user_input.strip())

            except KeyboardInterrupt:
                self.console.print("\n[dim]Use /exit to quit[/dim]")
            except EOFError:
                self._handle_exit([])

        self._show_goodbye()

    def _show_welcome(self) -> None:
        """Display welcome message"""
        load_env_file()

        panel = Panel(
            f"[bold cyan]Aetheris Interactive Mode[/bold cyan]\n\n"
            f"Current provider: [green]{self.state.provider.value}[/green]\n"
            f"Type [bold]/help[/bold] for available commands\n"
            f"Type [bold]/exit[/bold] to quit\n\n"
            f"[dim]Tab for autocomplete • Ctrl+C to cancel • Ctrl+D to exit[/dim]",
            title="Welcome",
            border_style="cyan",
        )
        self.console.print(panel)

    def _show_goodbye(self) -> None:
        """Display goodbye message"""
        self.console.print("\n[dim]Goodbye![/dim]")

    def _execute(self, user_input: str) -> None:
        """Parse and execute user input"""
        # Check if it's a command (starts with /)
        if user_input.startswith("/"):
            self._execute_command(user_input[1:])
        else:
            # Natural language query - send to AI
            self._execute_query(user_input)

    def _execute_command(self, command_str: str) -> None:
        """Execute a /command"""
        try:
            parts = shlex.split(command_str)
        except ValueError as e:
            self.console.print(f"[red]Parse error: {e}[/red]")
            return

        if not parts:
            return

        command_name = parts[0].lower()
        args = parts[1:]

        # Check if command exists
        cmd = self.registry.get(command_name)
        if not cmd:
            # Suggest similar commands
            suggestions = self.completer.suggest_similar(command_name)
            self.console.print(f"[red]Unknown command: /{command_name}[/red]")
            if suggestions:
                self.console.print(f"[dim]Did you mean: /{', /'.join(suggestions)}?[/dim]")
            return

        # Check provider compatibility
        if cmd.provider != Provider.ALL and cmd.provider != self.state.provider:
            self.console.print(
                f"[yellow]/{cmd.name} is only available with {cmd.provider.value} provider[/yellow]"
            )
            return

        # Execute handler
        if command_name in self._handlers:
            self._handlers[command_name](args)
        else:
            # Pass through to underlying CLI
            self._passthrough_command(cmd, args)

    def _execute_query(self, query: str) -> None:
        """Execute a natural language query"""
        self.console.print(f"[dim]Processing query with {self.state.provider.value}...[/dim]")
        # TODO: Implement AI query processing
        self.console.print("[yellow]Natural language queries not yet implemented[/yellow]")

    def _passthrough_command(self, cmd: Command, args: List[str]) -> None:
        """Pass command through to underlying provider CLI"""
        self.console.print(f"[dim]Passing /{cmd.name} to {self.state.provider.value} CLI...[/dim]")
        # TODO: Implement passthrough to provider CLIs
        self.console.print("[yellow]Command passthrough not yet implemented[/yellow]")

    # Command handlers

    def _handle_exit(self, args: List[str]) -> None:
        """Handle /exit command"""
        self.state.running = False

    def _handle_help(self, args: List[str]) -> None:
        """Handle /help command"""
        table = Table(title="Available Commands", show_header=True)
        table.add_column("Command", style="cyan")
        table.add_column("Description")
        table.add_column("Provider", style="dim")

        commands = self.registry.get_commands()
        # Sort: ALL first, then by name
        commands.sort(key=lambda c: (c.provider != Provider.ALL, c.name))

        for cmd in commands:
            provider = cmd.provider.value if cmd.provider != Provider.ALL else "all"
            aliases = f" ({', '.join(cmd.aliases)})" if cmd.aliases else ""
            table.add_row(f"/{cmd.name}{aliases}", cmd.description, provider)

        self.console.print(table)

    def _handle_clear(self, args: List[str]) -> None:
        """Handle /clear command - clears the terminal screen"""
        # Use subprocess with fixed command for security (no user input in command)
        clear_cmd = "cls" if os.name == "nt" else "clear"
        subprocess.run([clear_cmd], shell=True, check=False)

    def _handle_provider(self, args: List[str]) -> None:
        """Handle /provider command"""
        if not args:
            self.console.print(f"Current provider: [green]{self.state.provider.value}[/green]")
            self.console.print("[dim]Available: gemini, claude, openai[/dim]")
            return

        provider_name = args[0].lower()
        try:
            new_provider = Provider(provider_name)
            if new_provider == Provider.ALL:
                self.console.print("[red]Invalid provider name[/red]")
                return
            self.state.provider = new_provider
            self.completer.set_provider(new_provider)
            self.console.print(f"Switched to [green]{provider_name}[/green] provider")
        except ValueError:
            self.console.print(f"[red]Unknown provider: {provider_name}[/red]")
            self.console.print("[dim]Available: gemini, claude, openai[/dim]")

    def _handle_analysis(self, args: List[str]) -> None:
        """Handle /analysis command"""
        # Parse arguments
        preset = None
        agents = None
        profile = "safe"
        timeout = None
        reanalyze = False

        i = 0
        while i < len(args):
            if args[i] == "--preset" and i + 1 < len(args):
                preset = args[i + 1]
                i += 2
            elif args[i] == "--agents" and i + 1 < len(args):
                agents = args[i + 1]
                i += 2
            elif args[i] == "--profile" and i + 1 < len(args):
                profile = args[i + 1]
                i += 2
            elif args[i] == "--timeout" and i + 1 < len(args):
                timeout = args[i + 1]
                i += 2
            elif args[i] in ("--reanalyze", "-r"):
                reanalyze = True
                i += 1
            else:
                i += 1

        self.console.print("[cyan]Starting analysis...[/cyan]")
        self.console.print(f"  Preset: {preset or 'default'}")
        self.console.print(f"  Profile: {profile}")
        if agents:
            self.console.print(f"  Agents: {agents}")
        if timeout:
            self.console.print(f"  Timeout: {timeout}")
        if reanalyze:
            self.console.print("  Mode: reanalyze changed files only")

        # TODO: Call actual analysis
        self.console.print("[yellow]Full analysis execution not yet implemented[/yellow]")

    def _handle_fix(self, args: List[str]) -> None:
        """Handle /fix command"""
        auto = "--auto" in args
        category = None
        analyze_first = "--analyze-first" in args

        for i, arg in enumerate(args):
            if arg == "--category" and i + 1 < len(args):
                category = args[i + 1]

        self.console.print("[cyan]Starting fix process...[/cyan]")
        self.console.print(f"  Auto: {auto}")
        if category:
            self.console.print(f"  Category: {category}")
        if analyze_first:
            self.console.print("  Will analyze first")

        # TODO: Call actual fix
        self.console.print("[yellow]Fix execution not yet implemented[/yellow]")

    def _handle_stats(self, args: List[str]) -> None:
        """Handle /stats command"""
        self.console.print("[cyan]Fetching statistics...[/cyan]")
        # TODO: Call actual stats
        self.console.print("[yellow]Stats display not yet implemented[/yellow]")

    def _handle_settings(self, args: List[str]) -> None:
        """Handle /settings command"""
        self.console.print("[cyan]Opening settings...[/cyan]")
        # TODO: Launch settings UI
        self.console.print("[yellow]Settings UI not yet implemented in interactive mode[/yellow]")
