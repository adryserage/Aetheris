# Implementation Plan: GitHub Issues CLI Command

**Branch**: `001-github-issues-cli` | **Date**: 2026-01-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-github-issues-cli/spec.md`

## Summary

Add a new CLI command `aetheris issues` that parses existing analysis reports from `docs/analyses/`, extracts bug information, and creates GitHub issues using the `gh` CLI tool. The command supports dry-run mode, custom labels, assignees, deduplication, and progress feedback.

## Technical Context

**Language/Version**: Python 3.8+ (matches existing project)
**Primary Dependencies**: Rich (terminal UI), subprocess (gh CLI), re/pathlib (parsing)
**Storage**: N/A (reads existing markdown files, writes to GitHub via gh)
**Testing**: Manual testing with --dry-run mode
**Target Platform**: Linux, macOS, Windows (cross-platform CLI)
**Project Type**: Single CLI project (extends existing Aetheris CLI)
**Performance Goals**: Process 50 bugs in under 2 minutes
**Constraints**: Rate limiting (GitHub API), gh CLI must be installed
**Scale/Scope**: Typical analysis produces 10-100 bugs per run

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Library-First | ✅ Pass | New service `issue_creator.py` is self-contained |
| CLI Interface | ✅ Pass | Exposes via `aetheris issues` command |
| Test-First | ⚠️ Defer | `--dry-run` mode enables manual testing |
| Integration Testing | ✅ Pass | gh CLI integration is tested via subprocess |
| Observability | ✅ Pass | Rich progress bars, summary report |
| Simplicity | ✅ Pass | Single service, minimal dependencies |

## Project Structure

### Documentation (this feature)

```text
specs/001-github-issues-cli/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # N/A (CLI command, no API)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
src/
├── cli.py                    # MODIFY: Add issues subcommand
├── services/
│   └── issue_creator.py      # NEW: Core issue creation service
└── models/
    └── data_models.py        # EXISTING: Uses BugIdentifier, SecurityIssue
```

**Structure Decision**: Extends existing single project structure. New service in `src/services/` follows established pattern (dependency_analyzer.py, documentation_searcher.py, code_generator.py).

## Complexity Tracking

No violations requiring justification. Feature follows existing patterns exactly.

---

## Phase 0: Research Summary

### Decision 1: Report Parsing Strategy

**Decision**: Use regex-based markdown parsing to extract bugs from analysis reports.

**Rationale**:
- Analysis reports follow consistent template: `## Risques, dettes techniques ou incohérences` section contains bugs
- `BugIdentifier` objects in `FileAnalysis.bugs` list provide structured data when available
- Fallback to markdown parsing for legacy reports without structured data

**Alternatives Considered**:
- JSON sidecar files: Would require changes to report generation
- AST parsing: Overkill for markdown extraction

### Decision 2: GitHub CLI Integration

**Decision**: Use `gh issue create` via subprocess with JSON output.

**Rationale**:
- `gh` CLI is widely installed, handles authentication securely
- JSON output (`--json`) enables proper error handling
- Rate limiting info available via exit codes and stderr

**Alternatives Considered**:
- PyGithub library: Additional dependency, manual auth handling
- REST API direct: Would need token management, more code

### Decision 3: Deduplication Strategy

**Decision**: Query existing issues via `gh issue list --search` with title matching.

**Rationale**:
- Title format `[BugType] in filename - desc` is unique enough
- `--search` supports exact title matching with quotes
- Fetching once at start is efficient (vs. per-issue checks)

**Alternatives Considered**:
- Local cache file: Would go stale, complexity
- Issue body hash: Harder to match, more API calls

### Decision 4: Rate Limiting Handling

**Decision**: Detect rate limit from `gh` stderr, exponential backoff with max 3 retries.

**Rationale**:
- GitHub API rate limit: 5000 requests/hour for authenticated users
- Creating 50 issues << 5000, unlikely to hit unless burst
- `gh` outputs rate limit info on 403 errors

**Alternatives Considered**:
- Preemptive delay: Slower for normal case
- No handling: Would fail silently

---

## Phase 1: Design

### Data Model

See [data-model.md](./data-model.md) for full entity definitions.

**Key Entities**:

| Entity | Purpose |
|--------|---------|
| `ExtractedBug` | Bug parsed from markdown report |
| `IssueToCreate` | Issue ready for GitHub creation |
| `IssueResult` | Result of creation attempt (created/skipped/failed) |
| `IssuesSummary` | Final summary counts |

### Component Design

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   CLI Parser     │────▶│   IssueCreator   │────▶│   gh CLI         │
│   (cli.py)       │     │   Service        │     │   (subprocess)   │
└──────────────────┘     └──────────────────┘     └──────────────────┘
        │                        │
        ▼                        ▼
┌──────────────────┐     ┌──────────────────┐
│   Rich Console   │     │   Report Parser  │
│   (progress)     │     │   (markdown)     │
└──────────────────┘     └──────────────────┘
```

### API Contracts

**CLI Interface**:

```bash
aetheris issues [OPTIONS]

Options:
  --dry-run              Preview without creating issues
  --labels TEXT          Additional labels (comma-separated)
  --assignee TEXT        Assign issues to user
  --repo TEXT            Target repo (owner/repo format)
  --from-report PATH     Process specific report file only

Exit Codes:
  0: Success (all issues created or skipped)
  1: Partial failure (some issues failed)
  2: Fatal error (gh not installed, auth failed)
```

**IssueCreator Service Interface**:

```python
class IssueCreator:
    def __init__(self, repo: Optional[str] = None)

    async def validate_gh_cli(self) -> Tuple[bool, str]
    async def get_existing_issues(self) -> Set[str]  # titles
    async def parse_reports(self, report_path: Optional[str]) -> List[ExtractedBug]
    async def create_issue(self, bug: ExtractedBug, labels: List[str], assignee: Optional[str]) -> IssueResult
    async def run(self, options: IssueOptions) -> IssuesSummary
```

### File-by-File Changes

| File | Action | Description |
|------|--------|-------------|
| `src/cli.py` | MODIFY | Add `setup_issues_parser()` and `run_issues()` functions |
| `src/services/issue_creator.py` | CREATE | New service with IssueCreator class |
| `src/services/__init__.py` | MODIFY | Export IssueCreator if exists |

### Quickstart

See [quickstart.md](./quickstart.md) for development setup instructions.

---

## Build Sequence

1. **Create IssueCreator service** (`src/services/issue_creator.py`)
   - Implement `validate_gh_cli()` - check gh installed and authenticated
   - Implement `parse_reports()` - extract bugs from markdown
   - Implement `get_existing_issues()` - fetch titles for dedup
   - Implement `create_issue()` - call gh with proper formatting
   - Implement `run()` - orchestrate full flow with progress

2. **Add CLI subcommand** (`src/cli.py`)
   - Add `setup_issues_parser()` following `setup_analysis_parser()` pattern
   - Add `run_issues()` async function
   - Register in main parser

3. **Test manually**
   - Run `aetheris analysis` to generate reports
   - Run `aetheris issues --dry-run` to verify parsing
   - Run `aetheris issues` to create real issues
   - Verify deduplication on second run
