# Feature Specification: Reanalyze Flag

**Feature Branch**: `014-reanalyze-flag`
**Created**: 2026-01-09
**Status**: Draft
**Target Version**: v2.6.1
**Input**: Add --reanalyze flag to analysis command that detects edited files since last analysis and reruns analysis on them, then fully updates the documentation reports.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Developer Wants Fresh Analysis After Code Changes (Priority: P1)

A developer has made changes to their codebase after a previous Aetheris analysis. They want to reanalyze only the files that changed and update the existing reports without running a full analysis from scratch.

**Why this priority**: This is the primary use case - incremental analysis saves time and API costs.

**Independent Test**: Run analysis, modify a file, run with --reanalyze, verify only modified files are analyzed.

**Acceptance Scenarios**:

1. **Given** a previous analysis exists, **When** the user runs `aetheris analysis --reanalyze`, **Then** only files modified since the last analysis are reanalyzed
2. **Given** modified files are detected, **When** analysis completes, **Then** the existing reports are updated with new findings
3. **Given** no files have changed since last analysis, **When** --reanalyze is used, **Then** the user is informed and no API calls are made

---

### User Story 2 - CI Pipeline Incremental Analysis (Priority: P2)

A CI pipeline wants to run quick incremental analysis on PR changes without reanalyzing the entire codebase.

**Why this priority**: Reduces CI runtime and API costs for frequent commits.

**Acceptance Scenarios**:

1. **Given** a CI job runs after a commit, **When** `--reanalyze` is combined with `--changed-files-only`, **Then** both flags work together correctly
2. **Given** cache exists from previous run, **When** --reanalyze is used, **Then** cache is invalidated only for changed files

---

### Edge Cases

- What if no previous analysis exists? (Run full analysis with warning)
- What if the metrics file is corrupted or missing? (Fall back to full analysis)
- What if a file was deleted since last analysis? (Remove from reports, log the removal)
- What if git is not available to detect changes? (Use file modification timestamps)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: CLI MUST accept `--reanalyze` / `-r` flag on the analysis command
- **FR-002**: System MUST detect files modified since last analysis using git diff or file timestamps
- **FR-003**: System MUST skip unchanged files (bypass cache check, no API calls)
- **FR-004**: System MUST update existing reports with new findings for changed files
- **FR-005**: System MUST preserve findings for unchanged files in reports
- **FR-006**: System MUST log which files are being reanalyzed
- **FR-007**: If no previous analysis exists, system MUST run full analysis with informational message
- **FR-008**: `--reanalyze` MUST work with existing flags (`--changed-files-only`, `--timeout`, etc.)

### Key Entities

- **Last Analysis Metadata**: Timestamp, analyzed files list, git commit SHA (stored in metrics JSON)
- **Changed Files Detector**: Logic to identify modified files since last run
- **Report Updater**: Logic to merge new findings into existing reports

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Running `--reanalyze` on 5 changed files out of 100 completes in <20% of full analysis time
- **SC-002**: API costs for reanalysis are proportional to changed file count
- **SC-003**: Reports accurately reflect combined state of old + new findings
- **SC-004**: No data loss for unchanged files when reports are updated

## Assumptions

- Git is available in most environments for change detection (fallback to timestamps otherwise)
- Previous analysis metrics are stored in `docs/metrics/` directory
- Existing cache system can be selectively invalidated per file
