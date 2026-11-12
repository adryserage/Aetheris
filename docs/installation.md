# Installation

Aetheris runs locally through [`uvx`](https://docs.astral.sh/uv/), which comes with uv. There is no account to create and no API key to set.

## Automatic setup

```bash
uvx --from adryserage-aetheris aetheris install
```

The command adds the server to every supported client it finds: Claude Code, Cursor and Claude Desktop. Restart the client afterwards, then ask it: "review my changes with Aetheris".

| Option | Effect |
| --- | --- |
| `--client <id>` | Install in one client only: `claude-code`, `cursor` or `claude-desktop`. The default is `all`, which means every client found on this machine. |
| `--project` | Write the configuration of the current directory instead of your user configuration. Claude Code uses its project scope and Cursor uses `.cursor/mcp.json`. Claude Desktop has no per-project file, so it is skipped. |

Remove the server with the same options:

```bash
uvx --from adryserage-aetheris aetheris uninstall
```

What each client gets:

- Claude Code: the installer runs `claude mcp add` (scope `user`, or `project` with `--project`). If the `claude` command is not on your path, it prints the command for you to run.
- Cursor: an `aetheris` entry in `~/.cursor/mcp.json`, or `.cursor/mcp.json` with `--project`.
- Claude Desktop: an `aetheris` entry in `claude_desktop_config.json` (`~/Library/Application Support/Claude/` on macOS, `%APPDATA%\Claude\` on Windows, `~/.config/Claude/` on Linux).

The installer only adds or removes the `aetheris` entry. It leaves the rest of the file alone and never rewrites a file it cannot parse as JSON. It stores the absolute path of `uvx` when it finds one, because desktop apps often start without your shell path.

## Manual setup

### Claude Code

```bash
claude mcp add aetheris -- uvx adryserage-aetheris
```

Add `--scope project` to share the server with the project, or `--scope user` for all your projects.

### Cursor

Add this to `.cursor/mcp.json` in your project, or to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "aetheris": {
      "command": "uvx",
      "args": ["adryserage-aetheris"]
    }
  }
}
```

### Other MCP clients

Run `uvx adryserage-aetheris` as a stdio server. The same command is available as `aetheris serve` when the package is installed.

## Choosing the project directory

The server reads files under one directory, the project root. By default that is the directory the client starts it in. Set `AETHERIS_ROOT` to use another one. Every path an assistant passes to a tool is resolved inside this root, and a path that escapes it is refused.

In a JSON client, add an `env` table to the entry:

```json
{
  "mcpServers": {
    "aetheris": {
      "command": "uvx",
      "args": ["adryserage-aetheris"],
      "env": { "AETHERIS_ROOT": "/path/to/project" }
    }
  }
}
```

## Running from a local checkout

To try a clone of the repository, point `uvx` at the folder with `--from`:

```bash
uvx --from /path/to/aetheris aetheris install
```

The entry that `install` stores still names the published package. To make a client run your checkout, configure it by hand with `uvx --from /path/to/aetheris adryserage-aetheris` as the command line:

```bash
claude mcp add aetheris -- uvx --from /path/to/aetheris adryserage-aetheris
```

## Check that it works

Ask your assistant to list the Aetheris tools, or run `aetheris --version` in a terminal. The server exposes six tools, described in [Tools](tools.md).
