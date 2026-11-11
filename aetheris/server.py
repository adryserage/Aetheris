"""MCP server (stdio). Five tools that drive a code review; no AI API is ever called."""

import functools
import json
import logging
import sys
from collections import Counter
from collections.abc import Callable
from typing import Any, Literal

from mcp.server.fastmcp import FastMCP

from aetheris import __version__, registry
from aetheris.changes import changed_files
from aetheris.checks import CHECKS, CheckContext
from aetheris.domain import AGENT_IDS, AgentId, Finding, severity_rank
from aetheris.files import (
    MAX_FILES,
    is_manifest,
    language_of,
    project_root,
    select_files,
)
from aetheris.synthesis import synthesize

MAX_FINDINGS = 200
log = logging.getLogger("aetheris")

NEXT_STEPS = (
    "For each agent listed: 1) call get_rules(agent) and read the rules; 2) call "
    "run_checks(agent, paths) to get deterministic findings; 3) read the listed files and judge "
    "them against the rules, adding your own findings (source='assistant', same schema as "
    "the Finding schema returned by get_rules). Finish with synthesize_report(findings) on all "
    "findings together, and report its score and top findings. Review qa_synthesis last."
)

_CODE_REASONS: dict[AgentId, str] = {
    "security": "secrets and unsafe code patterns apply to any code",
    "code_quality": "code files are in scope",
    "metrics": "code files are in scope",
    "architecture": "several code files may import each other",
    "data_privacy": "code files may handle personal data",
    "performance": "code files are in scope",
}


def _select_agents(
    files: list[str], preset: str | None, agents: list[AgentId] | None
) -> list[dict[str, str]]:
    if agents:
        return [{"id": a, "reason": "requested explicitly"} for a in _ordered(agents)]
    if preset:
        if preset not in registry.PRESETS:
            raise ValueError(f"unknown preset {preset!r}; known: {sorted(registry.PRESETS)}")
        ids = _ordered(registry.PRESETS[preset].agents)
        return [{"id": a, "reason": f"preset {preset}"} for a in ids]
    languages = {language_of(f) for f in files} - {None}
    chosen: dict[AgentId, str] = {}
    if languages:
        chosen.update(_CODE_REASONS)
    if any(is_manifest(f) for f in files):
        chosen["dependency"] = "a dependency manifest is in scope"
    typed = sorted(lang for lang in languages if lang in ("typescript", "python", "java"))
    if typed:
        chosen["type_safety"] = "typed languages detected: " + ", ".join(typed)
    hints = ("api", "route", "controller", "endpoint", "handler")
    if any(h in f.lower() for f in files for h in hints):
        chosen["api_contract"] = "files look like API routes or handlers"
    if not chosen:
        chosen["security"] = "secrets can sit in any text file"
    chosen["qa_synthesis"] = "merges all findings into one report"
    return [{"id": a, "reason": chosen[a]} for a in _ordered(list(chosen))]


def _ordered(agents: Any) -> list[AgentId]:
    wanted = set(agents)
    ordered = [a for a in AGENT_IDS if a in wanted and a != "qa_synthesis"]
    return ordered + (["qa_synthesis"] if "qa_synthesis" in wanted else [])


def list_agents() -> dict[str, Any]:
    """List the review agents (rule counts, deterministic checks) and the presets."""
    return {
        "agents": [
            {
                "id": a.id,
                "name": a.name,
                "summary": a.summary,
                "rule_count": len(a.rules),
                "checks": list(a.checks),
            }
            for a in registry.AGENTS.values()
        ],
        "presets": {
            name: {"description": p.description, "agents": list(p.agents)}
            for name, p in registry.PRESETS.items()
        },
    }


