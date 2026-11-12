"""File selection inside the project root: sandbox, ignore rules, size and binary filters."""

import os
from dataclasses import dataclass
from pathlib import Path

import pathspec

MAX_FILE_BYTES = 1024 * 1024
MAX_FILES = 500

LANGUAGES: dict[str, str] = {
    ".py": "python",
    ".pyi": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".mts": "typescript",
    ".cts": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".java": "java",
    ".kt": "kotlin",
    ".go": "go",
    ".rs": "rust",
    ".dart": "dart",
    ".cs": "csharp",
    ".php": "php",
    ".rb": "ruby",
    ".swift": "swift",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".hpp": "cpp",
}

MANIFESTS = ("package.json", "pubspec.yaml", "requirements.txt", "pyproject.toml")

EXCLUDED_DIRS = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        "node_modules",
        "__pycache__",
        ".venv",
        "venv",
        "env",
        ".tox",
        ".nox",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".dart_tool",
        ".next",
        ".nuxt",
        ".idea",
        ".vscode",
        "dist",
        "build",
        "htmlcov",
        "coverage",
        "site-packages",
        "vendor",
    }
)

EXCLUDED_FILE_SUFFIXES = (".min.js", ".min.css", ".map", ".lock", ".egg", ".whl")
EXCLUDED_FILE_NAMES = frozenset({"package-lock.json", "pnpm-lock.yaml", "yarn.lock", ".DS_Store"})

BINARY_SUFFIXES = frozenset(
    {
        ".pyc",
        ".pyo",
        ".so",
        ".dll",
        ".exe",
        ".bin",
        ".o",
        ".a",
        ".lib",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".ico",
        ".webp",
        ".pdf",
        ".zip",
        ".tar",
        ".gz",
        ".bz2",
        ".7z",
        ".rar",
        ".mp3",
        ".mp4",
        ".avi",
        ".mov",
        ".woff",
        ".woff2",
        ".ttf",
        ".eot",
        ".otf",
        ".sqlite",
        ".db",
    }
)


class PathOutsideRootError(ValueError):
    """A requested path resolves outside the project root."""


@dataclass(frozen=True)
class FileSelection:
    files: list[str]
    truncated: bool


def project_root() -> Path:
    """AETHERIS_ROOT if set, else the working directory, symlinks resolved."""
    return Path(os.environ.get("AETHERIS_ROOT") or os.getcwd()).resolve()


def resolve_in_root(root: Path, rel: str) -> Path:
    """Resolve rel against root and reject anything that escapes it."""
    if "\0" in rel:
        raise PathOutsideRootError("path contains a NUL byte")
    candidate = (root / rel).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        raise PathOutsideRootError(f"path escapes the project root: {rel}") from None
    return candidate


def check_label(raw: str) -> str:
    """A path the client sent with a file's content: only a label, never opened.

    It must be relative, without `..`, a NUL byte or a drive letter. Returns it normalized.
    """
    parts = raw.replace("\\", "/").split("/")
    if "\0" in raw:
        raise ValueError("path contains a NUL byte")
    if raw.startswith(("/", "\\")) or (len(raw) > 1 and raw[1] == ":"):
        raise ValueError(f"path must be relative: {raw[:200]}")
    if ".." in parts:
        raise ValueError(f"path must not contain '..': {raw[:200]}")
    label = "/".join(part for part in parts if part not in ("", "."))
    if not label:
        raise ValueError("path is empty")
    return label


def to_rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def language_of(rel: str) -> str | None:
    return LANGUAGES.get(Path(rel).suffix.lower())


TEST_DIRS = frozenset({"tests", "test", "__tests__", "fixtures", "testdata"})
DOC_SUFFIXES = frozenset({".md", ".rst", ".txt", ".adoc"})


def is_test_file(rel: str) -> bool:
    """A file of a test suite: a test directory, or a test file name in any language."""
    path = Path(rel)
    if any(part.lower() in TEST_DIRS for part in path.parts[:-1]):
        return True
    name = path.name
    stem = name.split(".", 1)[0]
    return (
        name == "conftest.py"
        or stem.startswith("test_")
        or stem.endswith(("_test", "_spec", "Test", "Tests"))
        or ".test." in name
        or ".spec." in name
    )


