"""
Interactive agent selection with Rich UI (v2.11)
"""

import sys
from typing import List, Optional, Set

from src.core.agent_selector import (
    ALL_AGENTS,
    CORE_AGENTS,
    EXTENDED_AGENTS,
    AgentSelector,
)
from src.core.presets import get_preset, list_presets


class InteractiveAgentSelector:
    """Interactive UI for agent selection using Rich"""

    def __init__(
        self,
        preset: Optional[str] = None,
        compliance: Optional[str] = None,
    ):
        """
        Initialize interactive selector

        Args:
            preset: Pre-select agents from this preset
            compliance: Pre-select compliance frameworks
        """
        self.preset = preset
        self.compliance = compliance
        self._selected_agents: Set[str] = set()
        self._selected_compliance: Set[str] = set()

    def _check_interactive_support(self) -> bool:
        """Check if terminal supports interactive mode"""
        return sys.stdin.isatty() and sys.stdout.isatty()

    def _get_agent_descriptions(self) -> dict:
        """Get agent descriptions"""
        return AgentSelector().get_agent_descriptions()

    def run(self) -> tuple:
        """
        Run interactive selection

        Returns:
            Tuple of (selected_agents, selected_compliance)
        """
        if not self._check_interactive_support():
            print("Warning: Non-interactive terminal detected. Using default agents.")
            return list(ALL_AGENTS), []

        try:
            from rich.console import Console
            from rich.panel import Panel
            from rich.prompt import Confirm, Prompt
            from rich.table import Table
        except ImportError:
            print("Warning: Rich library not available. Using default agents.")
            return list(ALL_AGENTS), []

        console = Console()

        # Display header
        console.print(
            Panel.fit(
                "[bold blue]Aetheris Agent Selection[/bold blue]\n"
                "Select which AI agents to run for your analysis.",
                border_style="blue",
            )
        )

        # Show available presets
        console.print("\n[bold]Available Presets:[/bold]")
        presets = list_presets()
        preset_table = Table(show_header=True, header_style="bold cyan")
        preset_table.add_column("Preset", style="green")
        preset_table.add_column("Description")
        preset_table.add_column("Agents")

        for p in presets:
            agents_str = ", ".join(p.agents[:3])
            if len(p.agents) > 3:
                agents_str += f" (+{len(p.agents) - 3})"
            preset_table.add_row(p.name, p.description, agents_str)

        console.print(preset_table)

        # Ask for preset
        console.print()
        use_preset = Confirm.ask("Would you like to use a preset?", default=False)

        if use_preset:
            preset_names = [p.name for p in presets]
            preset_name = Prompt.ask(
                "Enter preset name",
                choices=preset_names,
                default="full",
            )
            preset = get_preset(preset_name)
            if preset:
                self._selected_agents = set(ALL_AGENTS if "all" in preset.agents else preset.agents)
                if preset.compliance_profile:
                    self._selected_compliance.add(preset.compliance_profile)
                console.print(f"[green]Using preset: {preset_name}[/green]")
        else:
            # Manual selection
            console.print("\n[bold]Core Agents (6):[/bold]")
            self._select_agents_group(console, CORE_AGENTS)

            console.print("\n[bold]Extended Agents (4) - v2.10+:[/bold]")
            self._select_agents_group(console, EXTENDED_AGENTS)

        # Compliance selection
        if "data_privacy" in self._selected_agents:
            console.print("\n[bold]Compliance Frameworks:[/bold]")
            frameworks = ["gdpr", "hipaa", "pci_dss", "ccpa"]
            for framework in frameworks:
                if Confirm.ask(f"  Enable {framework.upper()}?", default=False):
                    self._selected_compliance.add(framework)

        # Summary
        console.print("\n[bold]Selected Configuration:[/bold]")
        console.print(f"  Agents: {', '.join(sorted(self._selected_agents)) or 'none'}")
        if self._selected_compliance:
            console.print(f"  Compliance: {', '.join(sorted(self._selected_compliance))}")

        if Confirm.ask("\nProceed with this configuration?", default=True):
            return list(self._selected_agents), list(self._selected_compliance)
        else:
            console.print("[yellow]Selection cancelled.[/yellow]")
            return [], []

    def _select_agents_group(self, console, agents: List[str]) -> None:
        """Select agents from a group"""
        try:
            from rich.prompt import Confirm
        except ImportError:
            return

        descriptions = self._get_agent_descriptions()
        for agent in agents:
            desc = descriptions.get(agent, "")
            if Confirm.ask(f"  [{agent}] {desc}?", default=True):
                self._selected_agents.add(agent)


def run_interactive_selection(
    preset: Optional[str] = None,
    compliance: Optional[str] = None,
) -> tuple:
    """
    Run interactive agent selection

    Args:
        preset: Pre-select agents from this preset
        compliance: Pre-select compliance frameworks

    Returns:
        Tuple of (selected_agents, selected_compliance)
    """
    selector = InteractiveAgentSelector(preset=preset, compliance=compliance)
    return selector.run()
