# Tasks: Agent Selection & Targeted Fix

**Input**: Design documents from `/specs/009-agent-selection/`
**Target Version**: v3.0.2
**Estimated LOC**: ~400-500

---

## Phase 1: Setup

- [ ] T001 Create AgentPreset dataclass in src/core/presets.py
- [ ] T002 [P] Create FixCategory dataclass in src/core/fix_categories.py
- [ ] T003 [P] Create config/presets.json with default presets
- [ ] T004 Create CategoryProgress dataclass for reporting in src/core/fix_categories.py

**Checkpoint**: Data models ready

---

## Phase 2: User Story 1 - Selective Agent Analysis (Priority: P1)

- [ ] T005 [US1] Create AgentSelector class in src/core/agent_selector.py
- [ ] T006 [US1] Implement parse_agents() for comma-separated list in src/core/agent_selector.py
- [ ] T007 [US1] Implement get_selected_agents() returning agent list in src/core/agent_selector.py
- [ ] T008 [US1] Add --agents parameter to analysis command in src/cli.py
- [ ] T009 [US1] Validate agent names and show valid options on error in src/cli.py
- [ ] T010 [US1] Integrate AgentSelector into orchestrator in src/core/orchestrator.py
- [ ] T011 [US1] Handle `--agents none` (disable optional agents) in src/core/agent_selector.py
- [ ] T012 [US1] Handle `--agents core` (6 base agents only) in src/core/agent_selector.py

**Checkpoint**: Selective agent analysis working

---

## Phase 3: User Story 2 - Targeted Fix (Priority: P1)

- [ ] T013 [US2] Create CategoryFilter class in src/core/fix_categories.py
- [ ] T014 [US2] Implement filter_issues_by_category() in src/core/fix_categories.py
- [ ] T015 [US2] Add --category parameter to fix command in src/cli.py
- [ ] T016 [US2] Integrate CategoryFilter into fix workflow in src/core/orchestrator.py
- [ ] T017 [US2] Preserve non-targeted issues in report (skip, don't delete) in src/core/orchestrator.py
- [ ] T018 [US2] Handle `--category compliance --compliance gdpr` in src/cli.py

**Checkpoint**: Targeted fix by category working

---

## Phase 4: User Story 3 - Presets (Priority: P2)

- [ ] T019 [US3] Implement load_presets() from JSON in src/core/presets.py
- [ ] T020 [US3] Implement get_preset() by name in src/core/presets.py
- [ ] T021 [US3] Add --preset parameter to analysis command in src/cli.py
- [ ] T022 [US3] Implement preset + agents merge (union) in src/core/agent_selector.py
- [ ] T023 [US3] Support custom presets from config.json in src/core/presets.py
- [ ] T024 [US3] Add preset descriptions to --help output in src/cli.py

**Checkpoint**: Presets working

---

## Phase 5: User Story 4 - Interactive Mode (Priority: P2)

- [ ] T025 [US4] Create InteractiveAgentSelector class in src/core/interactive_select.py
- [ ] T026 [US4] Implement checkbox menu with Rich in src/core/interactive_select.py
- [ ] T027 [US4] Display agent descriptions in menu in src/core/interactive_select.py
- [ ] T028 [US4] Add --interactive parameter to analysis command in src/cli.py
- [ ] T029 [US4] Pre-select preset agents when --preset combined in src/core/interactive_select.py
- [ ] T030 [US4] Handle non-interactive terminals (skip menu) in src/core/interactive_select.py

**Checkpoint**: Interactive selection working

---

## Phase 6: User Story 5 - Progress Reporting (Priority: P3)

- [ ] T031 [US5] Implement CategoryProgress tracking in src/core/fix_categories.py
- [ ] T032 [US5] Display per-category progress bars during fix in src/cli.py
- [ ] T033 [US5] Generate category summary table at fix completion in src/cli.py

**Checkpoint**: Category progress visible

---

## Phase 7: Polish

- [ ] T034 Handle invalid preset name with list of valid options in src/cli.py
- [ ] T035 Handle `--category` with no matching issues (warning, not error) in src/core/orchestrator.py
- [ ] T036 Document all presets in README in README.md
- [ ] T037 Update pyproject.toml version to 3.0.2

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 37 |
| Files Created | 5 |
| Files Modified | 3 |
