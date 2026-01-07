# Fix Command

The `aetheris fix` command automatically fixes bugs using Claude Code CLI.

## Prerequisites

Claude Code must be installed:
```bash
npm install -g @anthropic-ai/claude-code
```

## Usage

```bash
aetheris fix [options]
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--test` | Test Claude Code connection | - |
| `--auto` | Automatic mode without confirmations | - |
| `--batch-size`, `-b` | Parallel corrections (recommended: 10) | `1` |
| `--timeout` | Timeout per bug (seconds) | `300` |
| `--terminal` | Open Claude Code in terminal window | - |
| `--severity` | Minimum severity to fix | `medium` |
| `--analyze-first` | Run analysis before fixing | - |
| `--retry-failed` | Retry only previously failed bugs | - |

## Examples

### Test Connection
```bash
aetheris fix --test
```

### Fix from Existing Cache
```bash
aetheris fix
```

### Automatic Mode
```bash
aetheris fix --auto
```

### Parallel Mode (Recommended)
```bash
aetheris fix --auto --batch-size 10
```

### Fix Critical Bugs Only
```bash
aetheris fix --severity critical
```

### Analyze First
```bash
aetheris fix --analyze-first --auto -b 10
```

### Retry Failed
```bash
aetheris fix --retry-failed
```

## Performance

Parallel mode significantly improves speed:

| Bugs | Sequential | Parallel (10) | Speedup |
|------|------------|---------------|---------|
| 10   | ~10 min    | ~2 min        | 5x |
| 50   | ~50 min    | ~10 min       | 5x |
| 100  | ~1h40      | ~20 min       | 5x |

## Execution Modes

| Mode | Description | Command |
|------|-------------|---------|
| Direct (default) | Background execution | `aetheris fix` |
| Terminal | Opens new window | `aetheris fix --terminal` |
| Parallel | Multiple simultaneous | `aetheris fix -b 10` |

## Bug Cache

Bugs are cached in `.bugs_cache.json` with status:
- Fixed bugs with timestamp and summary
- Failed bugs with failure reason
- Unfixed bugs pending correction

## Severity Levels

| Level | Description |
|-------|-------------|
| `critical` | Security vulnerabilities, data loss risks |
| `high` | Major bugs, significant impact |
| `medium` | Standard bugs, moderate impact |
| `low` | Minor issues, cosmetic bugs |
