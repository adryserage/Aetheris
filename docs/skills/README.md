# Aetheris Skills System

Aetheris v3.0 introduces a Skills system that enables AI agents to interact with files, execute commands, and perform actions.

## Overview

Skills are executable capabilities that AI models can invoke through their respective tool/function calling interfaces:

- **Claude**: Tool Use format
- **Gemini**: Function Calling format
- **OpenAI**: Function Calling format (planned)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Provider                              │
│                (Claude/Gemini/OpenAI)                       │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  Provider Adapter                           │
│         (Converts between formats)                          │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Skill Registry                            │
│   ┌─────────────┬─────────────┬─────────────────────────┐  │
│   │  Built-in   │   Custom    │   MCP Tools             │  │
│   │  Skills     │   Skills    │   (via Bridge)          │  │
│   └─────────────┴─────────────┴─────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Skill Types

### 1. Built-in Skills

Pre-defined skills that come with Aetheris:

| Skill | Description | Requires Confirmation |
|-------|-------------|----------------------|
| `read_file` | Read file contents | No |
| `write_file` | Write/modify files | Yes |
| `search_files` | Search for files | No |
| `execute_command` | Run shell commands | Yes |

See [builtin-skills.md](./builtin-skills.md) for details.

### 2. Custom Skills

User-defined skills via YAML configuration:

```yaml
skills:
  - name: run_tests
    description: Run project tests
    command: pytest {path}
    parameters:
      - name: path
        type: string
        description: Test path
        default: tests/
```

See [custom-skills.md](./custom-skills.md) for details.

### 3. MCP Tools

Skills imported from MCP (Model Context Protocol) servers:

```json
{
  "mcp": {
    "servers": [
      {
        "name": "filesystem",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem"]
      }
    ]
  }
}
```

See [../mcp-integration.md](../mcp-integration.md) for details.

## Safety Features

### Sandbox Validation

All file operations are sandboxed to the project directory by default:

```python
# Allowed
skill.execute({"path": "src/main.py"})

# Blocked (outside project)
skill.execute({"path": "/etc/passwd"})
```

### Confirmation Prompts

Dangerous operations require user confirmation:

```
Skill 'write_file' wants to modify: src/config.py
Allow? [y/N]:
```

### Blocked Commands

Certain shell commands are blocked:

- `rm -rf /`
- `sudo rm`
- Format/partition commands
- Network attacks

## Provider Adapters

Adapters convert skills to provider-specific formats:

### Claude (Tool Use)

```json
{
  "name": "read_file",
  "description": "Read a file's contents",
  "input_schema": {
    "type": "object",
    "properties": {
      "path": {"type": "string"}
    },
    "required": ["path"]
  }
}
```

### Gemini (Function Calling)

```json
{
  "name": "read_file",
  "description": "Read a file's contents",
  "parameters": {
    "type": "object",
    "properties": {
      "path": {"type": "string"}
    },
    "required": ["path"]
  }
}
```

## Configuration

Configure skills in `config.json`:

```json
{
  "skills": {
    "enabled": true,
    "custom_skills_path": "./aetheris-skills/",
    "sandbox_enabled": true,
    "confirmation_required": ["write_file", "execute_command"],
    "disabled_skills": []
  }
}
```

## Quick Start

1. **Enable skills** in your config
2. **Start interactive mode**: `aetheris --cli`
3. **Ask the AI** to perform actions:
   ```
   aetheris[gemini]> Read the README.md file
   ```
4. **Confirm** any write operations when prompted

## Documentation Index

- [Built-in Skills](./builtin-skills.md)
- [Custom Skills](./custom-skills.md)
- [MCP Integration](../mcp-integration.md)
