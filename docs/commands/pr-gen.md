# PR Generator Command

The `aetheris pr-gen` command generates GitHub Pull Requests with AI-generated fixes for bugs found in analysis.

## Prerequisites

- GitHub CLI installed and authenticated: `gh auth login`
- AI provider configured (see below)

### AI Provider Configuration

Create a `.env` file in your project root with your API key:

```bash
# Option 1: Gemini (recommended, free tier available)
AI_PROVIDER=gemini
GEMINI_API_KEY=your_key_here

# Option 2: OpenAI
AI_PROVIDER=openai
OPENAI_API_KEY=your_key_here

# Option 3: Claude (Anthropic)
AI_PROVIDER=claude
ANTHROPIC_API_KEY=your_key_here
```

**Get your API key:**
- Gemini: https://ai.google.dev (free tier available)
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/

> **Important**: Add `.env` to your `.gitignore` to avoid committing API keys.

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
| `--link-issues` | Automatically link PRs to matching GitHub issues (requires `aetheris issues` to be run first) |
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

> **⚠️ Prerequisite**: Run `aetheris issues` first to create GitHub issues from analysis reports. The `--link-issues` option matches PRs to existing issues by bug ID. If issues don't exist, PRs will be created without issue links.

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

> **Important**: Steps must be executed in order. The `--link-issues` option in step 4 depends on issues created in step 2.

```bash
# 1. Analyze codebase
aetheris analysis

# 2. Create GitHub issues (REQUIRED before --link-issues)
aetheris issues

# 3. Preview PRs
aetheris pr-gen --dry-run

# 4. Generate PRs with issue linking
aetheris pr-gen --link-issues
```

> **Note**: If you skip step 2 and use `--link-issues`, PRs will still be created but without issue references. Use `--issue-number` to explicitly link to a known issue number.

### Single Bug Fix
```bash
# Fix specific bug and link to issue
aetheris pr-gen --bug-index 0 --issue-number 123
```

## Branch Naming

Branches are named automatically using a deterministic format:
```
fix/<file>-<bug-type>-<short-id>
```

Where:
- `<file>`: Source filename (without extension)
- `<bug-type>`: Normalized bug type (e.g., `null-reference`, `security`)
- `<short-id>`: First 8 characters of the bug's unique ID hash (e.g., `BUG-BE2212F2` → `be2212f2`)

**Collision prevention**: The `short-id` is derived from the bug's deterministic hash (Bug ID), which is computed from the bug's file path, line number, type, and description. This ensures:
- Same bug always produces same branch name (idempotent)
- Different bugs produce unique branch names
- Re-running `pr-gen` detects existing branches and skips them

Example: `fix/analyzer-null-reference-be2212f2`

## Batching Strategies

By default, each bug creates one PR (1 bug = 1 PR). For codebases with many minor bugs, this can result in PR spam. Consider these strategies:

### Strategy 1: Filter by Severity
Process only high-priority bugs first:
```bash
# Use --from-report with pre-filtered reports
aetheris analysis --min-severity high
aetheris pr-gen
```

### Strategy 2: Incremental Processing
Process bugs one at a time to control PR volume:
```bash
# Fix bugs incrementally by index
aetheris pr-gen --bug-index 0
aetheris pr-gen --bug-index 1
# ...
```

### Strategy 3: File-Scoped PRs
Focus on one file at a time:
```bash
aetheris pr-gen --from-report docs/analyses/specific_file.md
```

### Strategy 4: Manual Batching Workflow
For maximum control, combine multiple fixes manually:
```bash
# 1. Preview all fixes
aetheris pr-gen --dry-run

# 2. Create a single branch for related fixes
git checkout -b fix/batch-minor-issues

# 3. Apply fixes selectively using bug indices
aetheris pr-gen --bug-index 0 --dry-run  # Review fix
# Manually apply or cherry-pick desired changes

# 4. Create a single PR with all batched fixes
gh pr create --title "fix: batch of minor issues" --body "Combined fixes for issues #1, #2, #3"
```

> **Tip**: For large reports (50+ bugs), consider running analysis with stricter filters or addressing bugs in phases by severity level.

## Notes

- Default behavior: 1 bug = 1 PR (atomic, reviewable changes)
- Existing branches are detected and skipped
- AI generates fixes based on bug context and code
- Use `--dry-run` first to preview changes
- For batch processing, use the strategies above to control PR volume
