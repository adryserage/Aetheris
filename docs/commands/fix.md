# Fix Command

The `aetheris fix` command automatically fixes bugs using Claude Code CLI.

## Prerequisites

Claude Code must be installed:
```bash
npm install -g @anthropic-ai/claude-code@^1
```

> **Note**: The `@^1` version constraint ensures compatibility with Aetheris while allowing minor updates. Check the [Claude Code releases](https://www.npmjs.com/package/@anthropic-ai/claude-code) for the latest compatible version.

## Usage

```bash
aetheris fix [options]
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--test` | Test Claude Code connection | `false` |
| `--auto` | Automatic mode without confirmations | `false` |
| `--batch-size`, `-b` | Parallel corrections (recommended: 10) | `1` |
| `--timeout` | Timeout per bug (seconds) | `300` |
| `--terminal` | Open a single terminal window showing Claude Code progress (blocks parallel execution; use for debugging) | `false` |
| `--severity` | Minimum severity to fix | `medium` |
| `--analyze-first` | Run analysis before fixing | `false` |
| `--retry-failed` | Retry only previously failed bugs | `false` |

## Security Warning

> ⚠️ **IMPORTANT**: The `--auto` option applies AI-generated fixes without confirmation. AI-generated code may contain:
> - **Functional regressions**: Logic errors or unintended behavior changes
> - **Security vulnerabilities**: Hallucinations that introduce new attack vectors
> - **Incomplete fixes**: Partial solutions that mask underlying issues
>
> **Best practices:**
> 1. Always review AI-generated corrections before deployment
> 2. Run your test suite after automatic fixes
> 3. Use version control to track changes (`git diff` before committing)
> 4. Consider using `--auto` only in non-production environments first

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
| Direct (default) | Silent background execution, progress shown in current terminal | `aetheris fix` |
| Terminal | Opens a single interactive terminal window for debugging; processes bugs sequentially (incompatible with `--batch-size > 1`) | `aetheris fix --terminal` |
| Parallel | Runs multiple fixes simultaneously in background; no additional windows opened | `aetheris fix -b 10` |

> **Note**: The `--terminal` flag is intended for debugging individual fixes. It opens only one window and forces sequential processing. For production use, prefer the default (Direct) or Parallel modes.

## Bug Cache

Bugs are cached in `.bugs_cache.json` with status:
- Fixed bugs with timestamp and summary
- Failed bugs with failure reason
- Unfixed bugs pending correction

### Missing or Corrupted Cache

If `.bugs_cache.json` is missing or corrupted:

| Scenario | Behavior |
|----------|----------|
| Cache missing | Command exits with error. Use `--analyze-first` to generate cache, or run `aetheris analysis` first. |
| Cache corrupted (invalid JSON) | Command exits with error. Delete the file and regenerate with `--analyze-first` or `aetheris analysis`. |
| Cache empty (no bugs) | Command reports "No bugs to fix" and exits successfully. |

**Recommended workflow:**
```bash
# First run: analyze and fix in one command
aetheris fix --analyze-first --auto -b 10

# Subsequent runs: fix from existing cache
aetheris fix --auto -b 10
```

## Severity Levels

| Level | Description |
|-------|-------------|
| `critical` | Security vulnerabilities, data loss risks |
| `high` | Major bugs, significant impact |
| `medium` | Standard bugs, moderate impact |
| `low` | Minor issues, cosmetic bugs |

## Error Handling

The `aetheris fix` command handles various error scenarios gracefully:

### Authentication Errors

| Error | Cause | Resolution |
|-------|-------|------------|
| `Claude Code not authenticated` | Missing or invalid API key | Run `claude login` to authenticate |
| `Invalid API key` | Expired or revoked key | Generate a new key at [console.anthropic.com](https://console.anthropic.com) |
| `Authentication timeout` | Network issues during auth | Check internet connection and retry |

When authentication fails, the command will:
1. Display a clear error message with the failure reason
2. Skip the current bug and mark it as `failed` in the cache
3. Continue with remaining bugs (in batch mode)
4. Exit with code `1` if all fixes fail

### Rate Limits and Quota

| Error | Cause | Resolution |
|-------|-------|------------|
| `Rate limit exceeded` | Too many requests per minute | Reduce `--batch-size` or wait 1 minute |
| `Quota exceeded` | Monthly API quota depleted | Upgrade plan or wait for quota reset |
| `Token limit exceeded` | Single request too large | Split large files or reduce context |

Rate limit handling behavior:
- **Automatic retry**: The command retries with exponential backoff (up to 3 attempts)
- **Batch adaptation**: In parallel mode, failed requests are queued for retry
- **Graceful degradation**: If quota is exceeded, remaining bugs are marked as `pending` for later retry with `--retry-failed`

### Connection Errors

| Error | Cause | Resolution |
|-------|-------|------------|
| `Connection refused` | Claude Code CLI not running | Ensure Claude Code is installed and accessible |
| `Timeout` | Request exceeded `--timeout` value | Increase timeout or simplify the bug |
| `Network error` | Internet connectivity issues | Check network connection |

### Exit Codes

| Code | Meaning |
|------|---------|
| `0` | All bugs fixed successfully |
| `1` | Some bugs failed (partial success) |
| `2` | Authentication or configuration error |
| `3` | Claude Code CLI not found |

### Troubleshooting

```bash
# Test Claude Code connection and authentication
aetheris fix --test

# View detailed error logs
aetheris fix --auto 2>&1 | tee fix.log

# Retry only failed bugs after resolving issues
aetheris fix --retry-failed
```
