"""Shared plumbing for the deterministic checks."""

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from aetheris.domain import AgentId, Finding, Severity
from aetheris.files import language_of, read_text

MAX_PER_FILE_PATTERN = 20
COMMENT_PREFIXES = ("//", "#", "*", "/*")


@dataclass
class CheckContext:
    root: Path
    files: list[str]
    errors: list[str] = field(default_factory=list)
    _cache: dict[str, str | None] = field(default_factory=dict)

    def read(self, rel: str) -> str | None:
        if rel not in self._cache:
            self._cache[rel] = read_text(self.root, rel)
        return self._cache[rel]

    def code_files(self) -> list[str]:
        return [f for f in self.files if language_of(f)]


Check = Callable[[CheckContext], list[Finding]]


@dataclass(frozen=True)
class LinePattern:
    name: str
    regex: re.Pattern[str]
    severity: Severity
    message: str
    languages: frozenset[str] = frozenset()
    ignore_case: bool = True


def pattern(
    name: str,
    regex: str,
    severity: Severity,
    message: str,
    languages: tuple[str, ...] = (),
    ignore_case: bool = True,
) -> LinePattern:
    flags = re.IGNORECASE if ignore_case else 0
    return LinePattern(name, re.compile(regex, flags), severity, message, frozenset(languages))


def is_comment(line: str) -> bool:
    return line.strip().startswith(COMMENT_PREFIXES)


def scan_patterns(
    ctx: CheckContext,
    agent: AgentId,
    patterns: list[LinePattern],
    redact: Callable[[str], str],
) -> list[Finding]:
    """Apply single-line patterns to every code file. Evidence is always redacted."""
    findings: list[Finding] = []
    for rel in ctx.code_files():
        language = language_of(rel)
        content = ctx.read(rel)
        if content is None:
            continue
        counts: dict[str, int] = {}
        for number, line in enumerate(content.splitlines(), start=1):
            if len(line) > 2000 or is_comment(line):
                continue
            for pat in patterns:
                if pat.languages and language not in pat.languages:
                    continue
                if counts.get(pat.name, 0) >= MAX_PER_FILE_PATTERN or not pat.regex.search(line):
                    continue
                counts[pat.name] = counts.get(pat.name, 0) + 1
                findings.append(
                    Finding(
                        agent=agent,
                        severity=pat.severity,
                        file=rel,
                        line=number,
                        message=f"{pat.name}: {pat.message}",
                        evidence=redact(line.strip())[:120],
                    )
                )
    return findings
