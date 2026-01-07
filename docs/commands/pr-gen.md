# PR Generator Command

The `aetheris pr-gen` command generates GitHub Pull Requests with AI-generated fixes for bugs found in analysis.

## Prerequisites

- GitHub CLI installed and authenticated: `gh auth login`
- AI provider configured (Gemini, OpenAI, or Claude)

## Usage

```bash
aetheris pr-gen [options]
```

Aliases: `generate-prs`

## Options

| Option | Description |
|--------|-------------|
| `--dry-run` | Preview PRs and fixes without creating them |
| `--base-branch BRANCH` | Target base branch for PRs (defaults to repo default) |
| `--from-report FILE` | Process only this specific analysis report |
| `--bug-index INDEX` | Process only the bug at this index (0-based) |
| `--link-issues` | Automatically link PRs to matching GitHub issues |
| `--issue-number NUM` | Explicitly link all PRs to this issue number |

## Examples

### Preview PRs (Recommended First)
```bash
aetheris pr-gen --dry-run
```

### Generate All PRs
```bash
aetheris pr-gen
```

### Link to Issues
```bash
aetheris pr-gen --link-issues
```

### Target Specific Branch
```bash
aetheris pr-gen --base-branch develop
```

### From Specific Report
```bash
aetheris pr-gen --from-report docs/analyses/analyzer.md
```

### Single Bug by Index
```bash
aetheris pr-gen --bug-index 0
```

### Link to Specific Issue
```bash
aetheris pr-gen --issue-number 42
```

## How It Works

1. **Parse Reports**: Reads bugs from `docs/analyses/` reports
2. **Generate Fixes**: Uses AI to generate code fixes
3. **Create Branch**: Creates feature branch per bug
4. **Apply Fix**: Applies the generated fix
5. **Push Branch**: Pushes to remote
6. **Create PR**: Opens PR with detailed description

## PR Format

### Title
```
fix(file): Bug type - brief description
```

### Body Sections
- Summary of the fix
- Bug details (type, severity, location)
- What was changed
- Link to issue (if `--link-issues`)
- Test plan

## Workflow

### Typical Flow
```bash
# 1. Analyze codebase
aetheris analysis

# 2. Create GitHub issues
aetheris issues

# 3. Preview PRs
aetheris pr-gen --dry-run

# 4. Generate PRs with issue linking
aetheris pr-gen --link-issues
```

### Single Bug Fix
```bash
# Fix specific bug and link to issue
aetheris pr-gen --bug-index 0 --issue-number 123
```

## Branch Naming

Branches are named automatically:
```
fix/<file>-<bug-type>-<short-id>
```

Example: `fix/analyzer-null-reference-a1b2c3`

## Notes

- Each bug creates one PR (1 bug = 1 PR)
- Existing branches are detected and skipped
- AI generates fixes based on bug context and code
- Use `--dry-run` first to preview changes
