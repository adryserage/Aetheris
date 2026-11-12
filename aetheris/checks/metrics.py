"""Per-file and per-function metrics (lines, cyclomatic complexity, nesting) and thresholds."""

import ast
import re
from dataclasses import dataclass, field

from aetheris.checks.base import CheckContext, make_finding
from aetheris.domain import Finding, Severity
from aetheris.files import language_of

COMPLEXITY_LIMIT = 15
NESTING_LIMIT = 4
FUNCTION_LENGTH_LIMIT = 80
DUPLICATE_WINDOW = 5
MAX_FUNCTION_SCAN_CHARS = 300_000

_SKIP_NAMES = {"if", "for", "while", "switch", "catch", "return", "else", "new", "synchronized"}
_BRACE_FUNCTION_STARTS = [
    re.compile(r"\bfunction\s*\*?\s*(\w+)\s*\([^)]*\)[^{;]*\{"),
    re.compile(
        r"\b(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:function\s*)?\([^)]*\)\s*"
        r"(?:=>)?\s*\{"
    ),
    re.compile(r"\bfn\s+(\w+)[^{;]*\{"),
    re.compile(r"\bfunc\s+(?:\([^)]*\)\s*)?(\w+)\s*\([^)]*\)[^{;]*\{"),
    re.compile(
        r"^[ \t]*(?:(?:public|private|protected|static|final|async|override|abstract)\s+)*"
        r"[\w<>\[\],.?]+\s+(\w+)\s*\([^);{]*\)\s*(?:throws [\w, .]+)?\{",
        re.M,
    ),
]
_BRACE_COMPLEXITY = [
    r"\bif\s*\(",
    r"\belse\s+if\b",
    r"\bwhile\s*\(",
    r"\bfor\s*\(",
    r"\bcase\s+",
    r"\bcatch\s*\(",
    r"&&",
    r"\|\|",
    r"\s\?\s[^:\n]+\s:\s",
]
_BRACE_COMPLEXITY_RE = re.compile("|".join(_BRACE_COMPLEXITY))

_PY_NESTING = tuple(
    getattr(ast, name)
    for name in ("If", "For", "AsyncFor", "While", "Try", "TryStar", "With", "AsyncWith")
    if hasattr(ast, name)
)
_PY_DEFS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


@dataclass(frozen=True)
class FunctionMetrics:
    name: str
    line: int
    length: int
    complexity: int
    nesting: int


@dataclass
class FileMetrics:
    lines: int
    code_lines: int
    complexity: int
    max_nesting: int
    functions: list[FunctionMetrics] = field(default_factory=list)


def _py_complexity(root: ast.AST, skip_defs: bool) -> int:
    total = 1
    stack: list[ast.AST] = [root]
    while stack:
        node = stack.pop()
        for child in ast.iter_child_nodes(node):
            if skip_defs and isinstance(child, _PY_DEFS):
                continue
            if isinstance(child, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.IfExp)):
                total += 1
            elif isinstance(child, ast.ExceptHandler):
                total += 1
            elif isinstance(child, ast.comprehension):
                total += 1 + len(child.ifs)
            elif isinstance(child, ast.BoolOp):
                total += len(child.values) - 1
            elif type(child).__name__ == "match_case":
                total += 1
            stack.append(child)
    return total


def _py_nesting(node: ast.AST, depth: int = 0) -> int:
    best = depth
    for child in ast.iter_child_nodes(node):
        if isinstance(child, _PY_DEFS):
            continue
        is_elif = (
            isinstance(node, ast.If)
            and isinstance(child, ast.If)
            and len(node.orelse) == 1
            and node.orelse[0] is child
        )
        deeper = depth + 1 if isinstance(child, _PY_NESTING) and not is_elif else depth
        best = max(best, _py_nesting(child, deeper))
    return best


def _python_metrics(content: str) -> FileMetrics | None:
    try:
        tree = ast.parse(content)
        functions: list[FunctionMetrics] = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                end = node.end_lineno or node.lineno
                functions.append(
                    FunctionMetrics(
                        node.name,
                        node.lineno,
                        end - node.lineno + 1,
                        _py_complexity(node, skip_defs=True),
                        _py_nesting(node),
                    )
                )
        return FileMetrics(
            lines=len(content.splitlines()),
            code_lines=_code_lines(content),
            complexity=_py_complexity(tree, skip_defs=False),
            max_nesting=max([_py_nesting(tree)] + [f.nesting for f in functions]),
            functions=sorted(functions, key=lambda f: f.line),
        )
    except (SyntaxError, RecursionError, ValueError):
        return None


def _code_lines(content: str) -> int:
    return sum(
        1
        for line in content.splitlines()
        if line.strip() and not line.strip().startswith(("#", "//", "*", "/*"))
    )


