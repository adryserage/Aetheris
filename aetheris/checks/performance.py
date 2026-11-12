"""Performance anti-patterns: loop-aware detection plus blocking calls in async code."""

import re

from aetheris.checks.base import (
    CheckContext,
    demote_in_tests,
    is_comment,
    make_finding,
    pattern,
    scan_patterns,
)
from aetheris.checks.secrets import redact
from aetheris.domain import Finding, Severity

_LOOP = re.compile(r"^(?:for|while)\b|^for\s+await\b")
# An inner loop over a literal or a module constant has a fixed size: no quadratic cost.
_FIXED_SIZE_LOOP = re.compile(
    r"^for\b.*?\b(?:in|of)\s+"
    r"(?P<it>\([^()]*\)|\[[^\[\]]*\]|\{[^{}]*\}|_?[A-Z][A-Z0-9_]*)\s*[:){]"
)
_IN_LOOP: list[tuple[str, re.Pattern[str], Severity, str]] = [
    (
        "n_plus_one",
        re.compile(r"\b(?:query|execute|findOne|findById|findMany|fetch|fetchone|select)\s*\("),
        "medium",
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
                fixed = _FIXED_SIZE_LOOP.match(stripped)
                fixed = fixed if fixed and " for " not in fixed["it"] else None
                if stack and stack[-1][1] not in reported_outer and not fixed:
                    outer = stack[-1][1]
                    reported_outer.add(outer)
                    findings.append(
                        make_finding(
                            "nested_loops",
                            "performance",
                            "low",
                            f"loop nested at line {number}; quadratic only if both loops grow "
                            "with the input",
                            rel,
                            outer,
                            redact(lines[outer - 1].strip())[:120],
                        )
                    )
                stack.append((indent, number))
                continue
            if not stack:
                continue
            for name, regex, severity, message in _IN_LOOP:
                if regex.search(line):
                    findings.append(
                        make_finding(
                            name,
                            "performance",
                            severity,
                            message,
                            rel,
                            number,
                            redact(stripped)[:120],
                        )
                    )
    return findings


def performance_patterns(ctx: CheckContext) -> list[Finding]:
    return demote_in_tests(
        _loop_findings(ctx) + scan_patterns(ctx, "performance", _LINE_PATTERNS, redact)
    )
