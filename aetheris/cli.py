"""The `aetheris` command: installs the MCP server into AI clients and explains the move from 3.x."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from aetheris import __version__

SERVER_NAME = "aetheris"
PACKAGE = "adryserage-aetheris"

LEGACY_COMMANDS = (
    "analysis",
    "fix",
    "pr",
    "pr-gen",
    "issues",
    "user-story",
    "stats",
    "run",
    "cleanup",
    "validate-package",
)

OVERVIEW = f"""Aetheris {__version__}: code review rules and checks for your AI coding assistant.

Aetheris 4 is an MCP server. Your assistant (Claude Code, Cursor, Claude Desktop) calls it
for the rules of 10 review agents and for checks that need no AI: secrets, known
vulnerabilities (OSV), metrics, circular imports and code patterns. It needs no API key.

  aetheris install     add the server to Claude Code, Cursor and Claude Desktop
  aetheris uninstall   remove it
  aetheris serve       run the server over stdio (what your assistant launches)

Then ask your assistant: "review my changes with Aetheris".
"""

LEGACY_NOTICE = """`aetheris {command}` was removed in Aetheris 4.

Aetheris 4 no longer calls Gemini, OpenAI or Claude with your API key. It is now an MCP
server: your AI coding assistant runs the review with the rules and checks Aetheris serves.

  Keep the 3.x command line:  pip install "adryserage-aetheris==3.0.0"
  Move to Aetheris 4:         aetheris install, then ask your assistant for a review

