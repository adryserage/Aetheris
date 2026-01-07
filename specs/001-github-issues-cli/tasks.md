# Tasks: GitHub Issues CLI Command

**Input**: Design documents from `/specs/001-github-issues-cli/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, quickstart.md ✅

**Tests**: Not explicitly requested - using `--dry-run` for manual testing as specified in plan.

**Organization**: Tasks grouped by user story (5 stories: US1-US5) for independent implementation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (US1-US5)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/` at repository root (existing Aetheris structure)

---

## Phase 1: Setup

**Purpose**: Project initialization and basic structure

- [x] T001 Create feature branch `001-github-issues-cli` (already done via /speckit.specify)
- [x] T002 Create `src/services/issue_creator.py` with module docstring and imports

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Add data classes `ExtractedBug`, `IssueOptions`, `IssueToCreate`, `IssueResult`, `IssuesSummary` in `src/services/issue_creator.py`
- [x] T004 Implement `validate_gh_cli()` method to check `gh` CLI installation and authentication in `src/services/issue_creator.py`
- [x] T005 Implement `_run_gh_command()` helper for subprocess calls with error handling in `src/services/issue_creator.py`
- [x] T006 Add `setup_issues_parser()` function stub in `src/cli.py` following `setup_analysis_parser()` pattern
- [x] T007 Register issues subcommand in `main()` function in `src/cli.py`

**Checkpoint**: Foundation ready - CLI accepts `aetheris issues --help`

---

## Phase 3: User Story 1 - Create GitHub Issues from Analysis (Priority: P1) 🎯 MVP

**Goal**: Parse analysis reports and create GitHub issues for each bug found

**Independent Test**: Run `aetheris issues` after analysis, verify issues appear in GitHub

### Implementation for User Story 1

- [x] T008 [US1] Implement `parse_single_report()` method to extract bugs from one markdown file in `src/services/issue_creator.py`
- [x] T009 [US1] Implement regex patterns for `## Risques` section parsing in `src/services/issue_creator.py`
- [x] T010 [US1] Implement `parse_reports()` method to scan `docs/analyses/` directory in `src/services/issue_creator.py`
- [x] T011 [US1] Implement `format_issue_body()` method with markdown template in `src/services/issue_creator.py`
- [x] T012 [US1] Implement `format_issue_title()` method with `[Type] in file - desc` format in `src/services/issue_creator.py`
- [x] T013 [US1] Implement `get_labels_for_bug()` method with severity/type mapping in `src/services/issue_creator.py`
- [x] T014 [US1] Implement `create_issue()` method using `gh issue create` in `src/services/issue_creator.py`
- [x] T015 [US1] Implement basic `run()` orchestration method in `src/services/issue_creator.py`
- [x] T016 [US1] Implement `run_issues()` async function in `src/cli.py`
- [x] T017 [US1] Add Rich progress bar for issue creation progress in `src/services/issue_creator.py`
- [x] T018 [US1] Add summary report output (created/failed counts) in `src/services/issue_creator.py`

**Checkpoint**: `aetheris issues` creates issues from analysis reports

---

## Phase 4: User Story 2 - Preview Issues (Priority: P2)

**Goal**: Preview issues before creating them with `--dry-run`

**Independent Test**: Run `aetheris issues --dry-run`, verify no GitHub API calls made

### Implementation for User Story 2

- [x] T019 [US2] Add `--dry-run` argument to issues parser in `src/cli.py`
- [x] T020 [US2] Modify `run()` to skip `create_issue()` when dry_run=True in `src/services/issue_creator.py`
- [x] T021 [US2] Add formatted preview output for each issue in dry-run mode in `src/services/issue_creator.py`
- [x] T022 [US2] Add dry-run summary (X issues would be created) in `src/services/issue_creator.py`

**Checkpoint**: `aetheris issues --dry-run` shows preview without creating issues

---

## Phase 5: User Story 3 - Skip Duplicate Issues (Priority: P2)

**Goal**: Avoid creating issues that already exist in the repository

**Independent Test**: Run `aetheris issues` twice, verify second run skips existing issues

### Implementation for User Story 3

- [x] T023 [US3] Implement `get_existing_issues()` method using `gh issue list --json title` in `src/services/issue_creator.py`
- [x] T024 [US3] Add title matching logic to check for duplicates in `src/services/issue_creator.py`
- [x] T025 [US3] Modify `run()` to skip issues with matching titles in `src/services/issue_creator.py`
- [x] T026 [US3] Add "skipped (already exists)" output for duplicate issues in `src/services/issue_creator.py`
- [x] T027 [US3] Update summary to include skipped count in `src/services/issue_creator.py`

