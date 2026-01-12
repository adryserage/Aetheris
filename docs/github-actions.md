# GitHub Actions Integration (v2.13)

This guide shows how to integrate Aetheris into your GitHub Actions CI/CD pipeline for automated code analysis.

## Quick Start

1. **Add your API key as a repository secret:**
   - Go to Settings > Secrets and variables > Actions
   - Click "New repository secret"
   - Name: `AETHERIS_API_KEY`
   - Value: Your Gemini/OpenAI/Claude API key

2. **Copy the workflow file:**
   ```bash
   # Copy from Aetheris repository
   mkdir -p .github/workflows
   curl -o .github/workflows/aetheris-analysis.yml \
     https://raw.githubusercontent.com/adryserage/aetheris/main/.github/workflows/aetheris-analysis.yml
   ```

3. **Commit and push:**
   ```bash
   git add .github/workflows/aetheris-analysis.yml
   git commit -m "ci: add Aetheris code analysis"
   git push
   ```

That's it! Aetheris will now analyze your code on every push and PR.

## Features

### Automatic Analysis

The workflow runs automatically on:
- Push to `main` or `develop` branches
- Pull requests (opened, synchronized, reopened)

### Manual Trigger

Trigger analysis manually from the Actions tab with options:
- **Mode**: Choose between `analysis` (scan only) or `fix` (auto-fix issues)
- **Timeout**: Set custom timeout (e.g., `30m`, `2h`)
- **Full scan**: Force full codebase scan instead of changed files only

### Changed Files Detection

By default, only changed files are analyzed on PRs for efficiency:
- Pull requests: Files changed vs. base branch
- Push: Files changed in the commit

### Artifacts

Analysis reports are uploaded as artifacts and retained for 30 days:
- Download from the Actions run page
- Contains all Markdown reports
- Includes local setup instructions

### PR Comments

On pull requests, a summary comment is posted with:
- Analysis highlights
- Link to full artifacts

## Workflow Options

### Triggers

```yaml
on:
  push:
    branches: [main, develop]  # Customize branches
  pull_request:
    types: [opened, synchronize, reopened]
  workflow_dispatch:
    inputs:
      mode:
        type: choice
        options: [analysis, fix]
      timeout:
        type: string
        default: "60m"
      full_scan:
        type: boolean
        default: false
```

### Concurrency

Prevents multiple runs on the same branch:

```yaml
concurrency:
  group: aetheris-${{ github.ref }}
  cancel-in-progress: true
```

### Timeout

The workflow has a 6-hour GitHub Actions limit. Set custom timeouts for analysis:

```yaml
- name: Run Aetheris analysis
  run: aetheris analysis --timeout 2h
```

## Customization

### Use Different AI Provider

Set the appropriate API key secret:

| Provider | Secret Name | Get API Key |
|----------|-------------|-------------|
| Gemini (default) | `AETHERIS_API_KEY` | [ai.google.dev](https://ai.google.dev) |
| OpenAI | `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com/api-keys) |
| Claude | `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) |

### Add Exclude Patterns

Exclude specific paths from analysis:

```yaml
- name: Run Aetheris analysis
  run: |
    aetheris analysis --profile ci \
      --exclude "tests/**,docs/**,migrations/**"
```

### Safety Profiles (v2.12+)

Use different safety profiles:

```yaml
# Safe mode (default) - restrictive, local development
aetheris analysis --profile safe

# CI mode - fail-fast, audit logging, no prompts
aetheris analysis --profile ci

# YOLO mode - extended limits (requires --yes)
aetheris analysis --profile yolo --yes
```

### Agent Selection (v2.11+)

Select specific agents or presets:

```yaml
# Security-focused scan
aetheris analysis --preset security-audit

# Performance review
aetheris analysis --agents performance,metrics,architecture

# With compliance frameworks
aetheris analysis --agents data_privacy --compliance gdpr,hipaa
```

### Custom Branch Triggers

Edit the `on:` section to trigger on different branches:

```yaml
on:
  push:
    branches: [main, release/*, feature/*]
  pull_request:
    branches: [main, develop]
```

### Schedule Analysis

Run analysis on a schedule:

```yaml
on:
  schedule:
    - cron: '0 0 * * 1'  # Every Monday at midnight
```

## Troubleshooting

### Missing API Key

```
Error: Missing AETHERIS_API_KEY secret
```

**Solution:** Add your API key as a repository secret (Settings > Secrets > Actions).

### Timeout Exceeded

```
Error: Analysis interrupted: timeout reached
```

**Solution:** Increase timeout in workflow_dispatch or edit the workflow file:
```yaml
run: aetheris analysis --timeout 2h
```

### No Changed Files

If the workflow skips analysis:
- Check that code files were changed (not just configs)
- Use `full_scan: true` in manual trigger for full scan

### Permission Denied

```
Error: Resource not accessible by integration
```

**Solution:** Check workflow permissions:
```yaml
permissions:
  contents: read
  pull-requests: write
  issues: write
```

## Example Output

### PR Comment

After analysis, a comment is posted on PRs:

```markdown
## Aetheris Analysis Complete

### Summary

**Critical Issues**: 2
**High Priority**: 5
**Medium Priority**: 12

Download full results: [Analysis Artifacts](link)
```

### Artifacts Structure

```
aetheris-analysis-abc1234/
├── README.md
└── docs/
    └── analyses/
        ├── quality_assurance_report.md
        ├── vulnerabilities_report.md
        └── file_analysis_*.md
```

## Best Practices

1. **Use CI profile** for automated pipelines:
   ```bash
   aetheris analysis --profile ci
   ```

2. **Set appropriate timeout** based on codebase size:
   - Small projects (<100 files): `30m`
   - Medium projects (100-500 files): `1h`
   - Large projects (500+ files): `2h`

3. **Review artifacts** before merging PRs

4. **Use changed files detection** for faster PR feedback

5. **Configure concurrency** to avoid wasted runs

## Environment Variables

| Variable | Source | Description |
|----------|--------|-------------|
| `AETHERIS_API_KEY` | Repository secret | AI provider API key |
| `GEMINI_API_KEY` | Repository secret | Gemini API key (alternative) |
| `OPENAI_API_KEY` | Repository secret | OpenAI API key (alternative) |
| `ANTHROPIC_API_KEY` | Repository secret | Claude API key (alternative) |
| `CHANGED_FILES` | Auto-detected | Files changed in PR |

## Local Setup from Artifacts

After downloading artifacts:

**Linux/macOS:**
```bash
chmod +x setup-local.sh
./setup-local.sh
```

**Windows (PowerShell):**
```powershell
.\setup-local.ps1
```

## Related Documentation

- [CLI Commands](commands/README.md)
- [Security Profiles](headless.md#security-profiles)
- [Configuration](configuration.md)
