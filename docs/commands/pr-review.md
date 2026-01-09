# PR Review Command

The `aetheris pr` command analyzes GitHub Pull Requests with AI and posts review comments.

## Prerequisites

### GitHub CLI

GitHub CLI must be installed and authenticated:
```bash
# Install
brew install gh        # macOS
sudo apt install gh    # Ubuntu/Debian
winget install gh      # Windows

# Authenticate
gh auth login
```

#### Required GitHub Permissions

The `aetheris pr` command requires the following minimum permission scopes:

| Scope | Purpose |
|-------|---------|
| `repo` | Read PR content, diff, and files; post review comments |
| `read:org` | Access PRs in organization repositories (if applicable) |

When running `gh auth login`, select **HTTPS** as the protocol and authenticate via browser. The default scopes granted by `gh auth login` are sufficient for most use cases.

To verify your current scopes:
```bash
gh auth status
```

> **Tip**: If you only need to review public repositories, the `public_repo` scope (subset of `repo`) is sufficient.

### AI Provider Configuration

Configure at least one AI provider by setting the appropriate environment variable in your `.env` file or shell:

| Provider | Environment Variable | How to Get |
|----------|---------------------|------------|
| Gemini | `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com/apikey) |
| OpenAI | `OPENAI_API_KEY` | [OpenAI Platform](https://platform.openai.com/api-keys) |
| Claude | `ANTHROPIC_API_KEY` | [Anthropic Console](https://console.anthropic.com/settings/keys) |

**Example `.env` file:**
```bash
# Choose one or more providers
AI_PROVIDER=gemini                    # Default provider (gemini, openai, or claude)
GEMINI_API_KEY=your-gemini-key-here
OPENAI_API_KEY=your-openai-key-here   # Optional: for multi-provider reviews
ANTHROPIC_API_KEY=your-claude-key     # Optional: for multi-provider reviews
```

> **Tip**: For multi-provider consensus reviews (`--providers gemini,claude,openai`), configure all providers you intend to use.

## Usage

```bash
aetheris pr [options]
```

## Options

### PR Identification (mutually exclusive)

You must specify the PR using **one** of these methods:

| Option | Description |
|--------|-------------|
| `--url URL` | Full PR URL |
| `--repo REPO` + `--pr NUM` | Repository and PR number |

> **Note**: `--url` and `--repo`/`--pr` are mutually exclusive. Use either `--url` alone, or `--repo` together with `--pr`. Providing both will result in an error.

### Analysis Options

| Option | Description | Default |
|--------|-------------|---------|
| `--providers LIST` | AI providers to use (comma-separated, e.g., `gemini,claude,openai`) | `gemini` |
| `--consensus` | Report only issues found by ALL providers | `true` |
| `--no-consensus` | Report all issues from each provider | `false` |
| `--dry-run` | Analyze without posting comments | `false` |
| `--severity LEVEL` | Minimum severity filter | `low` |
| `--no-inline` | Summary only, no inline comments | `false` |
| `--output FILE` | Save report to file (Markdown format, use `.md` extension) | none |
| `--auto-fix` | Offer to fix if it's your PR | `false` |

> **Note**: When `--auto-fix` is combined with `--dry-run`, the analysis runs in simulation mode: issues are identified and fixes are **proposed** but **not applied**. No comments are posted and no code is modified. This is useful for previewing what fixes would be suggested before running the actual auto-fix.

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

### Preview Auto-Fix (Dry Run)
```bash
aetheris pr --url https://... --auto-fix --dry-run
```
This shows what fixes would be suggested without applying them or posting comments.

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
