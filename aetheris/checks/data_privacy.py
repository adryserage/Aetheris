"""PII literals, PII in logs, insecure client-side storage, tracking calls."""

import re

from aetheris.checks.base import CheckContext, make_finding, pattern, scan_patterns
from aetheris.checks.secrets import redact
from aetheris.domain import Finding

PATTERNS = [
    pattern("ssn", r"\b\d{3}-\d{2}-\d{4}\b|\bssn\s*[:=]\s*[\"']?\d+", "high", "SSN-like value"),
    pattern(
        "email_literal",
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "low",
        "email address in code",
    ),
    pattern(
        "pii_logging",
        r"(?:console\.log|print|logger?\.\w+|Log\.\w+)\s*\([^)]*"
        r"(?:email|ssn|password|phone|card|user\.)",
        "medium",
        "personal data may reach the logs",
    ),
    pattern(
        "pii_logging",
        r"log\.\w+\([^)]*(?:req|request)\.body",
        "medium",
        "request body logged",
    ),
    pattern(
        "insecure_storage",
        r"cookie\s*\([^)]*(?:httpOnly|secure)\s*:\s*false"
        r"|(?:local|session)Storage\.setItem\s*\([^)]*(?:token|password|secret|auth)",
        "medium",
        "credential kept in client storage or in a weak cookie",
    ),
    pattern(
        "data_retention",
        r"(?:deleteOld|cleanup|purge)\s*[:=]\s*false|retention\s*[:=]\s*(?:null|undefined|none)",
        "low",
        "retention disabled",
    ),
    pattern(
        "tracking_without_consent_check",
        r"analytics\.track\s*\(|gtag\s*\(\s*[\"']event[\"']|mixpanel\.track\s*\(",
        "low",
        "tracking call; confirm consent is checked first",
    ),
]

_CARD = re.compile(r"\b(?:\d[ -]?){13,16}\b")


def _luhn(digits: str) -> bool:
    total = 0
    for index, char in enumerate(reversed(digits)):
        number = int(char)
        if index % 2 == 1:
            number = number * 2 - 9 if number > 4 else number * 2
        total += number
    return total % 10 == 0


def _card_findings(ctx: CheckContext) -> list[Finding]:
    findings: list[Finding] = []
    for rel in ctx.code_files():
        content = ctx.read(rel)
        if content is None:
            continue
        for number, line in enumerate(content.splitlines(), start=1):
            for match in _CARD.finditer(line):
                digits = re.sub(r"\D", "", match.group(0))
                if 13 <= len(digits) <= 16 and _luhn(digits):
                    masked = line.strip().replace(match.group(0), digits[:4] + "********")
                    findings.append(
                        make_finding(
                            "credit_card",
                            "data_privacy",
                            "high",
                            "number passing the Luhn check",
                            rel,
                            number,
                            redact(masked)[:120],
                        )
                    )
    return findings


def pii_patterns(ctx: CheckContext) -> list[Finding]:
    # Never lowered in test files: a real secret or personal data committed in a test leaks.
    return scan_patterns(ctx, "data_privacy", PATTERNS, redact) + _card_findings(ctx)
