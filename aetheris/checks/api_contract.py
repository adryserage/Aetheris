"""Route extraction, REST naming, and endpoints that nothing calls (or calls nothing)."""

import re
from dataclasses import dataclass

from aetheris.checks.base import CheckContext, is_comment
from aetheris.checks.secrets import redact
from aetheris.domain import Finding, Severity

_ROUTE_PATTERNS = [
    re.compile(
        r"\b(?:app|router|api|server|fastify|route|routes)\.(?P<m>get|post|put|patch|delete)"
        r"\s*\(\s*[`'\"](?P<p>/[^`'\"]*)[`'\"]"
    ),
    re.compile(r"@(?P<m>Get|Post|Put|Patch|Delete)(?:Mapping)?\s*\(\s*['\"](?P<p>[^'\"]*)['\"]"),
    re.compile(r"@\w+\.(?P<m>get|post|put|patch|delete|route)\s*\(\s*['\"](?P<p>/[^'\"]*)['\"]"),
]
_CALL_PATTERNS = [
    re.compile(r"\bfetch\s*\(\s*[`'\"](?P<p>[^`'\"]+)[`'\"]"),
    re.compile(r"\b(?:axios|ky|requests|httpx|http|dio)\.\w+\s*\(\s*[`'\"](?P<p>[^`'\"]+)[`'\"]"),
    re.compile(r"\$\.(?:get|post|ajax)\s*\(\s*['\"](?P<p>[^'\"]+)['\"]"),
]
_VERB_SEGMENT = re.compile(r"^(?:get|create|update|delete|fetch|add|remove)(?:[A-Z_\-]|$)")
_PARAM = re.compile(r"\$\{[^}]*\}|\{[^}]*\}|<[^>]*>|:\w+")


@dataclass(frozen=True)
class Route:
    method: str
    segments: tuple[str, ...]
    path: str
    file: str
    line: int


def _segments(path: str) -> tuple[str, ...]:
    path = re.sub(r"^[a-z][a-z0-9+.-]*://[^/]+", "", path.split("?")[0])
    path = _PARAM.sub("{}", path)
    return tuple(s for s in path.split("/") if s)


def _matches(route: tuple[str, ...], call: tuple[str, ...]) -> bool:
    """Route matches the call, ignoring a mount prefix on either side."""
    shorter, longer = sorted((route, call), key=len)
    if not shorter:
        return False
    tail = longer[len(longer) - len(shorter) :]
    return all(a == b or "{}" in (a, b) for a, b in zip(shorter, tail))


def _collect(ctx: CheckContext) -> tuple[list[Route], list[Route]]:
    routes: list[Route] = []
    calls: list[Route] = []
    seen: set[tuple[str, int, str, str]] = set()
    for rel in ctx.code_files():
        content = ctx.read(rel)
        if content is None:
            continue
        for number, line in enumerate(content.splitlines(), start=1):
            if len(line) > 2000 or is_comment(line):
                continue
            for regex in _ROUTE_PATTERNS:
                for match in regex.finditer(line):
                    path = match.group("p")
                    key = (rel, number, path, "route")
                    if key not in seen:
                        seen.add(key)
                        method = match.group("m").upper()
                        routes.append(Route(method, _segments(path), path, rel, number))
            for regex in _CALL_PATTERNS:
                for match in regex.finditer(line):
                    path = match.group("p")
                    calls.append(Route("ANY", _segments(path), path, rel, number))
    return routes, calls


def _finding(severity: Severity, route: Route, message: str) -> Finding:
    return Finding(
        agent="api_contract",
        severity=severity,
        file=route.file,
        line=route.line,
        message=message,
        evidence=redact(route.path)[:120],
    )


def api_patterns(ctx: CheckContext) -> list[Finding]:
    routes, _ = _collect(ctx)
    findings: list[Finding] = []
    for route in routes:
        if any(_VERB_SEGMENT.match(s) for s in route.segments):
            findings.append(
                _finding(
                    "low",
                    route,
                    f"verb_in_url: {route.method} {route.path} puts a verb in the URL; "
                    "name the resource and let the HTTP method carry the action",
                )
            )
    return findings


def orphan_endpoints(ctx: CheckContext) -> list[Finding]:
    routes, calls = _collect(ctx)
    findings: list[Finding] = []
    if not routes:
        return findings
    for route in routes:
        if not any(_matches(route.segments, c.segments) for c in calls):
            findings.append(
                _finding(
                    "info",
                    route,
                    f"orphan_endpoint: no call to {route.method} {route.path} in the "
                    "inspected files (external clients may still use it)",
                )
            )
    for call in calls:
        relative = call.path.startswith("/")
        if relative and not any(_matches(r.segments, call.segments) for r in routes):
            findings.append(
                _finding(
                    "medium",
                    call,
                    f"orphan_call: {call.path} matches no route defined in the inspected files",
                )
            )
    return findings
