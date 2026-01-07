# Research: GitHub Issues CLI Command

**Feature**: 001-github-issues-cli
**Date**: 2026-01-06

## Research Tasks Completed

### 1. Report Format Analysis

**Task**: Understand existing analysis report structure for parsing.

**Findings**:
- Reports are markdown files in `docs/analyses/`
- File naming: `{path_with_underscores}.md`
- Key sections:
  - `# Analyse: {path}`
  - `## Langage détecté`
  - `## Objectif / Fonction principale`
  - `## Points forts / Bonnes pratiques`
  - `## Risques, dettes techniques ou incohérences` ← **bugs here**
  - `## Suggestions d'amélioration`

**Decision**: Parse `## Risques` section with regex to extract bugs.

---

### 2. Existing Data Models

**Task**: Identify reusable models from codebase.

**Findings** (`src/models/data_models.py`):

```python
@dataclass
class BugIdentifier:
    id: str                    # "BUG-{hash[:8]}"
    file_path: str
    line_number: Optional[int]
    bug_type: str              # 'security', 'risk', 'inconsistency', 'suggestion'
    severity: str              # 'critical', 'high', 'medium', 'low'
    description: str
    recommendation: str
    impacted_files: List[str]

@dataclass
class SecurityIssue:
    severity: str
    issue_type: str
    description: str
    line_number: Optional[int]
    code_snippet: Optional[str]
    recommendation: str
```

**Decision**: Map `BugIdentifier.bug_type` to GitHub labels:
- `security` → labels: bug, security, aetheris-analysis
- `risk` → labels: bug, tech-debt, aetheris-analysis
- `inconsistency` → labels: bug, aetheris-analysis
- `suggestion` → labels: enhancement, aetheris-analysis

---

### 3. GitHub CLI (`gh`) Research

**Task**: Best practices for `gh issue create`.

**Findings**:
```bash
# Create issue with labels and assignee
gh issue create \
  --title "[Security] in auth.py - SQL injection vulnerability" \
  --body "## File\n\`src/auth.py\`\n\n## Description\n..." \
  --label "bug,security,aetheris-analysis" \
  --assignee "username"

# List existing issues for deduplication
gh issue list --state all --json title --limit 1000

# Check auth status
gh auth status
```

**Rate Limiting**:
- 5000 requests/hour for authenticated users
- `gh` returns exit code 1 with stderr message on rate limit
- Exponential backoff: 1s, 2s, 4s, max 3 retries

**Decision**: Use subprocess with JSON output for error handling.

---

### 4. Existing CLI Patterns

**Task**: Understand how to add new subcommand.

**Findings** (`src/cli.py`):
```python
def setup_analysis_parser(subparsers):
    """Configure le parser pour la sous-commande analysis"""
    analysis_parser = subparsers.add_parser("analysis", ...)
    analysis_parser.add_argument("--changed-files-only", ...)
    return analysis_parser

async def run_analysis(args):
    """Execute analysis command"""
    ...
```

**Decision**: Follow exact pattern:
1. Add `setup_issues_parser(subparsers)` function
2. Add `run_issues(args)` async function
3. Register in `main()` argparse setup

---

## Unknowns Resolved

| Unknown | Resolution |
|---------|------------|
| Report parsing strategy | Regex on `## Risques` section |
| Issue body format | Structured markdown with ## sections |
| Deduplication method | `gh issue list --json title` lookup |
| Rate limit handling | Exponential backoff, max 3 retries |
| Severity to label mapping | Defined mapping table |
