"""Data model shared by the registry, the checks and the MCP tools."""

from typing import Literal, get_args

from pydantic import BaseModel

AgentId = Literal[
    "security",
    "architecture",
    "code_quality",
    "metrics",
    "dependency",
    "qa_synthesis",
    "type_safety",
    "performance",
    "api_contract",
    "data_privacy",
]
Severity = Literal["critical", "high", "medium", "low", "info"]
PlaybookTask = Literal["analyze", "triage"]

AGENT_IDS: tuple[AgentId, ...] = get_args(AgentId)
SEVERITIES: tuple[Severity, ...] = get_args(Severity)

SEVERITY_PENALTY: dict[Severity, int] = {
    "critical": 15,
    "high": 8,
    "medium": 3,
    "low": 1,
    "info": 0,
}


def severity_rank(severity: Severity) -> int:
    """Lower is more severe."""
    return SEVERITIES.index(severity)


class Rule(BaseModel, frozen=True):
    id: str
    title: str
    severity: Severity
    check: str
    languages: tuple[str, ...] = ()
    references: tuple[str, ...] = ()


class Agent(BaseModel, frozen=True):
    id: AgentId
    name: str
    summary: str
    rules: tuple[Rule, ...]
    checks: tuple[str, ...]


class Playbook(BaseModel, frozen=True):
    """A review method adapted from a third-party source, served with its attribution."""

    id: str
    title: str
    agents: tuple[AgentId, ...]
    task: PlaybookTask
    languages: tuple[str, ...] = ()
    when: str
    source: str
    source_commit: str
    author: str
    license: str
    license_url: str
    changes: str
    steps: str


class Finding(BaseModel):
    agent: AgentId
    rule_id: str | None = None
    severity: Severity
    file: str | None = None
    line: int | None = None
    message: str
    evidence: str | None = None
    source: Literal["check", "assistant"] = "check"
