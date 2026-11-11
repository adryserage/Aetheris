"""Changed files according to git. No shell, bounded by a timeout."""

import re
import subprocess
from pathlib import Path

GIT_TIMEOUT_SECONDS = 20
_SAFE_REV = re.compile(r"^[\w./~^@{}\-]+$")


class GitError(RuntimeError):
    """git failed or the root is not a git repository."""


def _git(root: Path, *args: str) -> list[str]:
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True,
            text=True,
            timeout=GIT_TIMEOUT_SECONDS,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise GitError(f"git could not run: {exc}") from exc
    if proc.returncode != 0:
        raise GitError(proc.stderr.strip() or f"git {args[0]} failed")
    return [line for line in proc.stdout.splitlines() if line]


def changed_files(root: Path, base: str = "HEAD") -> list[str]:
    """Files changed against base plus untracked files, relative to root, sorted."""
    if base.startswith("-") or not _SAFE_REV.match(base):
        raise GitError(f"invalid git revision: {base!r}")
    tracked = _git(root, "diff", "--name-only", "--relative", "--diff-filter=ACMR", base, "--")
    untracked = _git(root, "ls-files", "--others", "--exclude-standard")
    return sorted(set(tracked) | set(untracked))
