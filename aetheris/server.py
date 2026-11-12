"""MCP server. Six tools that drive a code review; no AI API is ever called.

Local mode (stdio) reads the project on disk. Hosted mode (aetheris.hosted, over HTTP) never
touches a disk: the assistant sends the contents of the files to check.

Playbooks are review methods adapted from third-party sources (aetheris/playbooks/); get_playbook
returns one with its attribution block, which must travel with any reproduction.
"""

import functools
import json
import logging
import sys
import time
from collections import Counter
from collections.abc import Awaitable, Callable
from typing import Any, Literal

import anyio
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

from aetheris import __version__, registry
from aetheris.changes import changed_files
from aetheris.checks import CHECKS, CheckContext
from aetheris.domain import AGENT_IDS, AgentId, Finding, severity_rank
from aetheris.files import (
    MAX_FILE_BYTES,
    MAX_FILES,
    check_label,
    is_manifest,
    language_of,
    project_root,
    select_files,
)
from aetheris.synthesis import synthesize

MAX_FINDINGS = 200
MAX_SENT_FILES = 100
log = logging.getLogger("aetheris")

_STEPS = (
    "For each agent listed: 1) call get_rules(agent) and read the rules; 2) call {run} to get "
    "deterministic findings; 3) read the listed files and judge "
    "them against the rules, adding your own findings (source='assistant', same schema as "
    "the Finding schema returned by get_rules). Finish with synthesize_report(findings) on all "
    "findings together, and report its score and top findings. Review qa_synthesis last. "
    "When an agent lists playbooks, read each one with get_playbook(id) before judging, and "
    "keep its attribution if you reproduce it."
)
NEXT_STEPS = _STEPS.format(run="run_checks(agent, paths)")
HOSTED_NEXT_STEPS = (
    "This Aetheris server cannot see your files: you send their contents. "
    + _STEPS.format(
        run=(
            f"run_checks(agent, files) with the path and full content of each file (at most "
            f"{MAX_SENT_FILES} files of {MAX_FILE_BYTES // 2**20} MB each per call; split larger "
            "reviews into several calls)"
        )
    )
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


def _playbooks_for(agent: str, scope: str, files: list[str]) -> list[dict[str, str]]:
    reasons: dict[str, str] = {}
    if agent == "qa_synthesis":
        reasons["fp-check"] = "verify suspected security findings before reporting them"
        reasons["vulnerability-triage-brocards"] = "triage reported vulnerabilities and CVEs"
    if agent == "security":
        if scope == "diff":
            reasons["differential-review"] = "the scope is a diff"
        if any(f.startswith(".github/workflows/") for f in files):
            reasons["agentic-actions-auditor"] = "GitHub Actions workflows are in scope"
    return [
        {"id": pid, "task": registry.PLAYBOOKS[pid].task, "reason": reason}
        for pid, reason in reasons.items()
        if pid in registry.PLAYBOOKS and agent in registry.PLAYBOOKS[pid].agents
    ]


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
                "playbook_count": sum(a.id in p.agents for p in registry.PLAYBOOKS.values()),
            }
            for a in registry.AGENTS.values()
        ],
        "presets": {
            name: {"description": p.description, "agents": list(p.agents)}
            for name, p in registry.PRESETS.items()
        },
    }


