# Tasks: CI/CD Integration - GitHub Actions Template

**Input**: Design documents from `/specs/005-cicd-template/`
**Target Version**: v2.13
**Estimated LOC**: ~300 (YAML + scripts + docs)

---

## Phase 1: Setup

- [ ] T001 Create .github/workflows/ directory if not exists
- [ ] T002 [P] Create scripts/ directory for setup scripts
- [ ] T003 [P] Create docs/github-actions.md documentation file

**Checkpoint**: Directory structure ready

---

## Phase 2: User Story 1 - Automatic Analysis (Priority: P1)

- [ ] T004 [US1] Create aetheris-analysis.yml workflow file in .github/workflows/
- [ ] T005 [US1] Add push trigger for main/develop branches in workflow
- [ ] T006 [US1] Add pull_request trigger in workflow
- [ ] T007 [US1] Add Python setup step in workflow
- [ ] T008 [US1] Add Aetheris installation step in workflow
- [ ] T009 [US1] Add analysis execution step in workflow
- [ ] T010 [US1] Add PR comment step with analysis summary in workflow

**Checkpoint**: Automatic analysis on push/PR working

---

## Phase 3: User Story 2 - Manual Trigger (Priority: P1)

- [ ] T011 [US2] Add workflow_dispatch trigger in workflow
- [ ] T012 [US2] Add mode input (analysis/fix) in workflow
- [ ] T013 [US2] Add timeout input with default 60m in workflow
- [ ] T014 [US2] Add conditional logic for fix mode in workflow

**Checkpoint**: Manual workflow trigger working

---

## Phase 4: User Story 3 - Easy Setup (Priority: P2)

- [ ] T015 [US3] Add detailed comments to workflow YAML
- [ ] T016 [US3] Add AETHERIS_API_KEY secret configuration step
- [ ] T017 [US3] Add clear error message for missing API key
- [ ] T018 [US3] Document customization options in docs/github-actions.md

**Checkpoint**: Template easy to copy and customize

---

## Phase 5: User Story 4 - Artifacts (Priority: P2)

- [ ] T019 [US4] Add artifact upload step in workflow
- [ ] T020 [US4] Create setup-local.sh script in scripts/
- [ ] T021 [US4] Create setup-local.ps1 script in scripts/
- [ ] T022 [US4] Create README.md template for artifact in scripts/
- [ ] T023 [US4] Include setup scripts in artifact

**Checkpoint**: Artifacts downloadable and usable locally

---

## Phase 6: User Story 5 - Changed Files (Priority: P2)

- [ ] T024 [US5] Add step to detect changed files in workflow
- [ ] T025 [US5] Pass changed files to --files parameter in workflow
- [ ] T026 [US5] Add full-scan input option in workflow
- [ ] T027 [US5] Handle empty changed files (skip analysis) in workflow

**Checkpoint**: Only changed files analyzed

---

## Phase 7: Documentation Update

- [ ] T028 [DOC] Update docs/github-actions.md with complete setup guide
- [ ] T029 [DOC] Create docs/commands/cicd.md with CI/CD integration reference
- [ ] T030 [DOC] Update docs/commands/README.md command table with CI/CD section
- [ ] T031 [DOC] Update README.md with CI/CD integration feature section
- [ ] T032 [DOC] Update README.md roadmap to mark v2.13 as implemented
- [ ] T033 [DOC] Add CHANGELOG.md entry for v2.13 release

**Checkpoint**: Documentation complete

---

## Phase 8: Polish & Edge Cases

- [ ] T034 Add file/folder exclusion input in workflow
- [ ] T035 Handle GitHub Actions timeout (6h limit) in workflow
- [ ] T036 Add rate-limit retry logic in workflow
- [ ] T037 Add concurrency group to prevent parallel runs on same branch in workflow
- [ ] T038 Add chmod +x step for setup scripts in workflow (Linux/macOS permissions)
- [ ] T039 Handle existing docs/analyses/ folder in setup scripts (backup or merge)
- [ ] T040 Check for AETHERIS_API_KEY in setup scripts and show instructions if missing
- [ ] T041 Update pyproject.toml version to 2.13.0

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 41 |
| Phase 1 (Setup) | 3 tasks |
| US1 (Auto Analysis) | 7 tasks |
| US2 (Manual Trigger) | 4 tasks |
| US3 (Easy Setup) | 4 tasks |
| US4 (Artifacts) | 5 tasks |
| US5 (Changed Files) | 4 tasks |
| Phase 7 (Documentation) | 6 tasks |
| Phase 8 (Polish) | 8 tasks |
| Files Created | 7 |
