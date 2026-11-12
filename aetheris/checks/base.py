"""Shared plumbing for the deterministic checks."""

import re
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from pathlib import Path

from aetheris.domain import AgentId, Finding, Severity
from aetheris.files import (
    MAX_FILE_BYTES,
    check_label,
    is_test_file,
    language_of,
    read_text,
)

MAX_PER_FILE_PATTERN = 20
COMMENT_PREFIXES = ("//", "#", "*", "/*")


@dataclass
class CheckContext:
    """The files a check sees. root=None means the contents were sent and the disk is never read."""

    root: Path | None
    files: list[str]
    errors: list[str] = field(default_factory=list)
    _cache: dict[str, str | None] = field(default_factory=dict)

    @classmethod
    def from_contents(cls, files: Iterable[tuple[str, str]]) -> "CheckContext":
        """Files sent as (path, content). Paths are labels: relative, no `..`, no NUL byte.

        Same rules as a file read from disk: over MAX_FILE_BYTES is refused, binary is skipped.
        """
        cache: dict[str, str | None] = {}
        for raw, content in files:
            rel = check_label(raw)
            if rel in cache:
                raise ValueError(f"path sent twice: {rel}")
            if len(content.encode("utf-8")) > MAX_FILE_BYTES:
                raise ValueError(f"{rel}: content exceeds the limit of {MAX_FILE_BYTES} bytes")
            cache[rel] = None if "\0" in content[:1024] else content
        return cls(root=None, files=list(cache), _cache=cache)

    def read(self, rel: str) -> str | None:
        if rel not in self._cache:
            self._cache[rel] = None if self.root is None else read_text(self.root, rel)
        return self._cache[rel]

    def code_files(self) -> list[str]:
        return [f for f in self.files if language_of(f)]


RULE_IDS: dict[str, str | None] = {
    "secret_scan": "SEC-005",
    "sql_injection": "SEC-001",
    "xss": "SEC-003",
    "dynamic_eval": "SEC-004",
    "weak_crypto": "SEC-006",
    "insecure_random": "SEC-008",
    "ssn": "PRIV-002",
    "email_literal": "PRIV-002",
    "credit_card": "PRIV-002",
    "pii_logging": "PRIV-001",
    "insecure_storage": "PRIV-005",
    "data_retention": "PRIV-008",
    "tracking_without_consent_check": "PRIV-007",
    "n_plus_one": "PERF-001",
    "string_concat_in_loop": "PERF-004",
    "sort_in_loop": "PERF-011",
    "blocking_async": "PERF-005",
    "nested_loops": "PERF-002",
    "any_usage": "TYP-001",
    "raw_generic": "TYP-013",
    "unsafe_cast": "TYP-002",
    "non_null_assertion": "TYP-004",
    "type_ignore": "TYP-003",
    "null_safety": None,
    "verb_in_url": "API-005",
    "orphan_endpoint": "API-002",
    "orphan_call": "API-002",
    "circular_imports": "ARC-001",
    "manifest_parse": "DEP-011",
    "osv_lookup": "DEP-001",
    "file_metrics": None,
    "complexity": "CQ-004",
    "nesting": "CQ-005",
    "function_length": "CQ-006",
    "duplicate_block": "CQ-007",
}


def make_finding(
    name: str,
    agent: AgentId,
    severity: Severity,
    message: str,
    file: str | None = None,
    line: int | None = None,
    evidence: str | None = None,
) -> Finding:
    """The only way checks build a finding: prefixes the message and sets the rule id."""
    return Finding(
        agent=agent,
        rule_id=RULE_IDS[name],
        severity=severity,
        file=file,
        line=line,
        message=f"{name}: {message}",
        evidence=evidence,
    )


Check = Callable[[CheckContext], list[Finding]]


def demote_in_tests(findings: list[Finding]) -> list[Finding]:
    """Code patterns found in a test file drop to info: fixtures hold unsafe code on purpose."""
    return [
        (
            f.model_copy(update={"severity": "info", "message": f"{f.message} (test file)"})
            if f.file and is_test_file(f.file)
            else f
        )
        for f in findings
    ]


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
                    make_finding(
                        pat.name,
                        agent,
                        pat.severity,
                        pat.message,
                        rel,
                        number,
                        redact(line.strip())[:120],
                    )
                )
    return findings
