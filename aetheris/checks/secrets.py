"""Secret scan: credential regexes with masked evidence."""

import re
from dataclasses import dataclass

from aetheris.checks.base import CheckContext, make_finding
from aetheris.domain import Finding, Severity
from aetheris.files import MAX_FILE_BYTES, is_doc_file, is_test_file

_CONFIDENCE_RANK = {"high": 0, "medium": 1}

# (name, regex, confidence). Low-confidence patterns (bare UUIDs) are left out on purpose.
_PATTERNS: list[tuple[str, str, str]] = [
    ("aws_access_key", r"AKIA[0-9A-Z]{16}", "high"),
    (
        "aws_secret_key",
        r"(?i)aws[_\-]?secret[_\-]?(?:access[_\-]?)?key[\s]*[=:]\s*['\"]?([A-Za-z0-9/+=]{40})",
        "high",
    ),
    ("github_token", r"gh[pousr]_[A-Za-z0-9_]{36,255}", "high"),
    ("gitlab_token", r"glpat-[A-Za-z0-9\-_]{20,}", "high"),
    ("slack_token", r"xox[baprs]-[0-9]{10,13}-[0-9]{10,13}[a-zA-Z0-9-]*", "high"),
    (
        "slack_webhook",
        r"https://hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[A-Za-z0-9]+",
        "high",
    ),
    (
        "private_key_header",
        r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----",
        "high",
    ),
    ("gcp_api_key", r"AIza[0-9A-Za-z_-]{35}", "high"),
    ("gcp_service_account", r'"type":\s*"service_account"', "high"),
    (
        "azure_storage_key",
        r"(?i)DefaultEndpointsProtocol=https;AccountName=[^;]+;AccountKey=([A-Za-z0-9+/=]{88})",
        "high",
    ),
    ("stripe_secret_key", r"sk_(?:live|test)_[A-Za-z0-9]{24,}", "high"),
    ("sendgrid_api_key", r"SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}", "high"),
    ("twilio_api_key", r"SK[a-f0-9]{32}", "high"),
    (
        "twilio_auth_token",
        r"(?i)twilio[_\-]?auth[_\-]?token[\s]*[=:]\s*['\"]?([a-f0-9]{32})",
        "high",
    ),
    ("anthropic_api_key", r"sk-ant-[A-Za-z0-9_-]{95,}", "high"),
    ("openai_api_key", r"sk-[A-Za-z0-9]{48,}", "high"),
    ("mailgun_api_key", r"key-[A-Za-z0-9]{32}", "high"),
    ("npm_token", r"npm_[A-Za-z0-9]{36}", "high"),
    ("pypi_token", r"pypi-[A-Za-z0-9_-]{100,}", "high"),
    (
        "generic_api_key",
        r"(?i)(?:api[_\-]?key|apikey)[\s]*[=:]\s*['\"]?([A-Za-z0-9_\-]{20,})",
        "medium",
    ),
    (
        "generic_secret",
        r"(?i)(?:secret|token|password|passwd|pwd)[\s]*[=:]\s*['\"]?([^\s'\"]{8,})",
        "medium",
    ),
    ("jwt_token", r"eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*", "medium"),
    # Not an auth-param such as `Bearer resource_metadata="..."` (WWW-Authenticate).
    ("bearer_token", r'(?i)bearer\s+(?![a-z_]+=")([A-Za-z0-9_\-\.=]{16,})', "medium"),
    ("basic_auth", r"(?i)basic\s+([A-Za-z0-9+/=]{20,})", "medium"),
    (
        "connection_string",
        r"(?i)(?:mysql|postgres|postgresql|mongodb|redis|amqp)://[^\s'\"]+:([^\s'\"]+)@[^\s'\"]+",
        "medium",
    ),
    ("stripe_publishable_key", r"pk_(?:live|test)_[A-Za-z0-9]{24,}", "medium"),
]

_COMPILED = [(name, re.compile(rx), conf) for name, rx, conf in _PATTERNS]
_SEVERITY: dict[str, Severity] = {"high": "critical", "medium": "medium"}
_NOT_A_LITERAL = re.compile(r"[()\[\]{}<>$%]|^(?:os|process|env|config|settings|self|this)\b")
_PLACEHOLDERS = ("changeme", "example", "your_", "your-", "xxxx", "placeholder", "dummy")


@dataclass(frozen=True)
class SecretHit:
    name: str
    confidence: str
    start: int
    end: int
    value: str


def mask_secret(value: str, show_start: int = 4, show_end: int = 2) -> str:
    """Keep the first and last characters, mask the middle (at most 8 asterisks)."""
    if len(value) <= show_start + show_end:
        return "*" * len(value)
    middle = "*" * min(len(value) - show_start - show_end, 8)
    return f"{value[:show_start]}{middle}{value[-show_end:]}"


def _looks_like_literal(name: str, value: str) -> bool:
    """False for values that are not secrets: documented examples, placeholders, names."""
    lowered = value.lower()
    if "example" in lowered:
        return False  # documented sample keys, such as AWS's AKIA...EXAMPLE
    if name != "generic_secret":
        return True
    return not (_NOT_A_LITERAL.search(value) or any(p in lowered for p in _PLACEHOLDERS))


def find_secrets(line: str) -> list[SecretHit]:
    """Non-overlapping secret matches in a line, most confident first."""
    candidates: list[SecretHit] = []
    for name, regex, confidence in _COMPILED:
        for match in regex.finditer(line):
            group = 1 if match.re.groups else 0
            value = match.group(group)
            if value and _looks_like_literal(name, value):
                candidates.append(
                    SecretHit(name, confidence, match.start(group), match.end(group), value)
                )
    candidates.sort(key=lambda h: (_CONFIDENCE_RANK[h.confidence], h.start))
    accepted: list[SecretHit] = []
    for hit in candidates:
        if all(hit.end <= a.start or hit.start >= a.end for a in accepted):
            accepted.append(hit)
    return sorted(accepted, key=lambda h: h.start)


def redact(line: str) -> str:
    """The line with every secret value replaced by its masked form."""
    out: list[str] = []
    cursor = 0
    for hit in find_secrets(line):
        out.append(line[cursor : hit.start])
        out.append(mask_secret(hit.value))
        cursor = hit.end
    out.append(line[cursor:])
    return "".join(out)


def secret_scan(ctx: CheckContext) -> list[Finding]:
    findings: list[Finding] = []
    for rel in ctx.files:
        content = ctx.read(rel)
        if content is None or len(content) > MAX_FILE_BYTES:
            continue
        # Docs and tests hold sample credentials. A provider-specific key there still counts.
        sample_place = is_doc_file(rel) or is_test_file(rel)
        for number, line in enumerate(content.splitlines(), start=1):
            if len(line) > 2000:
                continue
            for hit in find_secrets(line):
                severity: Severity = (
                    "info"
                    if sample_place and hit.confidence != "high"
                    else _SEVERITY[hit.confidence]
                )
                findings.append(
                    make_finding(
                        "secret_scan",
                        "security",
                        severity,
                        f"possible {hit.name.replace('_', ' ')}",
                        rel,
                        number,
                        redact(line.strip())[:120],
                    )
                )
    return findings
