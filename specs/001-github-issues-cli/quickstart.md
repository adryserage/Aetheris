# Quickstart: GitHub Issues CLI Command

**Feature**: 001-github-issues-cli
**Date**: 2026-01-06

## Prerequisites

### 1. GitHub CLI (`gh`)

Install and authenticate the GitHub CLI:

```bash
# macOS
brew install gh

# Linux (Debian/Ubuntu)
sudo apt install gh

# Windows
winget install GitHub.cli

# Authenticate
gh auth login
```

Verify installation:
```bash
gh auth status
# Should show: Logged in to github.com as {username}
```

### 2. Python Environment

```bash
# Install Aetheris in development mode
pip install -e .

# Verify
aetheris --help
```

---

## Development Workflow

### Step 1: Run Analysis First

Generate analysis reports that the issues command will parse:

```bash
# Full codebase analysis
aetheris analysis

# Or specific files
aetheris analysis --files src/core/analyzer.py,src/cli.py
```

Reports are saved to `docs/analyses/`.

### Step 2: Preview Issues (Dry Run)

```bash
# Preview all issues that would be created
aetheris issues --dry-run
```

Expected output:
```
🔍 Dry-run mode - no issues will be created

Found 12 bugs in 5 analysis reports

[Security] in auth.py - SQL injection in query builder
  Labels: bug, security, priority-high, aetheris-analysis

[Risk] in cache.py - Potential memory leak in caching layer
  Labels: bug, tech-debt, priority-medium, aetheris-analysis

...

Summary: 12 issues would be created
```

### Step 3: Create Issues

```bash
# Create all issues
aetheris issues

# With custom labels
aetheris issues --labels "sprint-42,needs-review"

# Assign to someone
aetheris issues --assignee "developerusername"

# Target different repo
aetheris issues --repo "myorg/another-repo"
```

### Step 4: Verify Deduplication

Run again - existing issues should be skipped:

```bash
aetheris issues
# Output: 12 bugs found, 0 created, 12 skipped (already exist)
```

---

## Testing Checklist

- [ ] `gh auth status` shows authenticated
- [ ] `aetheris issues --dry-run` shows correct bug count
- [ ] Issue titles follow format: `[Type] in file - description`
- [ ] Issue bodies have all required sections
- [ ] Labels include severity and aetheris-analysis
- [ ] Duplicate run skips existing issues
- [ ] `--from-report` filters to single file
- [ ] Error handling for missing `gh` CLI

---

## File Locations

| Artifact | Path |
|----------|------|
| CLI entry point | `src/cli.py` |
| Issue creator service | `src/services/issue_creator.py` |
| Analysis reports | `docs/analyses/*.md` |
| Data models | `src/models/data_models.py` |
