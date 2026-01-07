# Quickstart: GitHub PR Generator

**Feature**: 002-github-pr-generator
**Date**: 2026-01-06

## Prerequisites

### 1. Same as Issues Command
- GitHub CLI (`gh`) installed and authenticated
- Python environment with Aetheris installed
- AI provider configured (GEMINI_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY)

### 2. Repository Access
```bash
# Verify you can push branches
git push --dry-run origin HEAD

# Verify gh PR access
gh pr list --limit 1
```

---

## Development Workflow

### Step 1: Run Analysis First
Generate analysis reports that the PR command will use:

```bash
aetheris analysis
```

### Step 2: Create Issues (Optional)
Create issues to link PRs to:

```bash
aetheris issues --dry-run  # Preview
aetheris issues            # Create issues
```

### Step 3: Preview PRs (Dry Run)
```bash
# Preview all PRs that would be created
aetheris pr --dry-run
```

Expected output:
```
🔍 Dry-run mode - no PRs will be created

Found 5 bugs in analysis reports

PR 1/5: fix: [Security] in auth.py - SQL injection
  Branch: fix/security-auth-abc123
  Fix preview:
    - Line 42: cursor.execute(query) → cursor.execute(query, params)
  Labels: aetheris-fix, security

PR 2/5: fix: [Risk] in cache.py - Memory leak
  Branch: fix/risk-cache-def456
  ...

Summary: 5 PRs would be created
```

### Step 4: Generate PRs
```bash
# Generate all PRs
aetheris pr

# With issue linking
aetheris pr --link-issues

# Target specific branch
aetheris pr --base-branch develop

# Process specific report
aetheris pr --from-report docs/analyses/auth.md
```

---

## Testing Checklist

- [ ] `gh auth status` shows authenticated
- [ ] `aetheris pr --dry-run` shows correct bug count
- [ ] PR titles follow format: `fix: [Type] in file - description`
- [ ] PR bodies have all required sections
- [ ] Branches are created with correct naming
- [ ] Generated fixes are syntactically valid
- [ ] Issue linking works with `--link-issues`
- [ ] `--from-report` filters correctly
- [ ] Error handling for missing files

---

## File Locations

| Artifact | Path |
|----------|------|
| CLI entry point | `src/cli.py` |
| PR generator service | `src/services/pr_generator.py` |
| Issue creator (reused) | `src/services/issue_creator.py` |
| AI providers | `src/core/ai_providers.py` |
| Analysis reports | `docs/analyses/*.md` |