Details: https://github.com/adryserage/aetheris/blob/main/CHANGELOG.md
"""


@dataclass(frozen=True)
class JsonClient:
    """A client configured through a JSON file holding an `mcpServers` table."""

    id: str
    name: str
    user_config: Callable[[], Path]
    project_config: Callable[[Path], Path] | None

    def config_path(self, project: Path | None) -> Path | None:
        if project is None:
            return self.user_config()
        return self.project_config(project) if self.project_config else None


def _claude_desktop_config() -> Path:
    if sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    elif sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / "Claude" / "claude_desktop_config.json"


JSON_CLIENTS = {
    "cursor": JsonClient(
        id="cursor",
        name="Cursor",
        user_config=lambda: Path.home() / ".cursor" / "mcp.json",
        project_config=lambda root: root / ".cursor" / "mcp.json",
    ),
    "claude-desktop": JsonClient(
        id="claude-desktop",
        name="Claude Desktop",
        user_config=_claude_desktop_config,
        project_config=None,
    ),
}
CLIENT_IDS = ("claude-code", *JSON_CLIENTS)


def server_entry() -> dict[str, object]:
    """The launch command clients store. Desktop apps often lack the shell PATH, so the
    absolute path of `uvx` is used when it can be found."""
    return {"command": shutil.which("uvx") or "uvx", "args": [PACKAGE]}


def _read_config(path: Path) -> dict[str, object]:
    if not path.exists() or not path.read_text(encoding="utf-8").strip():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} does not hold a JSON object")
    return data


def _write_config(path: Path, data: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def install_json(client: JsonClient, project: Path | None) -> str:
    path = client.config_path(project)
    if path is None:
        return f"{client.name}: skipped, it has no per-project configuration"
    try:
        data = _read_config(path)
    except (ValueError, OSError) as exc:
        return f"{client.name}: not changed, cannot read {path} as JSON ({exc})"
    servers = data.setdefault("mcpServers", {})
    if not isinstance(servers, dict):
        return f"{client.name}: not changed, `mcpServers` in {path} is not an object"
    entry = server_entry()
    if servers.get(SERVER_NAME) == entry:
        return f"{client.name}: already installed in {path}"
    servers[SERVER_NAME] = entry
    _write_config(path, data)
    return f"{client.name}: installed in {path}"


def uninstall_json(client: JsonClient, project: Path | None) -> str:
    path = client.config_path(project)
    if path is None or not path.exists():
        return f"{client.name}: nothing to remove"
    try:
        data = _read_config(path)
    except (ValueError, OSError) as exc:
        return f"{client.name}: not changed, cannot read {path} as JSON ({exc})"
    servers = data.get("mcpServers")
    if not isinstance(servers, dict) or SERVER_NAME not in servers:
        return f"{client.name}: nothing to remove"
    del servers[SERVER_NAME]
    _write_config(path, data)
    return f"{client.name}: removed from {path}"


def _claude(*args: str) -> subprocess.CompletedProcess[str] | None:
    exe = shutil.which("claude")
    if exe is None:
        return None
    try:
        return subprocess.run([exe, "mcp", *args], capture_output=True, text=True, timeout=60)
    except (subprocess.TimeoutExpired, OSError) as exc:
        return subprocess.CompletedProcess([exe, "mcp", *args], 1, "", str(exc))


def install_claude_code(project: Path | None) -> str:
    scope = "project" if project else "user"
    manual = f"claude mcp add --scope {scope} {SERVER_NAME} -- uvx {PACKAGE}"
    found = _claude("get", SERVER_NAME)
    if found is None:
        return f"Claude Code: `claude` not found, run this yourself: {manual}"
    if found.returncode == 0:
        return "Claude Code: already installed"
    done = _claude("add", "--scope", scope, SERVER_NAME, "--", "uvx", PACKAGE)
    if done is None or done.returncode != 0:
        detail = (done.stderr or done.stdout).strip() if done else ""
        return f"Claude Code: failed ({detail}), run this yourself: {manual}"
    return f"Claude Code: installed ({scope} scope)"


def uninstall_claude_code(project: Path | None) -> str:
    scope = "project" if project else "user"
    done = _claude("remove", "--scope", scope, SERVER_NAME)
    if done is None:
        return "Claude Code: `claude` not found, nothing removed"
    if done.returncode != 0:
        return "Claude Code: nothing to remove"
    return f"Claude Code: removed ({scope} scope)"


def _detected(client_id: str) -> bool:
    if client_id == "claude-code":
        return shutil.which("claude") is not None
    path = JSON_CLIENTS[client_id].user_config()
    return path.parent.exists()


def _targets(choice: str) -> list[str]:
    if choice != "all":
        return [choice]
    return [c for c in CLIENT_IDS if _detected(c)]


def run_install(choice: str, project: Path | None, remove: bool = False) -> int:
    targets = _targets(choice)
    if not targets:
        print("No supported client found (Claude Code, Cursor, Claude Desktop).")
        print(f"Add this MCP server to your client: uvx {PACKAGE} (stdio).")
        return 1
    for client_id in targets:
        if client_id == "claude-code":
            line = uninstall_claude_code(project) if remove else install_claude_code(project)
        else:
            client = JSON_CLIENTS[client_id]
            line = uninstall_json(client, project) if remove else install_json(client, project)
        print(line)
    if not remove:
        print("Restart the client, then ask it: review my changes with Aetheris.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aetheris", description=OVERVIEW.splitlines()[0])
    parser.add_argument("--version", action="version", version=f"aetheris {__version__}")
    sub = parser.add_subparsers(dest="command")
    for name, help_text in (
        ("install", "add the MCP server to your AI clients"),
        ("uninstall", "remove the MCP server from your AI clients"),
    ):
        cmd = sub.add_parser(name, help=help_text)
        cmd.add_argument("--client", choices=("all", *CLIENT_IDS), default="all")
        cmd.add_argument(
            "--project",
            action="store_true",
            help="use the current project's configuration instead of the user's",
        )
    sub.add_parser("serve", help="run the MCP server over stdio")
    return parser


def main(argv: list[str] | None = None) -> int:
    args_in = sys.argv[1:] if argv is None else argv
    if args_in and (args_in[0] in LEGACY_COMMANDS or args_in[0] in ("--cli", "-c")):
        print(LEGACY_NOTICE.format(command=args_in[0]), file=sys.stderr)
        return 2
    args = build_parser().parse_args(args_in)
    if args.command is None:
        print(OVERVIEW)
        return 0
    if args.command == "serve":
        from aetheris.server import main as serve

        serve()
        return 0
    project = Path.cwd() if args.project else None
    return run_install(args.client, project, remove=args.command == "uninstall")


def entry() -> None:
    sys.exit(main())
