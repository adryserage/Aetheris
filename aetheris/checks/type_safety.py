"""Typing escape hatches: any, unsafe casts, suppressed type errors."""

from aetheris.checks.base import CheckContext, demote_in_tests, pattern, scan_patterns
from aetheris.checks.secrets import redact
from aetheris.domain import Finding

_TS = ("typescript",)
_PY = ("python",)

PATTERNS = [
    pattern(
        "any_usage",
        r":\s*any\b|<any>|\bas\s+any\b",
        "medium",
        "'any' disables checks",
        _TS,
        ignore_case=False,
    ),
    pattern("unsafe_cast", r"\bas\s+unknown\s+as\b", "high", "double cast hides type errors", _TS),
    pattern(
        "non_null_assertion", r"\w!\.|\w!\[", "medium", "non-null assertion", _TS, ignore_case=False
    ),
    pattern(
        "type_ignore",
        r"@ts-ignore|@ts-nocheck|@ts-expect-error",
        "medium",
        "type checking suppressed",
        _TS,
    ),
    pattern(
        "any_usage",
        r":\s*Any\b|->\s*Any\b|Optional\[Any\]",
        "medium",
        "Any in a hint",
        _PY,
        ignore_case=False,
    ),
    pattern("unsafe_cast", r"\bcast\s*\(", "high", "typing.cast bypasses checking", _PY),
    pattern(
        "type_ignore",
        r"#\s*(?:type|pyright|mypy):\s*ignore",
        "medium",
        "type checking suppressed",
        _PY,
    ),
    pattern(
        "type_ignore",
        r"@SuppressWarnings\s*\(",
        "medium",
        "compiler warnings suppressed",
        ("java",),
    ),
    pattern("raw_generic", r"<\?>", "low", "unbounded wildcard", ("java",)),
    pattern("null_safety", r"\breturn\s+null\b", "low", "returns null", ("java",)),
]


def type_patterns(ctx: CheckContext) -> list[Finding]:
    return demote_in_tests(scan_patterns(ctx, "type_safety", PATTERNS, redact))
