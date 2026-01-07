# Tasks: GitHub PR Generator

**Input**: Design documents from `/specs/002-github-pr-generator/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, quickstart.md ✅

**Tests**: Not explicitly requested - using `--dry-run` for manual testing.

**Organization**: Tasks grouped by user story (5 stories: US1-US5).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (US1-US5)

---

## Phase 1: Setup

**Purpose**: Project initialization and basic structure

- [X] T001 Create feature branch `002-github-pr-generator` (already done)
- [X] T002 Create `src/services/pr_generator.py` with module docstring and imports

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story

- [X] T003 Add data classes `PROptions`, `GeneratedFix`, `PRToCreate`, `PRResult`, `PRSummary` in `src/services/pr_generator.py`
- [X] T004 Implement `validate_prerequisites()` to check git, gh CLI, and AI provider in `src/services/pr_generator.py`
- [X] T005 Implement `_run_git_command()` helper for git subprocess calls in `src/services/pr_generator.py`
- [X] T006 Implement `_run_gh_command()` helper (copy from issue_creator) in `src/services/pr_generator.py`
- [X] T007 Add `setup_pr_generator_parser()` function in `src/cli.py` following `setup_issues_parser()` pattern
- [X] T008 Register pr-gen subcommand in `main()` function in `src/cli.py`

**Checkpoint**: CLI accepts `aetheris pr-gen --help` ✅

---

## Phase 3: User Story 1 - Generate PRs from Bugs (Priority: P1) 🎯 MVP

**Goal**: Parse bugs and create PRs with AI-generated fixes

**Independent Test**: Run `aetheris pr`, verify branches and PRs appear in GitHub

### Implementation for User Story 1

- [X] T009 [US1] Import and reuse bug parsing from `issue_creator.py` in `src/services/pr_generator.py`
- [X] T010 [US1] Implement `generate_branch_name()` method with format `fix/<type>-<file>-<hash>` in `src/services/pr_generator.py`
- [X] T011 [US1] Implement `read_source_file()` to get file content for AI context in `src/services/pr_generator.py`
- [X] T012 [US1] Implement `build_fix_prompt()` to create AI prompt from bug info in `src/services/pr_generator.py`
- [X] T013 [US1] Implement `generate_fix()` method using AI provider in `src/services/pr_generator.py`
- [X] T014 [US1] Implement `validate_fix()` method for syntax checking in `src/services/pr_generator.py`
- [X] T015 [US1] Implement `create_branch()` method using git commands in `src/services/pr_generator.py`
- [X] T016 [US1] Implement `apply_fix()` to write fixed code to file in `src/services/pr_generator.py`
- [X] T017 [US1] Implement `commit_fix()` with conventional commit message in `src/services/pr_generator.py`
- [X] T018 [US1] Implement `push_branch()` to push to origin in `src/services/pr_generator.py`
- [X] T019 [US1] Implement `format_pr_body()` with markdown template in `src/services/pr_generator.py`
- [X] T020 [US1] Implement `format_pr_title()` with `fix: [Type] in file - desc` format in `src/services/pr_generator.py`
- [X] T021 [US1] Implement `create_pr()` using `gh pr create` in `src/services/pr_generator.py`
- [X] T022 [US1] Implement `restore_file()` to reset file after PR creation in `src/services/pr_generator.py`
- [X] T023 [US1] Implement main `run()` orchestration method in `src/services/pr_generator.py`
- [X] T024 [US1] Implement `run_pr_generator()` async function in `src/cli.py`
- [X] T025 [US1] Add Rich progress bar for PR creation in `src/services/pr_generator.py`
- [X] T026 [US1] Add summary report output (created/failed counts) in `src/services/pr_generator.py`

**Checkpoint**: `aetheris pr-gen` creates PRs from analysis reports ✅

---

## Phase 4: User Story 2 - Link PRs to Issues (Priority: P2)

**Goal**: Auto-link PRs to corresponding GitHub issues

**Independent Test**: Run `aetheris pr --link-issues`, verify PRs have "Fixes #N"

### Implementation for User Story 2

- [X] T027 [US2] Implement `get_existing_issues()` method to fetch issues from repo in `src/services/pr_generator.py`
- [X] T028 [US2] Implement `find_matching_issue()` to match bug to issue by title in `src/services/pr_generator.py`
- [X] T029 [US2] Add `--link-issues` argument to pr-gen parser in `src/cli.py`
- [X] T030 [US2] Add `--issue-number` argument for explicit linking in `src/cli.py`
- [X] T031 [US2] Modify `format_pr_body()` to include `Fixes #N` when linked in `src/services/pr_generator.py`

