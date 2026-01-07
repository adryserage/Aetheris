# Feature Specification: GitHub PR Generator CLI Command

**Feature Branch**: `002-github-pr-generator`
**Created**: 2026-01-06
**Status**: Draft
**Input**: User description: "Create a CLI command 'pr' that generates Pull Requests for each bug/issue found during code analysis. Each bug gets its own branch and PR with the fix implementation."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate PRs from Analysis Bugs (Priority: P1)

As a developer who has run Aetheris analysis and created issues, I want to automatically generate Pull Requests with AI-generated fixes for each bug so that I can quickly address technical debt.

**Why this priority**: This is the core functionality. Without the ability to generate fix code and create PRs, the feature has no value.

**Independent Test**: Can be fully tested by running `aetheris pr` after analysis, verifying branches are created with commits and PRs appear in GitHub.

**Acceptance Scenarios**:

1. **Given** analysis reports exist with bugs, **When** I run `aetheris pr`, **Then** for each bug a branch is created with an AI-generated fix commit and a PR is opened
2. **Given** a bug describes a code issue in `src/core/analyzer.py`, **When** a PR is generated, **Then** the PR title follows format `fix: [BugType] in analyzer.py - brief description`
3. **Given** a PR is created, **When** I view it on GitHub, **Then** it contains sections: Description, Changes Made, Related Issue, and Testing Notes
4. **Given** the AI cannot generate a valid fix, **When** processing that bug, **Then** the system creates a placeholder PR with TODO markers and notifies the user

---

### User Story 2 - Link PRs to Existing Issues (Priority: P2)

As a developer, I want PRs to be automatically linked to their corresponding GitHub issues so that closing the PR closes the issue.

**Why this priority**: Linking PRs to issues is essential for workflow integration but requires issues to exist first.

**Independent Test**: Can be tested by running `aetheris pr --link-issues` and verifying PRs contain "Fixes #123" references.

**Acceptance Scenarios**:

1. **Given** an issue exists with title matching the bug, **When** a PR is created, **Then** the PR body includes `Fixes #<issue_number>` for auto-close
2. **Given** I specify `--issue-number 42`, **When** the PR is created, **Then** it links specifically to issue #42
3. **Given** no matching issue exists, **When** the PR is created, **Then** the PR body notes "Related analysis bug" without auto-close link

---

### User Story 3 - Preview PRs Before Creation (Priority: P2)

As a developer, I want to preview what PRs and fixes will be generated before actually creating them so that I can verify the AI-generated code quality.

**Why this priority**: Dry-run capability prevents mistakes and gives users confidence in AI-generated code.

**Independent Test**: Can be tested by running `aetheris pr --dry-run` and verifying output shows PR previews with code diffs without creating actual branches or PRs.

**Acceptance Scenarios**:

1. **Given** analysis reports exist, **When** I run `aetheris pr --dry-run`, **Then** I see a preview of all PRs and code changes without any GitHub API calls or git operations
2. **Given** I'm in dry-run mode, **When** the preview completes, **Then** I see the generated fix code for review before committing
3. **Given** dry-run shows a poor fix, **When** I review it, **Then** I can skip that bug when running the real command

---

### User Story 4 - Process Specific Bug (Priority: P3)

As a developer, I want to generate a PR for a specific bug or from a specific report so that I can address high-priority issues first.

**Why this priority**: Useful for selective PR creation but most users will want all PRs.

**Independent Test**: Can be tested by running `aetheris pr --from-report docs/analyses/file.md` and verifying only bugs from that file generate PRs.

**Acceptance Scenarios**:

1. **Given** I specify `--from-report docs/analyses/analyzer.md`, **When** the command runs, **Then** only bugs from that specific report are processed
2. **Given** I specify `--bug-index 0`, **When** the command runs, **Then** only the first bug generates a PR
3. **Given** the specified report doesn't exist, **When** I run the command, **Then** I receive a clear error message

---

### User Story 5 - Custom Base Branch (Priority: P3)

