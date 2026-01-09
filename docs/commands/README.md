# Commands Reference

Aetheris provides several CLI commands for code analysis and automation.

## Available Commands

| Command | Description | Documentation |
|---------|-------------|---------------|
| `aetheris analysis` | Full codebase analysis | [analysis.md](./analysis.md) |
| `aetheris fix` | Fix bugs with Claude Code | [fix.md](./fix.md) |
| `aetheris pr` | Review GitHub Pull Requests | [pr-review.md](./pr-review.md) |
| `aetheris user-story` | Analyze user flows | [user-story.md](./user-story.md) |
| `aetheris issues` | Create GitHub issues from analysis | [issues.md](./issues.md) |
| `aetheris pr-gen` | Generate PRs with AI fixes | [pr-gen.md](./pr-gen.md) |
| `aetheris cleanup` | Remove artifacts before packaging | [cleanup.md](./cleanup.md) |
| `aetheris validate-package` | Pre-publication security check | [validate-package.md](./validate-package.md) |

## Quick Reference

```bash
# Get help for any command
aetheris --help
aetheris <command> --help

# Version
aetheris --version
```

## Common Workflows

### Full Analysis
```bash
aetheris analysis
```

### Incremental Analysis (v2.6.1)
```bash
# Reanalyze only files changed since last analysis
aetheris analysis --reanalyze

# Short form
aetheris analysis -r

# Combined with timeout for large codebases
aetheris analysis -r --timeout 30m
```

### Long-Running Analysis (v2.6.1)
```bash
# Set timeout (supports: 30m, 2h, etc.)
aetheris analysis --timeout 2h

# Unlimited timeout (no auto-termination)
aetheris analysis --timeout 0

# Heartbeat monitor runs automatically every 10 minutes
```

### Analyze and Fix
```bash
# --analyze-first: Run analysis before fixing (skips if recent analysis exists)
# --auto: Automatically apply fixes without confirmation prompts
aetheris fix --analyze-first --auto
```

### PR Review
```bash
# --url: GitHub PR URL to review (required)
aetheris pr --url https://github.com/owner/repo/pull/123
```

### Create Issues from Analysis
```bash
# Creates GitHub issues from the latest analysis report
aetheris issues
```

### Generate Fix PRs
```bash
# --link-issues: Link generated PRs to existing GitHub issues
aetheris pr-gen --link-issues
```

### Pre-Release Validation (v2.6.2)
```bash
# Preview what would be cleaned
aetheris cleanup --dry-run

# Clean artifacts before packaging
aetheris cleanup --deep

# Validate package for secrets and excluded files
aetheris validate-package

# Auto-fix validation issues
aetheris validate-package --fix
```

## Next Steps

- [Installation](/docs/installation.md) - Setup guide
- [Configuration](/docs/configuration.md) - Environment variables
- [AI Providers](/docs/ai-providers.md) - Provider configuration
