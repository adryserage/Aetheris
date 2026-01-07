# Data Model: GitHub PR Generator

**Feature**: 002-github-pr-generator
**Date**: 2026-01-06

## Reused Entities (from issue_creator.py)

### ExtractedBug
Already defined in `src/services/issue_creator.py`:
```python
@dataclass
class ExtractedBug:
    source_file: str
    report_file: str
    bug_type: str  # 'security', 'risk', 'inconsistency', 'suggestion'
    severity: str  # 'critical', 'high', 'medium', 'low'
    title: str
    description: str
    recommendation: str = ""
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
```

## New Entities

### PROptions
Configuration for the PR generation command:
```python
@dataclass
class PROptions:
    dry_run: bool = False
    base_branch: Optional[str] = None  # defaults to repo default
    from_report: Optional[str] = None
    bug_index: Optional[int] = None
    issue_number: Optional[int] = None
    link_issues: bool = False
```

### GeneratedFix
AI-generated fix for a bug:
```python
@dataclass
class GeneratedFix:
    bug: ExtractedBug
    original_code: str
    fixed_code: str
    file_path: str
    is_valid: bool  # syntax check passed
    validation_error: Optional[str] = None
```

### PRToCreate
Prepared PR ready for GitHub:
```python
@dataclass
class PRToCreate:
    title: str
    body: str
    branch_name: str
    base_branch: str
    fix: GeneratedFix
    linked_issue: Optional[int] = None
```

### PRResult
Result of a single PR creation attempt:
```python
@dataclass
class PRResult:
    status: str  # 'created', 'skipped', 'failed'
    title: str
    branch_name: Optional[str] = None
    url: Optional[str] = None
    error: Optional[str] = None
    bug: Optional[ExtractedBug] = None
```

### PRSummary
Final summary of the command execution:
```python
@dataclass
class PRSummary:
    total_bugs: int
    created: int
    skipped: int
    failed: int
    results: List[PRResult] = field(default_factory=list)
    duration_seconds: float = 0.0
```

## Entity Relationships

```
ExtractedBug (reused)
      │
      ▼
GeneratedFix ──────► PRToCreate ──────► PRResult
      │                   │                 │
      │                   │                 ▼
      │                   │            PRSummary
      │                   │
      ▼                   ▼
[original_code]     [linked_issue]
```

## State Transitions

### Bug Processing Flow
```
PENDING → GENERATING_FIX → VALIDATING → COMMITTING → PUSHING → CREATING_PR → DONE/FAILED
```

### PR Status Values
- `created`: PR successfully created on GitHub
- `skipped`: Branch already exists or source file missing
- `failed`: Error during any step (fix generation, commit, push, PR creation)