**Checkpoint**: Second run of `aetheris issues` skips all existing issues

---

## Phase 6: User Story 4 - Customize Issue Properties (Priority: P3)

**Goal**: Allow custom labels, assignees, and target repository

**Independent Test**: Run `aetheris issues --labels test --assignee user`, verify issue properties

### Implementation for User Story 4

- [x] T028 [P] [US4] Add `--labels` argument to issues parser in `src/cli.py`
- [x] T029 [P] [US4] Add `--assignee` argument to issues parser in `src/cli.py`
- [x] T030 [P] [US4] Add `--repo` argument to issues parser in `src/cli.py`
- [x] T031 [US4] Modify `create_issue()` to include custom labels in `src/services/issue_creator.py`
- [x] T032 [US4] Modify `create_issue()` to include assignee if provided in `src/services/issue_creator.py`
- [x] T033 [US4] Modify `_run_gh_command()` to use custom repo if provided in `src/services/issue_creator.py`

**Checkpoint**: Custom labels, assignees, and repo work correctly

---

## Phase 7: User Story 5 - Process Specific Report (Priority: P3)

**Goal**: Create issues from a specific analysis report file only

**Independent Test**: Run `aetheris issues --from-report docs/analyses/file.md`, verify only that file processed

### Implementation for User Story 5

- [x] T034 [US5] Add `--from-report` argument to issues parser in `src/cli.py`
- [x] T035 [US5] Modify `parse_reports()` to accept optional single file path in `src/services/issue_creator.py`
- [x] T036 [US5] Add validation for report file existence in `src/services/issue_creator.py`
- [x] T037 [US5] Add clear error message when specified report not found in `src/services/issue_creator.py`

**Checkpoint**: `--from-report` filters to single file correctly

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T038 [P] Add exponential backoff for rate limiting in `src/services/issue_creator.py`
- [x] T039 [P] Add graceful error handling for GitHub API errors in `src/services/issue_creator.py`
- [x] T040 Validate all edge cases from spec (no reports, empty reports, malformed bugs) in `src/services/issue_creator.py`
- [x] T041 Add help text and examples to CLI argument descriptions in `src/cli.py`
- [ ] T042 Run manual testing using quickstart.md validation steps
- [x] T043 Update pyproject.toml if new dependencies needed (no new deps required)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - **Core MVP**
- **User Story 2 (P2)**: Can start after US1 (shares run() method)
- **User Story 3 (P2)**: Can start after US1 (shares run() method)
- **User Story 4 (P3)**: Can start after US1 (extends create_issue())
- **User Story 5 (P3)**: Can start after US1 (extends parse_reports())

### Within Each User Story

- CLI arguments before service implementation
- Service methods before CLI integration
- Core implementation before edge cases

### Parallel Opportunities

- T028, T029, T030 can run in parallel (different CLI arguments)
- All US4 CLI argument tasks marked [P]

---

## Parallel Example: User Story 4

```bash
# Launch all CLI argument tasks together:
Task: "Add --labels argument to issues parser in src/cli.py"
Task: "Add --assignee argument to issues parser in src/cli.py"
Task: "Add --repo argument to issues parser in src/cli.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T002)
2. Complete Phase 2: Foundational (T003-T007)
3. Complete Phase 3: User Story 1 (T008-T018)
4. **STOP and VALIDATE**: Run `aetheris issues` on real analysis
5. Deploy if ready - core functionality complete!

### Incremental Delivery

1. MVP: Setup + Foundational + US1 → Creates issues from analysis
2. Add US2 (--dry-run) → Safe preview mode
3. Add US3 (dedup) → Prevents duplicate issues
4. Add US4 (customize) → Labels, assignees, repo
5. Add US5 (filter) → Single report processing
6. Polish → Rate limiting, error handling

### Recommended Order

**Solo developer**: US1 → US3 → US2 → US4 → US5 → Polish
(Get core + dedup working first, then dry-run for safety)

---

## Summary

| Metric | Count |
|--------|-------|
| Total Tasks | 43 |
| Setup Tasks | 2 |
| Foundational Tasks | 5 |
| US1 Tasks | 11 |
| US2 Tasks | 4 |
| US3 Tasks | 5 |
| US4 Tasks | 6 |
| US5 Tasks | 4 |
| Polish Tasks | 6 |
| Parallel Opportunities | 4 |

**MVP Scope**: Phases 1-3 (18 tasks) delivers core issue creation functionality.

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story
- Each story independently testable after completion
- Commit after each task or logical group
- Use `--dry-run` for testing before real issue creation