def is_doc_file(rel: str) -> bool:
    return Path(rel).suffix.lower() in DOC_SUFFIXES


def is_manifest(rel: str) -> bool:
    return Path(rel).name in MANIFESTS


def read_text(root: Path, rel: str) -> str | None:
    """File content, or None when it is missing, too large or binary."""
    try:
        path = resolve_in_root(root, rel)
        if not path.is_file() or path.stat().st_size > MAX_FILE_BYTES:
            return None
        data = path.read_bytes()
    except OSError:
        return None
    if b"\0" in data[:1024]:
        return None
    return data.decode("utf-8", errors="replace")


def _is_candidate(path: Path) -> bool:
    name = path.name
    if name in EXCLUDED_FILE_NAMES or name.endswith(EXCLUDED_FILE_SUFFIXES):
        return False
    if path.suffix.lower() in BINARY_SUFFIXES:
        return False
    try:
        return path.is_file() and path.stat().st_size <= MAX_FILE_BYTES
    except OSError:
        return False


def _ignore_syntax() -> str:
    try:
        pathspec.PathSpec.from_lines("gitignore", [])
    except (KeyError, ValueError, LookupError):
        return "gitwildmatch"
    return "gitignore"


_IGNORE_SYNTAX = _ignore_syntax()


def _load_gitignore(directory: Path) -> pathspec.PathSpec | None:
    gitignore = directory / ".gitignore"
    try:
        lines = gitignore.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None
    return pathspec.PathSpec.from_lines(_IGNORE_SYNTAX, lines)


def _walk(root: Path, start: Path, limit: int, out: list[str]) -> bool:
    """Collect candidate files under start into out. Return True when the limit cut the walk."""
    specs: list[tuple[Path, pathspec.PathSpec]] = []
    ancestor = start
    chain = [ancestor]
    while ancestor != root:
        ancestor = ancestor.parent
        chain.append(ancestor)
    for directory in reversed(chain):
        spec = _load_gitignore(directory)
        if spec:
            specs.append((directory, spec))

    def ignored(path: Path, is_dir: bool, active: list[tuple[Path, pathspec.PathSpec]]) -> bool:
        for base, spec in active:
            rel = path.relative_to(base).as_posix() + ("/" if is_dir else "")
            if spec.match_file(rel):
                return True
        return False

    stack: list[tuple[Path, list[tuple[Path, pathspec.PathSpec]]]] = [(start, specs)]
    while stack:
        directory, active = stack.pop()
        spec = _load_gitignore(directory) if directory != start else None
        if spec:
            active = active + [(directory, spec)]
        try:
            entries = sorted(os.scandir(directory), key=lambda e: e.name)
        except OSError:
            continue
        subdirs: list[Path] = []
        for entry in entries:
            path = Path(entry.path)
            if entry.is_dir(follow_symlinks=False):
                if entry.name in EXCLUDED_DIRS or ignored(path, True, active):
                    continue
                subdirs.append(path)
                continue
            if not entry.is_file(follow_symlinks=True) or ignored(path, False, active):
                continue
            try:
                real = path.resolve()
                real.relative_to(root)
            except (OSError, ValueError):
                continue
            if not _is_candidate(real):
                continue
            if len(out) >= limit:
                return True
            out.append(to_rel(root, path))
        for sub in reversed(subdirs):
            stack.append((sub, active))
    return False


def select_files(
    root: Path, paths: list[str] | None = None, limit: int = MAX_FILES
) -> FileSelection:
    """Files to inspect. paths=None means the whole repo. Raises PathOutsideRootError."""
    out: list[str] = []
    truncated = False
    targets = paths if paths is not None else ["."]
    for raw in targets:
        resolved = resolve_in_root(root, raw)
        if resolved.is_dir():
            truncated = _walk(root, resolved, limit, out) or truncated
        elif _is_candidate(resolved):
            rel = to_rel(root, resolved)
            if rel not in out:
                if len(out) >= limit:
                    truncated = True
                else:
                    out.append(rel)
        if truncated:
            break
    return FileSelection(files=out, truncated=truncated)
