"""Loads and validates the rule files (one YAML per agent) and defines the presets."""

from pathlib import Path
from typing import Any, cast, get_args

import yaml
from pydantic import BaseModel

from aetheris.checks import CHECK_NAMES
from aetheris.domain import AGENT_IDS, Agent, AgentId, Rule


class Preset(BaseModel, frozen=True):
    description: str
    agents: tuple[AgentId, ...]
    compliance_profile: str | None = None


def rules_dir() -> Path:
    return Path(__file__).parent / "rules"


def load_agents(directory: Path) -> dict[AgentId, Agent]:
    """Load every *.yaml in directory. Raises ValueError on a mismatch or a duplicate rule id."""
    agents: dict[AgentId, Agent] = {}
    rule_owner: dict[str, str] = {}
    files = sorted(directory.glob("*.yaml"))
    for file in files:
        data: dict[str, Any] = yaml.safe_load(file.read_text(encoding="utf-8")) or {}
        agent_id = data.get("agent")
        stem = file.name.removesuffix(".yaml")
        if agent_id != stem or agent_id not in get_args(AgentId):
            raise ValueError(f"{file.name}: 'agent' is {agent_id!r}, expected {stem!r}")
        agent_id = cast(AgentId, agent_id)
        rules = tuple(Rule(**raw) for raw in data.get("rules") or [])
        for rule in rules:
            if rule.id in rule_owner:
                raise ValueError(f"rule id {rule.id} is in {rule_owner[rule.id]} and {stem}")
            rule_owner[rule.id] = stem
        agents[agent_id] = Agent(
            id=agent_id,
            name=data["name"],
            summary=data["summary"],
            rules=rules,
            checks=CHECK_NAMES[agent_id],
        )
    return {a: agents[a] for a in AGENT_IDS if a in agents}


AGENTS: dict[AgentId, Agent] = load_agents(rules_dir())

PRESETS: dict[str, Preset] = {
    "full": Preset(description="All 10 agents", agents=AGENT_IDS),
    "core": Preset(
        description="The 6 core agents",
        agents=(
            "code_quality",
            "architecture",
            "security",
            "metrics",
            "dependency",
            "qa_synthesis",
        ),
    ),
    "security-audit": Preset(
        description="Security-focused review",
        agents=("security", "data_privacy", "dependency", "qa_synthesis"),
    ),
    "performance-review": Preset(
        description="Performance optimization review",
        agents=("performance", "metrics", "architecture", "qa_synthesis"),
    ),
    "quick-scan": Preset(
        description="Fast minimal review",
        agents=("code_quality", "security", "qa_synthesis"),
    ),
    "compliance-gdpr": Preset(
        description="GDPR compliance check",
        agents=("data_privacy", "qa_synthesis"),
        compliance_profile="gdpr",
    ),
    "compliance-hipaa": Preset(
        description="HIPAA compliance check",
        agents=("data_privacy", "qa_synthesis"),
        compliance_profile="hipaa",
    ),
    "compliance-pci": Preset(
        description="PCI-DSS compliance check",
        agents=("data_privacy", "qa_synthesis"),
        compliance_profile="pci_dss",
    ),
    "type-safety": Preset(
        description="Type safety review for TypeScript and Python",
        agents=("type_safety", "code_quality", "qa_synthesis"),
    ),
    "api-review": Preset(
        description="API contract and REST compliance",
        agents=("api_contract", "security", "qa_synthesis"),
    ),
}
