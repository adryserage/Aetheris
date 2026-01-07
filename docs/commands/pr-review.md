# PR Review Command

The `aetheris pr` command analyzes GitHub Pull Requests with AI and posts review comments.

## Prerequisites

GitHub CLI must be installed and authenticated:
```bash
# Install
brew install gh        # macOS
sudo apt install gh    # Ubuntu/Debian
winget install gh      # Windows

# Authenticate
gh auth login
```

## Usage

```bash
aetheris pr [options]
```

## Options

| Option | Description |
|--------|-------------|
| `--url URL` | Full PR URL |
| `--repo REPO` | Repository (owner/repo format) |
| `--pr NUM` | PR number (with --repo) |
| `--providers LIST` | AI providers (comma-separated) |
| `--consensus` | Report only issues found by ALL providers (default) |
| `--no-consensus` | Report all issues from each provider |
| `--dry-run` | Analyze without posting comments |
| `--severity LEVEL` | Minimum severity filter |
| `--no-inline` | Summary only, no inline comments |
| `--output FILE` | Save report to file |
| `--auto-fix` | Offer to fix if it's your PR |

## Examples

### Analyze by URL
```bash
aetheris pr --url https://github.com/owner/repo/pull/123
```

### Analyze by Repo and Number
```bash
aetheris pr --repo owner/repo --pr 123
```

### Multi-Provider Consensus
```bash
aetheris pr --url https://... --providers gemini,claude
```

### All Three Providers
```bash
aetheris pr --url https://... --providers gemini,claude,openai
```

### Disable Consensus
```bash
aetheris pr --url https://... --providers gemini,claude --no-consensus
```

### Dry Run
```bash
aetheris pr --url https://... --dry-run
```

### Filter by Severity
```bash
aetheris pr --url https://... --severity high
```

### Save Report
```bash
aetheris pr --url https://... --output review.md
```

## Consensus Mode

When using multiple providers, **consensus mode** (default):
- Only reports issues found by ALL providers
- Reduces false positives
- Higher confidence in results

## Issue Types

| Type | Description |
|------|-------------|
| `security` | Vulnerabilities (injection, XSS, etc.) |
| `bug` | Potential bugs and logic errors |
| `performance` | Performance issues |
| `logic` | Business logic errors |
| `style` | Code convention violations |
| `documentation` | Missing/incorrect documentation |
| `test` | Missing or insufficient tests |
| `best_practice` | Best practice violations |

## Severity Levels

| Level | Description |
|-------|-------------|
| `critical` | Must fix before merge |
| `high` | Should fix before merge |
| `medium` | Consider fixing |
| `low` | Nice to have |
| `info` | Informational only |
