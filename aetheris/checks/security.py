"""Security regex patterns. Hardcoded secrets are covered by secret_scan."""

import ast
from collections import Counter

from aetheris.checks.base import CheckContext, demote_in_tests, pattern, scan_patterns
from aetheris.checks.secrets import redact
from aetheris.domain import Finding
from aetheris.files import language_of

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


def _free_names(node: ast.AST) -> set[str]:
    names = [n for n in ast.walk(node) if isinstance(n, ast.Name)]
    bound = {n.id for n in names if isinstance(n.ctx, ast.Store)}
    return {n.id for n in names if isinstance(n.ctx, ast.Load)} - bound


def _module_constants(tree: ast.Module) -> set[str]:
    """Names bound once, at module level, to a value built only from literals and such names."""
    stores = Counter(
        n.id if isinstance(n, ast.Name) else n.arg
        for n in ast.walk(tree)
        if isinstance(n, ast.arg) or (isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store))
    )
    constants: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target, value = node.targets[0], node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            target, value = node.target, node.value
        else:
            continue
        if isinstance(target, ast.Name) and stores[target.id] == 1:
            if _free_names(value) <= constants:
                constants.add(target.id)
    return constants


def _sql_from_constants(content: str) -> set[int]:
    """Lines whose f-strings interpolate only module constants: no input reaches the SQL."""
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return set()
    constants = _module_constants(tree)
    lines: dict[int, bool] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.JoinedStr):
            safe = all(
                _free_names(v.value) <= constants
                for v in node.values
                if isinstance(v, ast.FormattedValue)
            )
            lines[node.lineno] = lines.get(node.lineno, True) and safe
    return {line for line, safe in lines.items() if safe}


def _drop_constant_sql(ctx: CheckContext, findings: list[Finding]) -> list[Finding]:
    safe_lines: dict[str, set[int]] = {}
    kept = []
    for f in findings:
        if f.rule_id == "SEC-001" and f.file and language_of(f.file) == "python":
            if f.file not in safe_lines:
                safe_lines[f.file] = _sql_from_constants(ctx.read(f.file) or "")
            if f.line in safe_lines[f.file]:
                continue
        kept.append(f)
    return kept


def security_patterns(ctx: CheckContext) -> list[Finding]:
    found = scan_patterns(ctx, "security", PATTERNS, redact)
    return demote_in_tests(_drop_constant_sql(ctx, found))
