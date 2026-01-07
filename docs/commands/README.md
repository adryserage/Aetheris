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

## Next Steps

- [Installation](/docs/installation.md) - Setup guide
- [Configuration](/docs/configuration.md) - Environment variables
- [AI Providers](/docs/ai-providers.md) - Provider configuration
