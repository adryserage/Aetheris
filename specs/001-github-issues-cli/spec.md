# Feature Specification: GitHub Issues CLI Command

**Feature Branch**: `001-github-issues-cli`
**Created**: 2026-01-06
**Status**: Draft
**Input**: User description: "Create a CLI command 'issues' that creates GitHub issues for each bug found during code analysis"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create GitHub Issues from Analysis (Priority: P1)

As a developer who has run Aetheris analysis on my codebase, I want to automatically create GitHub issues for each bug found so that I can track and assign fixes through my existing workflow.

**Why this priority**: This is the core functionality. Without the ability to create issues from analysis results, the feature has no value.

**Independent Test**: Can be fully tested by running `aetheris issues` after an analysis and verifying issues appear in GitHub. Delivers immediate value by bridging analysis to issue tracking.

**Acceptance Scenarios**:

1. **Given** analysis reports exist in `docs/analyses/`, **When** I run `aetheris issues`, **Then** GitHub issues are created for each bug found with proper formatting
2. **Given** a bug is found in `src/core/analyzer.py`, **When** an issue is created, **Then** the issue title follows format `[BugType] in analyzer.py - brief description`
3. **Given** an issue is created, **When** I view it on GitHub, **Then** it contains sections: File, Bug Description, Issue Details, Recommended Solution, and Code Context
4. **Given** issues are being created, **When** rate limiting occurs, **Then** the system waits and retries automatically with progress feedback

---

### User Story 2 - Preview Issues Before Creation (Priority: P2)

As a developer, I want to preview what issues will be created before actually creating them so that I can verify the content and avoid creating unwanted issues.

**Why this priority**: Dry-run capability prevents mistakes and gives users confidence. Important but not core functionality.

**Independent Test**: Can be tested by running `aetheris issues --dry-run` and verifying output shows issue previews without creating actual GitHub issues.

**Acceptance Scenarios**:

1. **Given** analysis reports exist, **When** I run `aetheris issues --dry-run`, **Then** I see a preview of all issues that would be created without any GitHub API calls
2. **Given** I'm in dry-run mode, **When** the preview completes, **Then** I see a summary count of issues that would be created

---

### User Story 3 - Skip Duplicate Issues (Priority: P2)

As a developer running issues command multiple times, I want the system to skip issues that already exist so that I don't create duplicates.

**Why this priority**: Essential for repeated use. Prevents issue spam and maintains clean issue tracker.

**Independent Test**: Can be tested by running `aetheris issues` twice on the same analysis and verifying no duplicate issues are created.

**Acceptance Scenarios**:

1. **Given** an issue with matching title already exists in the repository, **When** I run `aetheris issues`, **Then** that issue is skipped with a notification
2. **Given** some issues exist and some don't, **When** I run the command, **Then** only new issues are created and existing ones are reported as skipped

---

### User Story 4 - Customize Issue Properties (Priority: P3)

As a developer, I want to specify custom labels, assignees, and target repository so that issues fit my team's workflow.

**Why this priority**: Customization enhances usability but isn't required for basic functionality.

**Independent Test**: Can be tested by running `aetheris issues --labels security,urgent --assignee dev1` and verifying created issues have those properties.

**Acceptance Scenarios**:

1. **Given** I specify `--labels security,urgent`, **When** issues are created, **Then** they have labels: bug, aetheris-analysis, severity level, security, urgent
2. **Given** I specify `--assignee username`, **When** issues are created, **Then** they are assigned to that user
3. **Given** I specify `--repo owner/repo`, **When** issues are created, **Then** they are created in that repository instead of the current one

---

### User Story 5 - Process Specific Report (Priority: P3)

As a developer, I want to create issues from a specific analysis report file so that I can target particular analysis runs.

**Why this priority**: Useful for selective issue creation but most users will want all issues.

**Independent Test**: Can be tested by running `aetheris issues --from-report docs/analyses/specific-file.md` and verifying only bugs from that file generate issues.

