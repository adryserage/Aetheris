"""Security regex patterns. Hardcoded secrets are covered by secret_scan."""

from aetheris.checks.base import CheckContext, demote_in_tests, pattern, scan_patterns
from aetheris.checks.secrets import redact
from aetheris.domain import Finding

_COLUMNS = r"(?:\*|(?:DISTINCT\s+)?[\w.*()]+(?:\s*,\s*[\w.*()]+)*)"
_SQL_VERB = (
    r"\b(?:SELECT\s+" + _COLUMNS + r"\s+FROM"
    r"|INSERT\s+INTO\s+[\w.]+\s*(?:\(|VALUES\b|SELECT\b)"
    r"|UPDATE\s+[\w.]+\s+SET\b"
    r"|DELETE\s+FROM\s+[\w.]+\s+WHERE\b)"
)
SQL_REGEX = (
    r"""(?:execute|query)\s*\(\s*["'][^"']*["']\s*[+%]"""
    r"""|\bf(["'])(?:(?!\1).)*?""" + _SQL_VERB + r"""(?:(?!\1).)*?\{"""
    r"""|(["'])(?:(?!\2).)*?""" + _SQL_VERB + r"""(?:(?!\2).)*\2\s*(?:\+|%\s*[\w(]|\.format\s*\()"""
    r"""|`[^`]*?""" + _SQL_VERB + r"""[^`]*\$\{"""
)

PATTERNS = [
    pattern(
        "sql_injection",
        SQL_REGEX,
        "high",
        "SQL built by concatenation or formatting; use parameterized queries",
    ),
    pattern(
        "xss",
        r"innerHTML\s*=|dangerouslySetInnerHTML|document\.write\s*\(",
        "high",
        "unsafe HTML sink; escape input or use a sanitizer",
        ("javascript", "typescript"),
    ),
    pattern(
        "dynamic_eval",
        r"\beval\s*\(",
        "high",
        "dynamic code evaluation; avoid eval on anything derived from input",
    ),
    pattern(
        "weak_crypto",
        r"\b(?:MD5|SHA1|DES|RC4)\s*\(",
        "medium",
        "weak hash or cipher; use SHA-256 or AES-256",
    ),
    pattern(
        "insecure_random",
        r"Math\.random\s*\(|random\.randint|\bRandom\(\)",
        "medium",
        "non-cryptographic randomness; use secrets or crypto.getRandomValues for security uses",
    ),
]


def security_patterns(ctx: CheckContext) -> list[Finding]:
    return demote_in_tests(scan_patterns(ctx, "security", PATTERNS, redact))
