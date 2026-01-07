# GitHub Actions Integration

Aetheris includes a workflow for automated code analysis in GitHub Actions.

## Setup

### 1. Add Repository Secret

1. Go to Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add your API key:

| Name | Value |
|------|-------|
| `GEMINI_API_KEY` | Your Gemini API key |
| or `OPENAI_API_KEY` | Your OpenAI API key |
| or `ANTHROPIC_API_KEY` | Your Claude API key |

Optional secrets:
- `AI_PROVIDER`: Provider name (gemini, openai, claude)
- `AI_MODEL`: Specific model to use

### 2. Workflow File

The workflow is pre-configured in `.github/workflows/code-review.yml`.

## Triggers

| Event | Behavior |
|-------|----------|
| Push to main/master | Full codebase analysis |
| Pull Request | Changed files only |
| Manual dispatch | Choose mode: full or changed |

## Manual Execution

1. Go to Actions tab
2. Select "Code Review" workflow
3. Click "Run workflow"
4. Choose:
   - **Mode**: `full` or `changed`
   - **PR Number**: (optional for changed mode)

## Artifacts

Reports are available as GitHub artifacts:

1. Go to Actions
2. Select workflow run
3. Download "code-analysis-reports"

Contents:
- `docs/analyses/*.md` - Individual file reports
- `docs/architecture_overview.md` - Architecture report
- `docs/analyses/quality_assurance_report.md` - QA report
- `docs/analyses/vulnerabilities_report.md` - Vulnerabilities

## Customization

Edit `.github/workflows/code-review.yml`:

### Change Triggers
```yaml
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
```

### Exclude Paths
```yaml
paths-ignore:
  - '*.md'
  - 'docs/**'
  - '.github/**'
```

### Add Notifications
```yaml
- name: Notify Slack
  uses: slackapi/slack-github-action@v1
  with:
    channel-id: 'C123456'
    slack-message: 'Code review completed'
```

## Environment Variables

Available in workflow:

| Variable | Source |
|----------|--------|
| `GEMINI_API_KEY` | Repository secret |
| `CHANGED_FILES` | Auto-detected from PR |
| `PR_NUMBER` | From GitHub event |

## Example Workflow

```yaml
name: Code Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Aetheris
        run: pip install adryserage-aetheris

      - name: Run Analysis
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: |
          aetheris analysis --changed-files-only \
            --files '${{ steps.files.outputs.all }}'

      - name: Upload Reports
        uses: actions/upload-artifact@v4
        with:
          name: analysis-reports
          path: docs/analyses/
```
