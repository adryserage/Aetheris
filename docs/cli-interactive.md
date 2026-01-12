# CLI Interactive Mode

Aetheris v3.0 introduces an interactive CLI mode with REPL interface, command autocomplete, and multi-provider support.

## Starting Interactive Mode

```bash
# Launch interactive mode
aetheris --cli

# Or use short form
aetheris -c
```

## Interface Overview

When you start interactive mode, you'll see:

```
╭────────────────────────────────────────╮
│         Welcome to Aetheris            │
│      Interactive CLI Mode v3.0         │
│                                        │
│  Type /help for available commands     │
│  Press Tab for autocomplete            │
│  Type /exit or Ctrl+D to quit          │
╰────────────────────────────────────────╯

aetheris[gemini]> _
```

The prompt shows your current AI provider in brackets.

## Built-in Commands

### Core Commands

| Command | Alias | Description |
|---------|-------|-------------|
| `/analysis` | `/analyze` | Run code analysis on current project |
| `/fix` | - | Generate fix suggestions for issues |
| `/pr` | `/review-pr` | Review a pull request |
| `/issues` | - | List GitHub issues |
| `/stats` | - | Show analysis statistics |
| `/settings` | `/config` | Open settings interface |

### Session Commands

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/clear` | Clear the screen |
| `/provider <name>` | Switch AI provider |
| `/exit` | Exit interactive mode |

## Provider-Specific Commands

### Claude Mode

When using Claude as your provider, additional commands are available:

| Command | Description |
|---------|-------------|
| `/commit` | Generate commit message |
| `/review` | Review code changes |
| `/explain` | Explain code selection |
| `/refactor` | Suggest refactoring |
| `/test` | Generate tests |

### Gemini Mode

When using Gemini as your provider:

| Command | Description |
|---------|-------------|
| `/chat` | Free-form chat |
| `/code` | Code generation |
| `/plan` | Create execution plan |

## Autocomplete

The CLI provides intelligent autocomplete:

- **Tab**: Complete current command or argument
- **Tab Tab**: Show all completions
- **Arrow Up/Down**: Navigate command history

### Autocomplete Features

1. **Command Completion**: Type `/` and press Tab to see all commands
2. **Argument Completion**: Commands with arguments show suggestions
3. **File Path Completion**: File-related commands complete paths
4. **Typo Correction**: Unknown commands suggest similar ones

Example:
```
aetheris[gemini]> /analy<Tab>
→ /analysis

aetheris[gemini]> /exot
Unknown command: /exot
Did you mean: /exit?
```

## Natural Language Queries

You can type natural language queries directly:

```
aetheris[gemini]> Analyze the security of src/auth/
```

The AI will interpret your request and execute appropriate actions.

## Command History

- History is saved between sessions in `~/.aetheris/history`
- Use Up/Down arrows to navigate history
- History is per-user, not per-project

## Configuration

Interactive mode respects your `config.json` settings:

```json
{
  "cli": {
    "default_provider": "gemini",
    "history_size": 1000,
    "autocomplete_delay_ms": 100
  }
}
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+C` | Cancel current input |
| `Ctrl+D` | Exit (same as /exit) |
| `Ctrl+L` | Clear screen |
| `Ctrl+R` | Search history |
| `Tab` | Autocomplete |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Normal exit |
| 1 | Error occurred |
| 130 | Interrupted (Ctrl+C) |

## Examples

### Run Analysis

```
aetheris[gemini]> /analysis
Running analysis on current project...
```

### Switch Provider

```
aetheris[gemini]> /provider claude
Provider switched to: claude
aetheris[claude]> _
```

### Get Help

```
aetheris[gemini]> /help
Available commands:
  /analysis   - Run code analysis
  /fix        - Generate fix suggestions
  ...
```

## Troubleshooting

### "prompt_toolkit not found"

Install the required dependency:
```bash
pip install prompt_toolkit>=3.0.0
```

### History not saving

Ensure `~/.aetheris/` directory exists and is writable:
```bash
mkdir -p ~/.aetheris
chmod 700 ~/.aetheris
```

### Autocomplete slow

Adjust the delay in config:
```json
{
  "cli": {
    "autocomplete_delay_ms": 50
  }
}
```
