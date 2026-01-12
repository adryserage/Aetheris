"""
Interactive Settings UI for Aetheris (v2.9)

Provides a Rich-based terminal interface for viewing and editing configuration.
"""

import sys
from typing import Any, Dict, List, Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.text import Text

from src.core.config_file import ConfigFile, ConfigHierarchy
from src.core.config_schema import ConfigSchema, get_default_config
from src.i18n import t


class SettingsUI:
    """
    Interactive settings UI using Rich

    Provides tabbed navigation through configuration categories:
    - AI Provider
    - Analysis
    - Safety
    - Presets
    - Output
    """

    CATEGORIES = [
        ("ai", "AI Provider", "Configure AI provider and model settings"),
        ("analysis", "Analysis", "Configure analysis behavior and agents"),
        ("safety", "Safety", "Configure safety profiles and allowlist"),
        ("presets", "Presets", "Manage analysis presets"),
        ("output", "Output", "Configure output format and directory"),
    ]

    def __init__(self, root_dir: str = ".", use_global: bool = False):
        self.root_dir = root_dir
        self.use_global = use_global
        self.console = Console()
        self.config_file = ConfigFile(root_dir)
        self.hierarchy = ConfigHierarchy(root_dir)
        self._modified = False

    def is_interactive(self) -> bool:
        """Check if running in interactive terminal"""
        return sys.stdin.isatty() and sys.stdout.isatty()

    def run(self) -> bool:
        """
        Run the interactive settings UI

        Returns:
            True if changes were saved, False otherwise
        """
        if not self.is_interactive():
            self.console.print(
                t(
                    "settings.not_interactive",
                    fallback="[yellow]Settings UI requires an interactive terminal.[/yellow]",
                )
            )
            self.console.print(
                t(
                    "settings.use_cli",
                    fallback="Use 'aetheris config <key> <value>' for non-interactive configuration.",
                )
            )
            return False

        # Load current configuration
        self.hierarchy.load()
        config = self.hierarchy.get_merged_config()
        if config is None:
            config = get_default_config()

        self._show_welcome()

        while True:
            category = self._select_category()
            if category is None:
                break

            self._edit_category(category, config)

        if self._modified:
            if Confirm.ask(
                t("settings.save_confirm", fallback="Save changes?"), default=True
            ):
                self._save_config(config)
                self.console.print(
                    t("settings.saved", fallback="[green]Configuration saved![/green]")
                )
                return True
            else:
                self.console.print(
                    t("settings.discarded", fallback="[yellow]Changes discarded.[/yellow]")
                )

        return False

    def _show_welcome(self) -> None:
        """Display welcome message"""
        scope = "global" if self.use_global else "local"
        config_path = (
            self.config_file.global_config_path
            if self.use_global
            else self.config_file.local_config_path
        )

        self.console.print()
        self.console.print(
            Panel(
                f"[bold]Aetheris Settings[/bold]\n\n"
                f"Editing: [cyan]{scope}[/cyan] configuration\n"
                f"Path: [dim]{config_path}[/dim]",
                title="⚙️ Settings",
                border_style="blue",
            )
        )
        self.console.print()

    def _select_category(self) -> Optional[str]:
        """Show category menu and get user selection"""
        table = Table(title="Configuration Categories", show_header=True)
        table.add_column("#", style="cyan", width=3)
        table.add_column("Category", style="bold")
        table.add_column("Description")

        for i, (key, name, desc) in enumerate(self.CATEGORIES, 1):
            table.add_row(str(i), name, desc)

        table.add_row("q", "[red]Quit[/red]", "Exit settings")

        self.console.print(table)
        self.console.print()

        choice = Prompt.ask(
            "Select category",
            choices=[str(i) for i in range(1, len(self.CATEGORIES) + 1)] + ["q", "Q"],
            default="q",
        )

        if choice.lower() == "q":
            return None

        idx = int(choice) - 1
        return self.CATEGORIES[idx][0]

    def _edit_category(self, category: str, config: ConfigSchema) -> None:
        """Edit settings in a category"""
        if category == "ai":
            self._edit_ai_settings(config)
        elif category == "analysis":
            self._edit_analysis_settings(config)
        elif category == "safety":
            self._edit_safety_settings(config)
        elif category == "presets":
            self._edit_presets(config)
        elif category == "output":
            self._edit_output_settings(config)

    def _edit_ai_settings(self, config: ConfigSchema) -> None:
        """Edit AI provider settings"""
        self.console.print()
        self.console.print("[bold]AI Provider Settings[/bold]")
        self.console.print()

        # Show current values with source
        table = Table(show_header=True)
        table.add_column("Setting", style="cyan")
        table.add_column("Current Value")
        table.add_column("Source", style="dim")

        settings = [
            ("provider", config.ai.provider),
            ("model", config.ai.model),
            ("timeout", str(config.ai.timeout)),
            ("max_retries", str(config.ai.max_retries)),
        ]

        for key, value in settings:
            source = self.hierarchy.get_value_source(f"ai.{key}")
            table.add_row(key, value, source.source)

        self.console.print(table)
        self.console.print()

        # Edit options
        new_provider = Prompt.ask("Provider", default=config.ai.provider)
        if new_provider != config.ai.provider:
            config.ai.provider = new_provider
            self._modified = True

        new_model = Prompt.ask("Model", default=config.ai.model)
        if new_model != config.ai.model:
            config.ai.model = new_model
            self._modified = True

        new_timeout = Prompt.ask("Timeout (seconds)", default=str(config.ai.timeout))
        try:
            timeout_int = int(new_timeout)
            if timeout_int != config.ai.timeout:
                config.ai.timeout = timeout_int
                self._modified = True
        except ValueError:
            self.console.print("[red]Invalid timeout value[/red]")

        new_retries = Prompt.ask("Max retries", default=str(config.ai.max_retries))
        try:
            retries_int = int(new_retries)
            if retries_int != config.ai.max_retries:
                config.ai.max_retries = retries_int
                self._modified = True
        except ValueError:
            self.console.print("[red]Invalid retries value[/red]")

    def _edit_analysis_settings(self, config: ConfigSchema) -> None:
        """Edit analysis settings"""
        self.console.print()
        self.console.print("[bold]Analysis Settings[/bold]")
        self.console.print()

        # Show current values
        table = Table(show_header=True)
        table.add_column("Setting", style="cyan")
        table.add_column("Current Value")

        table.add_row("default_preset", config.analysis.default_preset)
        table.add_row("enabled_agents", ", ".join(config.analysis.enabled_agents))
        table.add_row("skip_agents", ", ".join(config.analysis.skip_agents) or "(none)")
        table.add_row("enable_cache", str(config.analysis.enable_cache))
        table.add_row("max_dependency_depth", str(config.analysis.max_dependency_depth))

        self.console.print(table)
        self.console.print()

        # Edit key options
        new_preset = Prompt.ask("Default preset", default=config.analysis.default_preset)
        if new_preset != config.analysis.default_preset:
            config.analysis.default_preset = new_preset
            self._modified = True

        new_cache = Confirm.ask("Enable cache?", default=config.analysis.enable_cache)
        if new_cache != config.analysis.enable_cache:
            config.analysis.enable_cache = new_cache
            self._modified = True

    def _edit_safety_settings(self, config: ConfigSchema) -> None:
        """Edit safety settings"""
        self.console.print()
        self.console.print("[bold]Safety Settings[/bold]")
        self.console.print()

        table = Table(show_header=True)
        table.add_column("Setting", style="cyan")
        table.add_column("Current Value")

        table.add_row("default_profile", config.safety.default_profile)
        table.add_row("audit_log_path", config.safety.audit_log_path)
        table.add_row("custom_allowlist", str(len(config.safety.custom_allowlist)) + " items")

        self.console.print(table)
        self.console.print()

        new_profile = Prompt.ask(
            "Default profile [safe/ci/yolo]",
            default=config.safety.default_profile,
            choices=["safe", "ci", "yolo"],
        )
        if new_profile != config.safety.default_profile:
            config.safety.default_profile = new_profile
            self._modified = True

    def _edit_presets(self, config: ConfigSchema) -> None:
        """Edit or view presets"""
        self.console.print()
        self.console.print("[bold]Analysis Presets[/bold]")
        self.console.print()

        if not config.presets:
            self.console.print("[dim]No custom presets defined.[/dim]")
        else:
            table = Table(show_header=True)
            table.add_column("Name", style="cyan")
            table.add_column("Description")
            table.add_column("Agents")

            for name, preset in config.presets.items():
                table.add_row(name, preset.description, ", ".join(preset.agents))

            self.console.print(table)

        self.console.print()
        self.console.print("[dim]Use 'aetheris config' CLI to manage presets.[/dim]")

    def _edit_output_settings(self, config: ConfigSchema) -> None:
        """Edit output settings"""
        self.console.print()
        self.console.print("[bold]Output Settings[/bold]")
        self.console.print()

        table = Table(show_header=True)
        table.add_column("Setting", style="cyan")
        table.add_column("Current Value")

        table.add_row("format", config.output.format)
        table.add_row("directory", config.output.directory)
        table.add_row("architecture_report_path", config.output.architecture_report_path)

        self.console.print(table)
        self.console.print()

        new_format = Prompt.ask(
            "Output format",
            default=config.output.format,
            choices=["markdown", "json", "html"],
        )
        if new_format != config.output.format:
            config.output.format = new_format
            self._modified = True

        new_dir = Prompt.ask("Output directory", default=config.output.directory)
        if new_dir != config.output.directory:
            config.output.directory = new_dir
            self._modified = True

    def _save_config(self, config: ConfigSchema) -> None:
        """Save configuration to file"""
        config_dict = config.to_dict()

        if self.use_global:
            self.config_file.save_global_config(config_dict)
        else:
            self.config_file.save_local_config(config_dict)


def run_settings_ui(root_dir: str = ".", use_global: bool = False) -> bool:
    """
    Run the interactive settings UI

    Args:
        root_dir: Project root directory
        use_global: Edit global config instead of local

    Returns:
        True if changes were saved
    """
    ui = SettingsUI(root_dir, use_global)
    return ui.run()
