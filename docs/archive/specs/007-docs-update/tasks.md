# Tasks: Documentation Update

**Input**: Design documents from `/specs/007-docs-update/`
**Target Version**: v2.10
**Estimated LOC**: ~500-700 (documentation)

---

## Phase 1: Setup

- [x] T001 Run `aetheris --help` and capture all commands
- [x] T002 [P] Run `aetheris <cmd> --help` for each command and capture options
- [x] T003 [P] Review current README.md structure

**Checkpoint**: Current CLI state documented

---

## Phase 2: User Story 1 - README Quick Reference (Priority: P1)

- [x] T004 [US1] Update Python version badge to 3.9+ in README.md
- [x] T005 [US1] Update Commands section with all current commands in README.md
- [x] T006 [US1] Add stats command to quick reference in README.md
- [x] T007 [US1] Update Quick Start section with current examples in README.md
- [x] T008 [US1] Verify all badges are current in README.md

**Checkpoint**: README reflects current state

---

## Phase 3: User Story 2 - Command Documentation (Priority: P1)

- [x] T009 [US2] Update docs/commands/analysis.md with all options
- [x] T010 [US2] Update docs/commands/fix.md with timeout, batch-size, severity
- [x] T011 [US2] Create docs/commands/stats.md for new stats command
- [x] T012 [US2] Review docs/commands/pr.md for completeness
- [x] T013 [US2] Review docs/commands/issues.md for completeness
- [x] T014 [US2] Review docs/commands/pr-gen.md for completeness
- [x] T015 [US2] Verify 100% option coverage vs --help output

**Checkpoint**: All commands fully documented

---

## Phase 4: User Story 3 - Configuration Reference (Priority: P2)

- [x] T016 [US3] Create docs/configuration.md
- [x] T017 [US3] Document config.json structure in docs/configuration.md
- [x] T018 [US3] Document configuration hierarchy in docs/configuration.md
- [x] T019 [US3] Document all AI providers (Gemini, Claude, OpenAI) in docs/configuration.md
- [x] T020 [US3] Document aetheris init command in docs/configuration.md
- [x] T021 [US3] Document aetheris settings command in docs/configuration.md
- [x] T022 [US3] Document secrets vs preferences separation in docs/configuration.md

**Checkpoint**: Configuration fully documented

---

## Phase 5: User Story 4 - Features Overview (Priority: P2)

- [x] T023 [US4] Update docs/features.md with multi-provider consensus
- [x] T024 [US4] Update docs/features.md with caching system
- [x] T025 [US4] Update docs/features.md with parallel analysis
- [x] T026 [US4] Update docs/features.md with ROI metrics

**Checkpoint**: Features overview current

---

## Phase 6: User Story 5 - GitHub Actions (Priority: P2)

- [x] T027 [US5] Create docs/github-actions.md
- [x] T028 [US5] Add complete workflow example in docs/github-actions.md
- [x] T029 [US5] Document required secrets in docs/github-actions.md
- [x] T030 [US5] Document changed-files-only option in docs/github-actions.md

**Checkpoint**: CI/CD integration documented

---

## Phase 7: User Story 6 - Troubleshooting (Priority: P3)

- [x] T031 [US6] Update docs/troubleshooting.md with Gemini errors
- [x] T032 [US6] Update docs/troubleshooting.md with Claude errors
- [x] T033 [US6] Update docs/troubleshooting.md with OpenAI errors
- [x] T034 [US6] Add rate-limit solutions in docs/troubleshooting.md
- [x] T035 [US6] Add timeout solutions in docs/troubleshooting.md

**Checkpoint**: Troubleshooting current

---

## Phase 8: Polish & Edge Cases

- [x] T036 Validate all internal links in documentation
- [x] T037 Update CHANGELOG.md with recent versions
- [x] T038 Verify examples are executable
- [x] T039 Add doc version header to each doc file matching package version in docs/
- [x] T040 Remove obsolete sections from docs (compare with current CLI --help) in docs/
- [x] T041 Add cross-reference validation script to ensure README and docs/ are consistent in scripts/
- [x] T042 Update pyproject.toml version to 2.6.0

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 42 |
| Phase 1 (Setup) | 3 tasks |
| US1 (README) | 5 tasks |
| US2 (Command Docs) | 7 tasks |
| US3 (Configuration) | 7 tasks |
| US4 (Features) | 4 tasks |
| US5 (GitHub Actions) | 4 tasks |
| US6 (Troubleshooting) | 5 tasks |
| Phase 8 (Polish) | 7 tasks |
| Files Created | 3 |
| Files Modified | 10+ |