def plan_review(
    scope: Literal["diff", "paths", "repo"] = "diff",
    paths: list[str] | None = None,
    base: str = "HEAD",
    preset: str | None = None,
    agents: list[AgentId] | None = None,
) -> dict[str, Any]:
    """Plan a review: files in priority order, languages, agents to run, next steps.

    scope "diff" uses git changes against base plus untracked files; "paths" uses the given
    paths; "repo" uses every source file after .gitignore and default exclusions.
    """
    root = project_root()
    if scope == "diff":
        selection = select_files(root, changed_files(root, base))
    elif scope == "paths":
        if not paths:
            raise ValueError("scope 'paths' needs a non-empty paths list")
        selection = select_files(root, paths)
    else:
        selection = select_files(root)
    files = sorted(
        selection.files,
        key=lambda f: (0 if language_of(f) else 1 if is_manifest(f) else 2, f),
    )
    languages = Counter(lang for f in files if (lang := language_of(f)))
    return {
        "root": str(root),
        "scope": scope,
        "base": base if scope == "diff" else None,
        "files": files,
        "file_count": len(files),
        "truncated": selection.truncated,
        "max_files": MAX_FILES,
        "languages": dict(languages.most_common()),
        "agents": _select_agents(files, preset, agents),
        "next_steps": NEXT_STEPS,
    }


def get_rules(agent: AgentId, language: str | None = None) -> dict[str, Any]:
    """Rules of one agent, optionally filtered by language, plus the Finding JSON schema."""
    found = registry.AGENTS.get(agent)
    if found is None:
        raise ValueError(f"no rule file loaded for agent {agent!r}")
    wanted = language.lower() if language else None
    rules = [r for r in found.rules if not wanted or not r.languages or wanted in r.languages]
    return {
        "agent": found.id,
        "name": found.name,
        "summary": found.summary,
        "language": wanted,
        "rules": [r.model_dump(exclude_defaults=True) for r in rules],
        "finding_schema": Finding.model_json_schema(),
    }


def run_checks(agent: AgentId, paths: list[str] | None = None) -> dict[str, Any]:
    """Run the deterministic checks of one agent on paths (default: the whole repo)."""
    root = project_root()
    selection = select_files(root, paths)
    checks = CHECKS[agent]
    result: dict[str, Any] = {"agent": agent, "checks": list(checks)}
    if not checks:
        result["note"] = "qa_synthesis has no deterministic checks; call synthesize_report."
    ctx = CheckContext(root=root, files=selection.files)
    findings: list[Finding] = []
    for name, check in checks.items():
        try:
            findings.extend(check(ctx))
        except Exception as exc:  # one broken check must not hide the others
            log.exception("check %s failed", name)
            ctx.errors.append(f"{name}: {type(exc).__name__}: {exc}"[:300])
    findings.sort(key=lambda f: (severity_rank(f.severity), f.file or "", f.line or 0))
    result.update(
        checked_files=len(selection.files),
        findings=[f.model_dump(exclude_none=True) for f in findings[:MAX_FINDINGS]],
        finding_count=len(findings),
        errors=ctx.errors,
        truncated=selection.truncated or len(findings) > MAX_FINDINGS,
    )
    return result


def synthesize_report(findings: list[Finding]) -> dict[str, Any]:
    """Deduplicate and sort findings, count them, and compute a 0-100 score."""
    return synthesize(findings)


def _compact(fn: Callable[..., dict[str, Any]]) -> Callable[..., str]:
    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> str:
        return json.dumps(fn(*args, **kwargs), separators=(",", ":"), ensure_ascii=False)

    return wrapper


def build_server() -> FastMCP:
    mcp = FastMCP("aetheris", instructions=NEXT_STEPS)
    for tool in (list_agents, plan_review, get_rules, run_checks, synthesize_report):
        mcp.tool(structured_output=False)(_compact(tool))
    return mcp


def main() -> None:
    logging.basicConfig(stream=sys.stderr, level=logging.WARNING)
    log.info("aetheris %s serving %s", __version__, project_root())
    build_server().run(transport="stdio")
