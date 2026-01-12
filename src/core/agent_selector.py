"""
Agent selection logic for selective analysis (v2.11)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from src.core.presets import get_preset, load_presets

# All available agents
CORE_AGENTS = [
    "code_analysis",
    "architecture",
    "security",
    "metrics",
    "vulnerability",
    "qa",
]

EXTENDED_AGENTS = [
    "type_safety",
    "performance",
    "api_contract",
    "data_privacy",
]

ALL_AGENTS = CORE_AGENTS + EXTENDED_AGENTS

# Agent aliases for convenience
AGENT_ALIASES = {
    "cae": "code_analysis",
    "aaa": "architecture",
    "ssa": "security",
    "cma": "metrics",
    "dva": "vulnerability",
    "qaa": "qa",
    "tsa": "type_safety",
    "paa": "performance",
    "aca": "api_contract",
    "dpa": "data_privacy",
}


@dataclass
class AgentSelectionResult:
    """Result of agent selection"""

    agents: List[str]
    compliance_frameworks: List[str]
    preset_used: Optional[str] = None
    errors: List[str] = field(default_factory=list)


class AgentSelector:
    """Handles agent selection logic for analysis"""

    def __init__(
        self,
        agents: Optional[str] = None,
        skip_agents: Optional[str] = None,
        preset: Optional[str] = None,
        compliance: Optional[str] = None,
    ):
        """
        Initialize agent selector

        Args:
            agents: Comma-separated list of agents to run (or 'all', 'core', 'none')
            skip_agents: Comma-separated list of agents to skip
            preset: Preset name to use
            compliance: Comma-separated list of compliance frameworks
        """
        self.agents_arg = agents
        self.skip_agents_arg = skip_agents
        self.preset_name = preset
        self.compliance_arg = compliance
        self._presets = load_presets()

    def parse_agents(self, agents_str: str) -> Set[str]:
        """
        Parse comma-separated agent list

        Args:
            agents_str: Comma-separated agent names

        Returns:
            Set of normalized agent names
        """
        agents = set()
        for agent in agents_str.split(","):
            agent = agent.strip().lower()
            if not agent:
                continue

            # Handle special values
            if agent == "all":
                agents.update(ALL_AGENTS)
            elif agent == "core":
                agents.update(CORE_AGENTS)
            elif agent == "extended":
                agents.update(EXTENDED_AGENTS)
            elif agent == "none":
                # Special value - returns empty set
                pass
            elif agent in AGENT_ALIASES:
                agents.add(AGENT_ALIASES[agent])
            elif agent in ALL_AGENTS:
                agents.add(agent)
            else:
                # Unknown agent - will be handled in validation
                agents.add(agent)

        return agents

    def validate_agents(self, agents: Set[str]) -> List[str]:
        """
        Validate agent names

        Args:
            agents: Set of agent names

        Returns:
            List of error messages for invalid agents
        """
        errors = []
        valid_agents = set(ALL_AGENTS)
        for agent in agents:
            if agent not in valid_agents:
                errors.append(
                    f"Unknown agent: '{agent}'. " f"Valid agents: {', '.join(sorted(ALL_AGENTS))}"
                )
        return errors

    def get_selected_agents(self) -> AgentSelectionResult:
        """
        Get the final list of selected agents

        Returns:
            AgentSelectionResult with selected agents and any errors
        """
        agents: Set[str] = set()
        errors: List[str] = []
        preset_used: Optional[str] = None
        compliance_frameworks: List[str] = []

        # Step 1: Start with preset if specified
        if self.preset_name:
            preset = get_preset(self.preset_name, self._presets)
            if preset:
                preset_used = preset.name
                if "all" in preset.agents:
                    agents.update(ALL_AGENTS)
                else:
                    agents.update(preset.agents)
                if preset.compliance_profile:
                    compliance_frameworks.append(preset.compliance_profile)
            else:
                errors.append(
                    f"Unknown preset: '{self.preset_name}'. "
                    f"Valid presets: {', '.join(sorted(self._presets.keys()))}"
                )

        # Step 2: Apply --agents (union with preset)
        if self.agents_arg:
            parsed = self.parse_agents(self.agents_arg)
            validation_errors = self.validate_agents(parsed)
            errors.extend(validation_errors)
            # Remove invalid agents
            valid_parsed = parsed - {a for a in parsed if a not in ALL_AGENTS}
            if preset_used:
                # Union with preset
                agents.update(valid_parsed)
            else:
                # Replace default
                agents = valid_parsed

        # Step 3: Handle 'none' special case
        if self.agents_arg and self.agents_arg.strip().lower() == "none":
            agents = set()
            # Check if compliance is provided
            if not self.compliance_arg:
                errors.append(
                    "--agents none requires --compliance to specify which compliance "
                    "frameworks to check. Example: --agents none --compliance gdpr"
                )

        # Step 4: Apply --skip-agents
        if self.skip_agents_arg:
            skip = self.parse_agents(self.skip_agents_arg)
            agents = agents - skip

        # Step 5: Default to all agents if nothing specified
        if not agents and not self.agents_arg and not self.preset_name:
            agents = set(ALL_AGENTS)

        # Step 6: Parse compliance frameworks
        if self.compliance_arg:
            for framework in self.compliance_arg.split(","):
                framework = framework.strip().lower()
                if framework:
                    compliance_frameworks.append(framework)
            # Ensure data_privacy agent is included for compliance
            if compliance_frameworks and "data_privacy" not in agents:
                agents.add("data_privacy")

        return AgentSelectionResult(
            agents=sorted(agents),
            compliance_frameworks=compliance_frameworks,
            preset_used=preset_used,
            errors=errors,
        )

    def get_agent_descriptions(self) -> Dict[str, str]:
        """Get descriptions for all agents"""
        return {
            "code_analysis": "Individual file analysis (Code Analysis Expert)",
            "architecture": "Architecture overview (Architect Analysis Agent)",
            "security": "Vulnerability detection (Security Analysis Agent)",
            "metrics": "Code metrics and complexity (Code Metrics Agent)",
            "vulnerability": "CVE scanning (Dependency Vulnerability Agent)",
            "qa": "Final synthesis (Quality Assurance Agent)",
            "type_safety": "Type safety issues (Type Safety Agent) - v2.10",
            "performance": "Performance anti-patterns (Performance Analysis Agent) - v2.10",
            "api_contract": "REST API violations (API Contract Agent) - v2.10",
            "data_privacy": "PII and compliance (Data Privacy Agent) - v2.10",
        }


def get_agent_help_text() -> str:
    """Get formatted help text for --agents option"""
    selector = AgentSelector()
    descriptions = selector.get_agent_descriptions()

    lines = [
        "Available agents:",
        "",
        "Core agents (6):",
    ]
    for agent in CORE_AGENTS:
        lines.append(f"  {agent}: {descriptions.get(agent, '')}")

    lines.extend(
        [
            "",
            "Extended agents (4) - v2.10+:",
        ]
    )
    for agent in EXTENDED_AGENTS:
        lines.append(f"  {agent}: {descriptions.get(agent, '')}")

    lines.extend(
        [
            "",
            "Special values:",
            "  all: Run all 10 agents (default)",
            "  core: Run only the 6 core agents",
            "  extended: Run only the 4 extended agents",
            "  none: Disable all agents (requires --compliance)",
            "",
            "Aliases:",
            "  CAE, AAA, SSA, CMA, DVA, QAA, TSA, PAA, ACA, DPA",
        ]
    )

    return "\n".join(lines)