**Acceptance Scenarios**:

1. **Given** I specify `--from-report docs/analyses/analyzer.md`, **When** the command runs, **Then** only bugs from that specific report are processed
2. **Given** the specified report doesn't exist, **When** I run the command, **Then** I receive a clear error message

---

### Edge Cases

- What happens when no analysis reports exist in `docs/analyses/`?
  - System displays informative message: "No analysis reports found. Run `aetheris analysis` first."
- What happens when an analysis report contains no bugs?
  - System reports "No bugs found in [filename]" and continues to next file
- What happens when GitHub API returns an error (other than rate limiting)?
  - System logs the error, reports which issue failed, and continues processing remaining issues
- What happens when the `gh` CLI is not installed or not authenticated?
  - System detects this upfront and provides clear instructions for installation/authentication
- What happens when a bug description in the report is malformed or unparseable?
  - System logs a warning, skips that bug, and continues processing
  - **Malformed examples**:
    - Missing `## Risques` section entirely
    - Empty bullet points under risks section
    - Bug text without clear severity indicator
    - Truncated markdown (incomplete code blocks)
    - Non-UTF8 characters causing parse errors

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a CLI command `aetheris issues` to create GitHub issues from analysis reports
- **FR-002**: System MUST parse Markdown analysis reports from `docs/analyses/` directory
- **FR-003**: System MUST extract bug information including: file path, bug type, description, issue details, recommended solution, and code context
- **FR-004**: System MUST create GitHub issues with structured body containing: File, Bug Description, Issue Details, Recommended Solution, Code Context sections
- **FR-005**: System MUST format issue titles as `[BugType] in filename - brief description`
- **FR-006**: System MUST apply default labels: `bug`, `aetheris-analysis`, and severity level (critical/high/medium/low)
- **FR-007**: System MUST use the `gh` CLI tool for GitHub API interactions
- **FR-008**: System MUST support `--dry-run` option to preview issues without creating them
- **FR-009**: System MUST support `--labels` option to add custom labels
- **FR-010**: System MUST support `--assignee` option to assign issues to a user
- **FR-011**: System MUST support `--repo` option to target a specific repository
- **FR-012**: System MUST support `--from-report` option to process a specific analysis file
- **FR-013**: System MUST handle GitHub API rate limiting with automatic retry and backoff
- **FR-014**: System MUST display progress feedback during issue creation
- **FR-015**: System MUST skip creating issues that already exist (deduplicated by title match)
- **FR-016**: System MUST validate `gh` CLI availability and authentication before processing
- **FR-017**: System MUST provide a summary report after completion showing: created, skipped, failed counts

### Key Entities

- **AnalysisReport**: Represents a parsed Markdown analysis file containing bugs, file path, and analysis metadata
- **Bug**: Represents a single bug extracted from a report - includes type, severity, description, solution, and code context
- **GitHubIssue**: Represents an issue to be created - includes title, body, labels, assignee, and repository target

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create GitHub issues from a complete analysis run in under 2 minutes for codebases with up to 50 bugs
- **SC-002**: 100% of valid bugs extracted from analysis reports result in properly formatted GitHub issues
- **SC-003**: Zero duplicate issues are created when running the command multiple times on the same analysis
- **SC-004**: Users receive clear progress feedback showing X of Y issues processed during execution
- **SC-005**: System gracefully handles rate limiting with zero lost issues (all issues eventually created after retries)
- **SC-006**: Dry-run mode shows accurate preview matching what would be created in actual run

## Assumptions

- The `gh` CLI tool is the standard interface for GitHub operations (widely adopted, well-documented)
- Analysis reports follow a consistent Markdown structure with identifiable bug sections
- Severity levels in analysis reports map to: critical, high, medium, low
- The current working directory contains a Git repository with a valid GitHub remote (for default repo detection)
- Users have write access to create issues in the target repository
