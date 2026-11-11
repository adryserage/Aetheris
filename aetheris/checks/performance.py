"""Performance anti-patterns: loop-aware detection plus blocking calls in async code."""

import re

from aetheris.checks.base import CheckContext, is_comment, pattern, scan_patterns
from aetheris.checks.secrets import redact
from aetheris.domain import Finding, Severity

_LOOP = re.compile(r"^(?:for|while)\b|^for\s+await\b")
_IN_LOOP: list[tuple[str, re.Pattern[str], Severity, str]] = [
    (
        "n_plus_one",
        re.compile(r"\b(?:query|execute|findOne|findById|findMany|fetch|fetchone|select)\s*\("),
        "high",
        "database or network call inside a loop; batch it",
    ),
    (
        "string_concat_in_loop",
        re.compile(r"\+=\s*(?:f?[\"']|str\()"),
        "low",
        "string built by repeated concatenation; collect and join",
    ),
    (
        "sort_in_loop",
        re.compile(r"\.sort\s*\(|\bsorted\s*\("),
        "low",
        "sort inside a loop; sort once outside",
    ),
]
_LINE_PATTERNS = [
    pattern(
        "blocking_async",
        r"await\b.*\.(?:readFileSync|writeFileSync|execSync)",
        "medium",
        "synchronous call inside async code blocks the event loop",
    ),
]


def _loop_findings(ctx: CheckContext) -> list[Finding]:
    findings: list[Finding] = []
    for rel in ctx.code_files():
        content = ctx.read(rel)
        if content is None:
            continue
        lines = content.splitlines()
        stack: list[tuple[int, int]] = []  # (indent, line number) of enclosing loops
        reported_outer: set[int] = set()
        for number, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped or is_comment(line):
                continue
            indent = len(line) - len(line.lstrip())
            while stack and indent <= stack[-1][0]:
                stack.pop()
            if _LOOP.match(stripped):
                if stack and stack[-1][1] not in reported_outer:
                    outer = stack[-1][1]
                    reported_outer.add(outer)
                    findings.append(
                        Finding(
                            agent="performance",
                            severity="medium",
                            file=rel,
                            line=outer,
                            message=f"nested_loops: loop nested at line {number}; "
                            "quadratic cost on large inputs",
                            evidence=redact(lines[outer - 1].strip())[:120],
                        )
                    )
                stack.append((indent, number))
                continue
            if not stack:
                continue
            for name, regex, severity, message in _IN_LOOP:
                if regex.search(line):
                    findings.append(
                        Finding(
                            agent="performance",
                            severity=severity,
                            file=rel,
                            line=number,
                            message=f"{name}: {message}",
                            evidence=redact(stripped)[:120],
                        )
                    )
    return findings


def performance_patterns(ctx: CheckContext) -> list[Finding]:
    return _loop_findings(ctx) + scan_patterns(ctx, "performance", _LINE_PATTERNS, redact)