def _matching_brace(content: str, open_pos: int) -> int:
    depth = 0
    for index in range(open_pos, len(content)):
        char = content[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index
    return len(content) - 1


def _max_brace_depth(text: str) -> int:
    depth = best = 0
    for char in text:
        if char == "{":
            depth += 1
            best = max(best, depth)
        elif char == "}":
            depth -= 1
    return best


def _brace_functions(content: str) -> list[FunctionMetrics]:
    if len(content) > MAX_FUNCTION_SCAN_CHARS:
        return []
    found: dict[int, tuple[str, int]] = {}
    for regex in _BRACE_FUNCTION_STARTS:
        for match in regex.finditer(content):
            name = match.group(1)
            if name not in _SKIP_NAMES:
                found.setdefault(match.end() - 1, (name, match.start()))
    functions: list[FunctionMetrics] = []
    for brace, (name, start) in found.items():
        body = content[brace : _matching_brace(content, brace) + 1]
        functions.append(
            FunctionMetrics(
                name=name,
                line=content.count("\n", 0, start) + 1,
                length=body.count("\n") + 1,
                complexity=1 + len(_BRACE_COMPLEXITY_RE.findall(body)),
                nesting=max(_max_brace_depth(body) - 1, 0),
            )
        )
    return sorted(functions, key=lambda f: f.line)


def compute_metrics(content: str, language: str | None) -> FileMetrics:
    if language == "python":
        result = _python_metrics(content)
        if result is not None:
            return result
    return FileMetrics(
        lines=len(content.splitlines()),
        code_lines=_code_lines(content),
        complexity=1 + len(_BRACE_COMPLEXITY_RE.findall(content)),
        max_nesting=_max_brace_depth(content),
        functions=[] if language == "python" else _brace_functions(content),
    )


def find_duplicate_blocks(content: str) -> list[tuple[int, int, int]]:
    """(start, end, first_seen_start) of repeated windows of non-trivial lines."""
    kept = [(n, line.strip()) for n, line in enumerate(content.splitlines(), 1)]
    kept = [(n, text) for n, text in kept if len(text) > 3]
    seen: dict[tuple[str, ...], int] = {}
    blocks: list[tuple[int, int, int]] = []
    last_end = 0
    for index in range(len(kept) - DUPLICATE_WINDOW + 1):
        window = kept[index : index + DUPLICATE_WINDOW]
        key = tuple(text for _, text in window)
        if sum(len(t) for t in key) < 80:
            continue
        first = seen.setdefault(key, window[0][0])
        if first != window[0][0] and window[0][0] > last_end:
            last_end = window[-1][0]
            blocks.append((window[0][0], last_end, first))
    return blocks


def file_metrics(ctx: CheckContext) -> list[Finding]:
    findings: list[Finding] = []
    for rel in ctx.code_files():
        content = ctx.read(rel)
        if content is None or not content.strip():
            continue
        m = compute_metrics(content, language_of(rel))
        findings.append(
            make_finding(
                "file_metrics",
                "metrics",
                "info",
                f"lines={m.lines} code_lines={m.code_lines} "
                f"complexity={m.complexity} max_nesting={m.max_nesting} "
                f"functions={len(m.functions)}",
                rel,
            )
        )
    return findings


def metric_thresholds(ctx: CheckContext) -> list[Finding]:
    findings: list[Finding] = []
    for rel in ctx.code_files():
        content = ctx.read(rel)
        if content is None or not content.strip():
            continue
        for fn in compute_metrics(content, language_of(rel)).functions:
            if fn.complexity > COMPLEXITY_LIMIT:
                findings.append(
                    _quality(
                        "complexity",
                        rel,
                        fn.line,
                        "medium",
                        f"{fn.name} has cyclomatic complexity {fn.complexity} "
                        f"(limit {COMPLEXITY_LIMIT})",
                    )
                )
            if fn.nesting > NESTING_LIMIT:
                findings.append(
                    _quality(
                        "nesting",
                        rel,
                        fn.line,
                        "low",
                        f"{fn.name} nests {fn.nesting} levels deep (limit {NESTING_LIMIT})",
                    )
                )
            if fn.length > FUNCTION_LENGTH_LIMIT:
                findings.append(
                    _quality(
                        "function_length",
                        rel,
                        fn.line,
                        "low",
                        f"{fn.name} is {fn.length} lines " f"(limit {FUNCTION_LENGTH_LIMIT})",
                    )
                )
    return findings


def duplicate_blocks(ctx: CheckContext) -> list[Finding]:
    findings: list[Finding] = []
    for rel in ctx.code_files():
        content = ctx.read(rel)
        if content is None:
            continue
        for start, end, first in find_duplicate_blocks(content):
            findings.append(
                _quality(
                    "duplicate_block",
                    rel,
                    start,
                    "low",
                    f"lines {start}-{end} repeat the block at line {first}",
                )
            )
    return findings


def _quality(name: str, rel: str, line: int, severity: Severity, message: str) -> Finding:
    return make_finding(name, "code_quality", severity, message, rel, line)
