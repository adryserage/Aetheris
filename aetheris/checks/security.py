"""Security regex patterns. Hardcoded secrets are covered by secret_scan."""

from aetheris.checks.base import CheckContext, pattern, scan_patterns
from aetheris.checks.secrets import redact
from aetheris.domain import Finding

PATTERNS = [
    pattern(
        "sql_injection",
        r"""(?:execute|query)\s*\(\s*["'][^"']*["']\s*[+%]|\.format\s*\(.*SELECT|f["'].*SELECT.*\{""",
        "high",
        "SQL built by concatenation or formatting; use parameterized queries",
    ),
    pattern(
        "xss",
        r"innerHTML\s*=|dangerouslySetInnerHTML|\beval\s*\(|document\.write\s*\(",
        "high",
        "unsafe HTML or code evaluation sink; escape input or use a sanitizer",
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
    return scan_patterns(ctx, "security", PATTERNS, redact)
