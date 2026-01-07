# Issues Command

The `aetheris issues` command creates GitHub issues from analysis reports.

## Prerequisites

GitHub CLI must be installed and authenticated:
```bash
gh auth login
```

## Usage

```bash
aetheris issues [options]
```

## Options

| Option | Description |
|--------|-------------|
| `--dry-run` | Preview issues without creating them |
| `--labels LABELS` | Additional labels (comma-separated) |
| `--assignee USER` | GitHub username to assign issues |
| `--repo REPO` | Target repository (owner/repo format) |
| `--from-report FILE` | Process only this specific report file |

## Examples

### Create Issues from All Reports
```bash
aetheris issues
```

### Preview Without Creating
```bash
aetheris issues --dry-run
```

### With Custom Labels
```bash
aetheris issues --labels security,sprint-42
```

### Assign to User
```bash
aetheris issues --assignee username
```

### Target Specific Repository
```bash
aetheris issues --repo owner/repo
```

### From Specific Report
```bash
aetheris issues --from-report docs/analyses/analyzer.md
```

## Issue Format

Each created issue includes:

### Title
```
[BugType] in filename - brief description
```

### Body Sections
- **File**: Path to the affected file
- **Bug Description**: What the issue is
- **Issue Details**: Severity, line number, context
- **Recommended Solution**: How to fix it
- **Code Context**: Relevant code snippet

### Labels
- `bug` - Issue type
- `aetheris-analysis` - Source identifier
- Severity level (`critical`, `high`, `medium`, `low`)
- Custom labels via `--labels`

## Deduplication

The command automatically skips issues that already exist (matched by title).

## Rate Limiting

GitHub API rate limits are handled automatically with progress feedback.

## Workflow

1. Run analysis: `aetheris analysis`
2. Preview issues: `aetheris issues --dry-run`
3. Create issues: `aetheris issues`
4. Generate fix PRs: `aetheris pr-gen --link-issues`