As a developer working with Git Flow, I want to specify the base branch for PRs so that they target the correct branch (develop, main, etc.).

**Why this priority**: Important for team workflows but has a sensible default (main/develop).

**Independent Test**: Can be tested by running `aetheris pr --base-branch develop` and verifying PRs target the develop branch.

**Acceptance Scenarios**:

1. **Given** I specify `--base-branch develop`, **When** PRs are created, **Then** they target the develop branch
2. **Given** no base branch specified, **When** PRs are created, **Then** they target the repository's default branch
3. **Given** the specified base branch doesn't exist, **When** I run the command, **Then** I receive a clear error message

---

### Edge Cases

- What happens when no analysis reports exist in `docs/analyses/`?
  - System displays informative message: "No analysis reports found. Run `aetheris analysis` first."
- What happens when the AI fails to generate valid fix code?
  - System creates a skeleton PR with TODO markers and a note explaining the fix needs manual implementation
- What happens when a branch with the same name already exists?
  - System skips that bug with message "Branch already exists, skipping" and continues processing
- What happens when the user doesn't have push access to the repository?
  - System detects this upfront and provides clear error message
- What happens when the fix introduces syntax errors?
  - System validates generated code with language-specific linter before committing; if invalid, creates placeholder PR
- What happens when rate limiting occurs?
  - System implements exponential backoff and retries
- What happens when the source file has been deleted since analysis?
  - System skips that bug with message "Source file not found, skipping"

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a CLI command `aetheris pr` to create PRs from analysis reports
- **FR-002**: System MUST reuse bug parsing logic from `issue_creator.py`
- **FR-003**: System MUST create a new git branch for each bug with format `fix/<bug-type>-<filename>-<short-hash>`
- **FR-004**: System MUST use AI to generate fix code based on bug description and file context
- **FR-005**: System MUST commit the generated fix to the branch with a conventional commit message
- **FR-006**: System MUST create a GitHub PR with structured body: Description, Changes, Related Issue, Testing Notes
- **FR-007**: System MUST format PR titles as `fix: [BugType] in filename - brief description`
- **FR-008**: System MUST support `--dry-run` option to preview PRs and fixes without creating them
- **FR-009**: System MUST support `--base-branch` option to specify target branch
- **FR-010**: System MUST support `--from-report` option to process a specific analysis file
- **FR-011**: System MUST support `--issue-number` option to link PR to a specific issue
- **FR-012**: System MUST support `--link-issues` option to auto-detect and link matching issues
- **FR-013**: System MUST validate generated code before committing (syntax check)
- **FR-014**: System MUST handle rate limiting with automatic retry and backoff
- **FR-015**: System MUST display progress feedback during PR creation
- **FR-016**: System MUST skip bugs where a branch already exists
- **FR-017**: System MUST validate git and gh CLI availability before processing
- **FR-018**: System MUST provide a summary report showing: created, skipped, failed counts

### Key Entities

- **Bug**: Extracted from analysis reports (reuse ExtractedBug from issue_creator)
- **GeneratedFix**: AI-generated code fix with file path, original code, and new code
- **PRToCreate**: Prepared PR with title, body, branch name, commits, and linked issue

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can generate PRs for a complete analysis run in under 5 minutes for codebases with up to 20 bugs
- **SC-002**: At least 70% of AI-generated fixes should be syntactically valid
- **SC-003**: 100% of PRs should have proper linking to related issues when `--link-issues` is used
- **SC-004**: Users receive clear progress feedback showing X of Y PRs processed during execution
- **SC-005**: System gracefully handles rate limiting with zero lost PRs (all PRs eventually created after retries)
- **SC-006**: Dry-run mode shows accurate preview matching what would be created in actual run

## Assumptions

- The `gh` CLI tool is installed and authenticated (same as issues command)
- The user has push access to create branches and PRs
- AI provider (Gemini/OpenAI/Claude) is configured for fix generation
- The codebase uses conventional commit format
- Branch naming follows `fix/<type>-<file>-<hash>` pattern