**Checkpoint**: PRs link to issues with "Fixes #N" ✅

---

## Phase 5: User Story 3 - Preview Mode (Priority: P2)

**Goal**: Preview PRs and fixes with --dry-run

**Independent Test**: Run `aetheris pr --dry-run`, verify no git/GitHub operations

### Implementation for User Story 3

- [X] T032 [US3] Add `--dry-run` argument to pr-gen parser in `src/cli.py`
- [X] T033 [US3] Implement `_print_dry_run_preview()` for fix and PR preview in `src/services/pr_generator.py`
- [X] T034 [US3] Modify `run()` to skip git/gh operations in dry-run mode in `src/services/pr_generator.py`
- [X] T035 [US3] Add dry-run summary with "would be created" wording in `src/services/pr_generator.py`

**Checkpoint**: `aetheris pr-gen --dry-run` shows preview without creating PRs ✅

---

## Phase 6: User Story 4 - Process Specific Bug (Priority: P3)

**Goal**: Filter to specific report or bug index

**Independent Test**: Run `aetheris pr --from-report file.md`, verify only that file processed

### Implementation for User Story 4

- [X] T036 [US4] Add `--from-report` argument to pr-gen parser in `src/cli.py`
- [X] T037 [US4] Add `--bug-index` argument for single bug processing in `src/cli.py`
- [X] T038 [US4] Modify bug parsing to respect from_report and bug_index filters in `src/services/pr_generator.py`

**Checkpoint**: Filtering works correctly ✅

---

## Phase 7: User Story 5 - Custom Base Branch (Priority: P3)

**Goal**: Target specific branch for PRs

**Independent Test**: Run `aetheris pr --base-branch develop`, verify PRs target develop

### Implementation for User Story 5

- [X] T039 [US5] Add `--base-branch` argument to pr-gen parser in `src/cli.py`
- [X] T040 [US5] Implement `get_default_branch()` to detect repo default in `src/services/pr_generator.py`
- [X] T041 [US5] Modify `create_branch()` to branch from specified base in `src/services/pr_generator.py`
- [X] T042 [US5] Modify `create_pr()` to target specified base branch in `src/services/pr_generator.py`

**Checkpoint**: PRs target correct base branch ✅

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Error handling and edge cases

- [X] T043 [P] Add exponential backoff for rate limiting in `src/services/pr_generator.py`
- [X] T044 [P] Add branch existence check before creating in `src/services/pr_generator.py`
- [X] T045 [P] Add source file existence check before processing in `src/services/pr_generator.py`
- [X] T046 Handle AI fix generation failures with placeholder PR in `src/services/pr_generator.py`
- [X] T047 Add help text and examples to CLI argument descriptions in `src/cli.py`
- [ ] T048 Run manual testing using quickstart.md validation steps

---

## Summary

| Metric | Count |
|--------|-------|
| Total Tasks | 48 |
| Setup Tasks | 2 |
| Foundational Tasks | 6 |
| US1 Tasks | 18 |
| US2 Tasks | 5 |
| US3 Tasks | 4 |
| US4 Tasks | 3 |
| US5 Tasks | 4 |
| Polish Tasks | 6 |

**MVP Scope**: Phases 1-3 (26 tasks) delivers core PR generation functionality.
