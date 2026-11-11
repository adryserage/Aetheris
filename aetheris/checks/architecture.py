"""Import graph and circular dependencies (Python and JavaScript/TypeScript)."""

import ast
import re
from pathlib import PurePosixPath

from aetheris.checks.base import CheckContext
from aetheris.domain import Finding
from aetheris.files import language_of

_JS_EXTENSIONS = (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".mts", ".cts")
_JS_IMPORT = re.compile(
    r"""(?:\bfrom\s*|\bimport\s*\(?\s*|\brequire\s*\(\s*)['"](\.{1,2}/[^'"]*|\.{1,2})['"]"""
)
MAX_CYCLE_FILES_SHOWN = 6


def _python_module_names(rel: str) -> list[str]:
    path = PurePosixPath(rel).with_suffix("")
    parts = list(path.parts)
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    if not parts:
        return []
    names = [".".join(parts)]
    if parts[0] in ("src", "lib") and len(parts) > 1:
        names.append(".".join(parts[1:]))
    return names


def _toplevel_imports(statements: list[ast.stmt]) -> list[ast.stmt]:
    """Import statements outside function bodies and TYPE_CHECKING blocks."""
    out: list[ast.stmt] = []
    for stmt in statements:
        if isinstance(stmt, (ast.Import, ast.ImportFrom)):
            out.append(stmt)
        elif isinstance(stmt, ast.If):
            test = ast.dump(stmt.test)
            if "TYPE_CHECKING" not in test:
                out.extend(_toplevel_imports(stmt.body))
            out.extend(_toplevel_imports(stmt.orelse))
        elif isinstance(stmt, ast.Try):
            for block in (stmt.body, stmt.orelse, stmt.finalbody):
                out.extend(_toplevel_imports(block))
        elif isinstance(stmt, ast.ClassDef):
            out.extend(_toplevel_imports(stmt.body))
    return out


def _python_edges(rel: str, content: str, modules: dict[str, str]) -> set[str]:
    try:
        tree = ast.parse(content)
    except (SyntaxError, ValueError, RecursionError):
        return set()
    is_package = PurePosixPath(rel).name == "__init__.py"
    own = _python_module_names(rel)
    package = (own[0] if is_package else own[0].rpartition(".")[0]) if own else ""
    targets: set[str] = set()
    for stmt in _toplevel_imports(tree.body):
        candidates: list[str] = []
        if isinstance(stmt, ast.Import):
            candidates = [alias.name for alias in stmt.names]
        elif isinstance(stmt, ast.ImportFrom):
            base = stmt.module or ""
            if stmt.level:
                anchor = package.split(".") if package else []
                anchor = anchor[: len(anchor) - (stmt.level - 1)] if stmt.level > 1 else anchor
                base = ".".join(anchor + ([stmt.module] if stmt.module else []))
            candidates = [f"{base}.{a.name}" if base else a.name for a in stmt.names] + [base]
        for name in candidates:
            while name:
                if name in modules:
                    targets.add(modules[name])
                    break
                name = name.rpartition(".")[0]
    targets.discard(rel)
    return targets


def _js_edges(rel: str, content: str, known: set[str]) -> set[str]:
    targets: set[str] = set()
    directory = PurePosixPath(rel).parent
    for match in _JS_IMPORT.finditer(content):
        raw = match.group(1)
        base = PurePosixPath(*directory.parts, raw) if raw else directory
        parts: list[str] = []
        for part in base.parts:
            if part == "..":
                if parts:
                    parts.pop()
            elif part != ".":
                parts.append(part)
        stem = "/".join(parts)
        options = [stem] + [stem + ext for ext in _JS_EXTENSIONS]
        options += [f"{stem}/index{ext}" for ext in _JS_EXTENSIONS]
        for option in options:
            if option in known and option != rel:
                targets.add(option)
                break
    return targets


def build_import_graph(ctx: CheckContext) -> dict[str, set[str]]:
    known = set(ctx.files)
    modules: dict[str, str] = {}
    for rel in ctx.files:
        if language_of(rel) == "python":
            for name in _python_module_names(rel):
                modules.setdefault(name, rel)
    graph: dict[str, set[str]] = {}
    for rel in ctx.files:
        language = language_of(rel)
        if language not in ("python", "javascript", "typescript"):
            continue
        content = ctx.read(rel)
        if content is None:
            continue
        if language == "python":
            graph[rel] = _python_edges(rel, content, modules)
        else:
            graph[rel] = _js_edges(rel, content, known)
    return graph


def strongly_connected(graph: dict[str, set[str]]) -> list[list[str]]:
    """Tarjan's algorithm, iterative. Components with more than one node."""
    index: dict[str, int] = {}
    low: dict[str, int] = {}
    on_stack: set[str] = set()
    stack: list[str] = []
    components: list[list[str]] = []
    counter = 0
    for root in sorted(graph):
        if root in index:
            continue
        work: list[tuple[str, list[str]]] = [(root, sorted(graph.get(root, ())))]
        index[root] = low[root] = counter
        counter += 1
        stack.append(root)
        on_stack.add(root)
        while work:
            node, pending = work[-1]
            if pending:
                nxt = pending.pop(0)
                if nxt not in graph:
                    continue
                if nxt not in index:
                    index[nxt] = low[nxt] = counter
                    counter += 1
                    stack.append(nxt)
                    on_stack.add(nxt)
                    work.append((nxt, sorted(graph.get(nxt, ()))))
                elif nxt in on_stack:
                    low[node] = min(low[node], index[nxt])
                continue
            work.pop()
            if work:
                parent = work[-1][0]
                low[parent] = min(low[parent], low[node])
            if low[node] == index[node]:
                component: list[str] = []
                while True:
                    member = stack.pop()
                    on_stack.discard(member)
                    component.append(member)
                    if member == node:
                        break
                if len(component) > 1:
                    components.append(sorted(component))
    return components


def circular_imports(ctx: CheckContext) -> list[Finding]:
    findings: list[Finding] = []
    for component in strongly_connected(build_import_graph(ctx)):
        shown = ", ".join(component[:MAX_CYCLE_FILES_SHOWN])
        extra = len(component) - MAX_CYCLE_FILES_SHOWN
        findings.append(
            Finding(
                agent="architecture",
                severity="high",
                file=component[0],
                message=f"circular_imports: {len(component)} files import each other: {shown}"
                + (f" (+{extra} more)" if extra > 0 else ""),
            )
        )
    return findings
