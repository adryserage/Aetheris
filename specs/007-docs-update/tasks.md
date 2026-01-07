# Tasks: Documentation Update

**Input**: Design documents from `/specs/007-docs-update/`
**Target Version**: v2.6.0
**Estimated LOC**: ~500-700 (documentation)

---

## Phase 1: Setup

- [ ] T001 Run `aetheris --help` and capture all commands
- [ ] T002 [P] Run `aetheris <cmd> --help` for each command and capture options
- [ ] T003 [P] Review current README.md structure

**Checkpoint**: Current CLI state documented

---

## Phase 2: User Story 1 - README Quick Reference (Priority: P1)

- [ ] T004 [US1] Update Python version badge to 3.9+ in README.md
- [ ] T005 [US1] Update Commands section with all current commands in README.md
- [ ] T006 [US1] Add stats command to quick reference in README.md
- [ ] T007 [US1] Update Quick Start section with current examples in README.md
- [ ] T008 [US1] Verify all badges are current in README.md

**Checkpoint**: README reflects current state

---

## Phase 3: User Story 2 - Command Documentation (Priority: P1)

- [ ] T009 [US2] Update docs/commands/analysis.md with all options
- [ ] T010 [US2] Update docs/commands/fix.md with timeout, batch-size, severity
- [ ] T011 [US2] Create docs/commands/stats.md for new stats command
- [ ] T012 [US2] Review docs/commands/pr.md for completeness
- [ ] T013 [US2] Review docs/commands/issues.md for completeness
- [ ] T014 [US2] Review docs/commands/pr-gen.md for completeness
- [ ] T015 [US2] Verify 100% option coverage vs --help output

**Checkpoint**: All commands fully documented

---

## Phase 4: User Story 3 - Configuration Reference (Priority: P2)

- [ ] T016 [US3] Create docs/configuration.md
- [ ] T017 [US3] Document config.json structure in docs/configuration.md
- [ ] T018 [US3] Document configuration hierarchy in docs/configuration.md
- [ ] T019 [US3] Document all AI providers (Gemini, Claude, OpenAI) in docs/configuration.md
- [ ] T020 [US3] Document aetheris init command in docs/configuration.md
- [ ] T021 [US3] Document aetheris settings command in docs/configuration.md
- [ ] T022 [US3] Document secrets vs preferences separation in docs/configuration.md

**Checkpoint**: Configuration fully documented

---

## Phase 5: User Story 4 - Features Overview (Priority: P2)

- [ ] T023 [US4] Update docs/features.md with multi-provider consensus
- [ ] T024 [US4] Update docs/features.md with caching system
- [ ] T025 [US4] Update docs/features.md with parallel analysis
- [ ] T026 [US4] Update docs/features.md with ROI metrics

**Checkpoint**: Features overview current

---

## Phase 6: User Story 5 - GitHub Actions (Priority: P2)

- [ ] T027 [US5] Create docs/github-actions.md
- [ ] T028 [US5] Add complete workflow example in docs/github-actions.md
- [ ] T029 [US5] Document required secrets in docs/github-actions.md
- [ ] T030 [US5] Document changed-files-only option in docs/github-actions.md

**Checkpoint**: CI/CD integration documented

---

## Phase 7: User Story 6 - Troubleshooting (Priority: P3)

- [ ] T031 [US6] Update docs/troubleshooting.md with Gemini errors
- [ ] T032 [US6] Update docs/troubleshooting.md with Claude errors
- [ ] T033 [US6] Update docs/troubleshooting.md with OpenAI errors
- [ ] T034 [US6] Add rate-limit solutions in docs/troubleshooting.md
- [ ] T035 [US6] Add timeout solutions in docs/troubleshooting.md

**Checkpoint**: Troubleshooting current

---

## Phase 8: Polish

- [ ] T036 Validate all internal links in documentation
- [ ] T037 Update CHANGELOG.md with recent versions
- [ ] T038 Verify examples are executable
- [ ] T039 Update pyproject.toml version to 2.6.0

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 39 |
| Files Created | 3 |
| Files Modified | 10+ |
