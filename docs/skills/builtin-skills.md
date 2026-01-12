# Built-in Skills

Aetheris includes these built-in skills that AI agents can invoke.

## read_file

Read the contents of a file.

### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `path` | string | Yes | Path to the file to read |
| `start_line` | integer | No | First line to read (1-indexed) |
| `end_line` | integer | No | Last line to read (inclusive) |

### Example

```json
{
  "skill": "read_file",
  "arguments": {
    "path": "src/main.py",
    "start_line": 1,
    "end_line": 50
  }
}
```

### Security

- Path is validated against sandbox (project directory)
- Symlinks are resolved and checked
- Binary files return an error

---

## write_file

Write content to a file.

### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `path` | string | Yes | Path to the file to write |
| `content` | string | Yes | Content to write |
| `mode` | string | No | Write mode: "overwrite" (default) or "append" |

### Example

```json
{
  "skill": "write_file",
  "arguments": {
    "path": "output.txt",
    "content": "Hello, World!",
    "mode": "overwrite"
  }
}
```

### Security

- **Requires confirmation** before execution
- Path is validated against sandbox
- Creates parent directories if needed
- Maximum file size: 10MB

---

## search_files

Search for files matching a pattern.

### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `pattern` | string | Yes | Glob pattern (e.g., "*.py", "src/**/*.ts") |
| `path` | string | No | Base directory (default: project root) |
| `content` | string | No | Regex to search within files |
| `max_results` | integer | No | Maximum results (default: 100) |

### Example

```json
{
  "skill": "search_files",
  "arguments": {
    "pattern": "**/*.py",
    "content": "def main\\(",
    "max_results": 20
  }
}
```

### Returns

List of matching files with optional content matches:

```json
{
  "files": [
    {
      "path": "src/main.py",
      "matches": [
        {"line": 42, "content": "def main():"}
      ]
    }
  ]
}
```

### Security

- Path restricted to sandbox
- Large directories may be truncated

---

## execute_command

Execute a shell command.

### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `command` | string | Yes | Command to execute |
| `cwd` | string | No | Working directory |
| `timeout` | integer | No | Timeout in seconds (default: 60) |

### Example

```json
{
  "skill": "execute_command",
  "arguments": {
    "command": "python -m pytest tests/",
    "timeout": 120
  }
}
```

### Returns

```json
{
  "stdout": "...",
  "stderr": "...",
  "return_code": 0,
  "timed_out": false
}
```

### Security

- **Requires confirmation** before execution
- Blocked commands:
  - `rm -rf /`, `rm -rf ~`
  - `sudo rm`, `sudo dd`
  - Format/partition commands
  - Network attack commands
- Dangerous patterns trigger extra warnings:
  - Commands containing `sudo`
  - Commands with `chmod 777`
  - Commands with `>` redirect to system paths
- Working directory restricted to sandbox

---

## Skill Confirmation

Skills marked with "Requires confirmation" will prompt the user:

```
╭──────────────────────────────────────────────╮
│  Skill Confirmation Required                 │
├──────────────────────────────────────────────┤
│  Skill: write_file                           │
│  Path: src/config.py                         │
│  Action: Overwrite file with 42 lines        │
│                                              │
│  Allow this action? [y/N]                    │
╰──────────────────────────────────────────────╯
```

## Sandbox Configuration

Configure sandbox behavior in `config.json`:

```json
{
  "skills": {
    "sandbox_enabled": true,
    "sandbox_root": ".",
    "allowed_paths": [
      "src/",
      "tests/",
      "docs/"
    ],
    "blocked_paths": [
      ".git/",
      ".env",
      "secrets/"
    ]
  }
}
```

## Disabling Skills

To disable specific skills:

```json
{
  "skills": {
    "disabled_skills": ["execute_command"]
  }
}
```

This prevents the AI from invoking that skill entirely.
