# Quickstart: CLI Wrapper & Skills (v2.8)

## Installation

```bash
pip install adryserage-aetheris>=2.8.0
```

## Basic Usage

### Direct Commands (Unchanged)

```bash
# All existing commands work exactly as before
aetheris analysis
aetheris fix --auto
aetheris pr --url https://github.com/...
```

### Interactive CLI Mode

```bash
# Launch interactive mode
aetheris --cli

# Or short form
aetheris -c
```

**Interactive Session Example:**

```
$ aetheris --cli
🔮 Aetheris Interactive CLI v2.8.0
Provider: gemini | Type /help for commands | /exit to quit

aetheris[gemini]> /
Available commands:
  /analysis    - Run full codebase analysis
  /fix         - Auto-fix detected issues
  /commit      - Create a git commit
  /help        - Show help for a command
  /exit        - Exit interactive mode

aetheris[gemini]> /ana<TAB>
aetheris[gemini]> /analysis --reanalyze

Running analysis on changed files...
✓ 15 files analyzed | 3 issues found

aetheris[gemini]> /help commit
/commit - Create a git commit

Usage: /commit -m "message" [--amend]

Arguments:
  -m, --message  Commit message (required)
  --amend        Amend the previous commit

aetheris[gemini]> /exit
Goodbye!
```

## Provider Selection

```bash
# Use Gemini (default)
aetheris --cli --provider gemini

# Use Claude
aetheris --cli --provider claude

# Switch provider in session (coming in v2.9)
aetheris[gemini]> /provider claude
Switched to: claude
aetheris[claude]>
```

## Agent Skills

Skills are automatically available to the AI when using auto-fix or interactive mode.

### Available Skills

| Skill | Description | Safe |
|-------|-------------|------|
| `read_file` | Read file contents | ✅ |
| `write_file` | Write to files | ⚠️ Confirmation |
| `search_files` | Search with patterns | ✅ |
| `execute_command` | Run shell commands | ⚠️ Confirmation |

### Safe Mode (Default)

```bash
# Safe mode enabled by default
aetheris fix --auto

# AI requests confirmation for dangerous operations:
# 🔒 Skill 'write_file' wants to modify: src/utils.py
# Allow? [y/N]
```

### Unsafe Mode

```bash
# Disable confirmations (use with caution!)
aetheris fix --auto --unsafe

# Or in config.json
{
  "skills": {
    "safe_mode": false
  }
}
```

## Gemini Conductor (Complex Tasks)

For complex multi-step tasks, Gemini uses the Conductor to plan and execute:

```bash
aetheris --cli --provider gemini

aetheris[gemini]> Analyze all security issues and fix the critical ones

🎭 Conductor Planning...
Step 1: Run security analysis
Step 2: Filter critical issues
Step 3: Generate fixes for each
Step 4: Apply fixes with write_file
Step 5: Run tests to verify

Executing plan (5 steps)...
[██████████] 5/5 complete

✓ Fixed 3 critical security issues
  - SQL injection in user_service.py
  - Hardcoded secret in config.py
  - XSS vulnerability in templates/form.html
```

### Verbose Mode

```bash
# See detailed Conductor execution
aetheris --cli --verbose

aetheris[gemini]> Fix all type errors

🎭 Conductor Plan:
┌─────┬──────────────────┬─────────────────┬────────┐
│ Step│ Skill            │ Parameters      │ Status │
├─────┼──────────────────┼─────────────────┼────────┤
│ 1   │ execute_command  │ mypy src/       │ ✓      │
│ 2   │ read_file        │ src/models.py   │ ✓      │
│ 3   │ write_file       │ src/models.py   │ ✓      │
│ ...                                              │
└─────┴──────────────────┴─────────────────┴────────┘
```

## MCP Integration

### Configuration

Add MCP servers to `config.json`:

```json
{
  "mcp": {
    "enabled": true,
    "servers": [
      {
        "name": "filesystem",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "./"]
      },
      {
        "name": "github",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env": {
          "GITHUB_TOKEN": "${GITHUB_TOKEN}"
        }
      }
    ]
  }
}
```

### Using MCP Tools

```bash
aetheris --cli

# MCP tools appear as additional commands
aetheris[gemini]> /
Available commands:
  /analysis       - Run full codebase analysis
  ...
  [MCP: filesystem]
  /fs:read_file   - Read file via MCP
  /fs:list_dir    - List directory
  [MCP: github]
  /gh:create_issue - Create GitHub issue
```

### MCP Resources as Context

```bash
# Resources are automatically included in analysis context
aetheris analysis

# MCP Resources loaded:
#   - file:///project/README.md (via filesystem)
#   - github://repo/issues (via github)
```

## Custom Skills

Create custom skills in `./aetheris-skills/`:

```yaml
# aetheris-skills/run_tests.yaml
name: run_tests
description: "Run project test suite"
parameters:
  - name: pattern
    type: string
    description: "Test file pattern"
    required: false
returns: "Test results"
safe: true
command: "pytest {pattern} --tb=short"
```

```bash
# Load custom skills
aetheris --cli

# Custom skill available
aetheris[gemini]> /run_tests --pattern "tests/unit/*"
```

## Configuration Reference

Full `config.json` for v2.8:

```json
{
  "cli": {
    "default_provider": "gemini",
    "enable_conductor": true,
    "conductor_max_steps": 20
  },
  "skills": {
    "safe_mode": true,
    "custom_skills_path": "./aetheris-skills/",
    "enabled_skills": ["read_file", "write_file", "execute_command", "search_files"]
  },
  "mcp": {
    "enabled": false,
    "servers": [],
    "override_builtins": false,
    "connection_timeout": 2000
  }
}
```

## Troubleshooting

### Autocomplete Not Working

```bash
# Ensure prompt_toolkit is installed
pip install prompt_toolkit>=3.0.0

# Check terminal compatibility
echo $TERM
# Should be: xterm-256color or similar
```

### MCP Connection Failed

```bash
# Test MCP server manually
npx -y @modelcontextprotocol/server-filesystem ./

# Check logs
aetheris --cli --verbose
# Look for: "MCP connection failed: ..."
```

### Skills Not Executing

```bash
# Check if skill is enabled
aetheris --cli
aetheris[gemini]> /skills list

# Enable a skill
# In config.json: "enabled_skills": ["skill_name"]
```