def _plan(
    selected: list[str], scope: str, preset: str | None, agents: list[AgentId] | None
) -> dict[str, Any]:
    files = sorted(
        selected,
        key=lambda f: (0 if language_of(f) else 1 if is_manifest(f) else 2, f),
    )
    languages = Counter(lang for f in files if (lang := language_of(f)))
    return {
        "scope": scope,
        "files": files,
        "file_count": len(files),
        "languages": dict(languages.most_common()),
        "agents": [
            {**a, "playbooks": _playbooks_for(a["id"], scope, files)}
            for a in _select_agents(files, preset, agents)
        ],
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
    return {
        "root": str(root),
        **_plan(selection.files, scope, preset, agents),
        "base": base if scope == "diff" else None,
        "truncated": selection.truncated,
        "max_files": MAX_FILES,
        "next_steps": NEXT_STEPS,
    }


class NamedFile(BaseModel):
    """A file to review. Only path is used to plan; content may be left out."""

    path: str
    content: str | None = None


class SentFile(BaseModel):
    """A file to check: path is a label (relative, no '..'), content is its full text."""

    path: str
    content: str


def _within_limit(files: list[Any]) -> None:
    if len(files) > MAX_SENT_FILES:
        raise ValueError(
            f"{len(files)} files sent; the limit is {MAX_SENT_FILES} per call, "
            "split them into several calls"
        )


def plan_sent_files(
    files: list[NamedFile] | None = None,
    preset: str | None = None,
    agents: list[AgentId] | None = None,
) -> dict[str, Any]:
    """Plan a review of files you will send: priority order, languages, agents, next steps.

    Pass the files you mean to review (path is enough here). Agents are chosen from the file
    names. The server never sees your project: run_checks needs the contents.
    """
    named = files or []
    _within_limit(named)
    labels = list(dict.fromkeys(check_label(f.path) for f in named))
    return {
        **_plan(labels, "provided", preset, agents),
        "max_files": MAX_SENT_FILES,
        "next_steps": HOSTED_NEXT_STEPS,
    }


def get_rules(agent: AgentId, language: str | None = None) -> dict[str, Any]:
    """Rules and playbooks of one agent, optionally filtered by language, plus the Finding schema."""
    found = registry.AGENTS.get(agent)
    if found is None:
        raise ValueError(f"no rule file loaded for agent {agent!r}")
    wanted = language.lower() if language else None
    rules = [r for r in found.rules if not wanted or not r.languages or wanted in r.languages]
    playbooks = [
        {"id": p.id, "title": p.title, "task": p.task, "when": p.when}
        for p in registry.PLAYBOOKS.values()
        if agent in p.agents and (not wanted or not p.languages or wanted in p.languages)
    ]
    return {
        "agent": found.id,
        "name": found.name,
        "summary": found.summary,
        "language": wanted,
        "rules": [r.model_dump(exclude_defaults=True) for r in rules],
        "playbooks": playbooks,
        "finding_schema": Finding.model_json_schema(),
    }


def get_playbook(id: str) -> dict[str, Any]:
    """Steps of one playbook (ids from get_rules or plan_review) plus its attribution block."""
    found = registry.PLAYBOOKS.get(id)
    if found is None:
        raise ValueError(f"unknown playbook {id!r}; known: {sorted(registry.PLAYBOOKS)}")
    return {
        "id": found.id,
        "task": found.task,
        "agents": list(found.agents),
        "steps": found.steps,
        "attribution": {
            "title": found.title,
            "author": found.author,
            "source": found.source,
            "license": found.license,
            "license_url": found.license_url,
            "changes": found.changes,
        },
    }


def _run(agent: AgentId, ctx: CheckContext, truncated: bool) -> dict[str, Any]:
    checks = CHECKS[agent]
    result: dict[str, Any] = {"agent": agent, "checks": list(checks)}
    if not checks:
        result["note"] = "qa_synthesis has no deterministic checks; call synthesize_report."
    findings: list[Finding] = []
    for name, check in checks.items():
        try:
            findings.extend(check(ctx))
        except Exception as exc:  # one broken check must not hide the others
            # The exception text can quote file content: it goes to the client, not to the log.
            log.error("check %s failed: %s", name, type(exc).__name__)
            ctx.errors.append(f"{name}: {type(exc).__name__}: {exc}"[:300])
    findings.sort(key=lambda f: (severity_rank(f.severity), f.file or "", f.line or 0))
    result.update(
        checked_files=len(ctx.files),
        findings=[f.model_dump(exclude_none=True) for f in findings[:MAX_FINDINGS]],
        finding_count=len(findings),
        errors=ctx.errors,
        truncated=truncated or len(findings) > MAX_FINDINGS,
    )
    return result


def run_checks(agent: AgentId, paths: list[str] | None = None) -> dict[str, Any]:
    """Run the deterministic checks of one agent on paths (default: the whole repo)."""
    root = project_root()
    selection = select_files(root, paths)
    return _run(agent, CheckContext(root=root, files=selection.files), selection.truncated)


def check_sent_files(agent: AgentId, files: list[SentFile]) -> dict[str, Any]:
    """Run the deterministic checks of one agent on the files you send (path and full content).

    At most 100 files of 1 MB each per call. Evidence in findings is redacted.
    """
    _within_limit(files)
    started = time.monotonic()
    ctx = CheckContext.from_contents((f.path, f.content) for f in files)
    result = _run(agent, ctx, truncated=False)
    log.info(
        "run_checks agent=%s files=%d bytes=%d duration_ms=%d",
        agent,
        len(files),
        sum(len(f.content.encode("utf-8")) for f in files),
        (time.monotonic() - started) * 1000,
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


def _in_thread(fn: Callable[..., str]) -> Callable[..., Awaitable[str]]:
    """Keep the HTTP event loop free while a check reads, parses or calls OSV."""

    @functools.wraps(fn)
    async def wrapper(*args: Any, **kwargs: Any) -> str:
        return await anyio.to_thread.run_sync(functools.partial(fn, *args, **kwargs))

    return wrapper


def build_server(hosted: bool = False) -> FastMCP:
    """Local mode reads the project on disk; hosted mode only sees the contents it is sent."""
    if not hosted:
        mcp = FastMCP("aetheris", instructions=NEXT_STEPS)
        tools = (list_agents, plan_review, get_rules, get_playbook, run_checks, synthesize_report)
        for tool in tools:
            mcp.tool(structured_output=False)(_compact(tool))
        return mcp
    mcp = FastMCP(
        "aetheris",
        instructions=HOSTED_NEXT_STEPS,
        host="0.0.0.0",  # Host and Origin are checked by aetheris.hosted, not by FastMCP
        stateless_http=True,
        json_response=True,
    )
    hosted_tools = (
        ("list_agents", list_agents),
        ("plan_review", plan_sent_files),
        ("get_rules", get_rules),
        ("get_playbook", get_playbook),
        ("run_checks", check_sent_files),
        ("synthesize_report", synthesize_report),
    )
    for name, fn in hosted_tools:
        mcp.tool(name=name, structured_output=False)(_in_thread(_compact(fn)))
    return mcp


def main() -> None:
    logging.basicConfig(stream=sys.stderr, level=logging.WARNING)
    log.info("aetheris %s serving %s", __version__, project_root())
    build_server().run(transport="stdio")
