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
- [ ] T005 Add preset schema to ConfigSchema (default_preset, custom_presets) in src/core/config_schema.py

**Checkpoint**: Data models ready

---

## Phase 2: User Story 1 - Selective Agent Analysis (Priority: P1)

- [ ] T006 [US1] Create AgentSelector class in src/core/agent_selector.py
- [ ] T007 [US1] Implement parse_agents() for comma-separated list in src/core/agent_selector.py
- [ ] T008 [US1] Implement get_selected_agents() returning agent list in src/core/agent_selector.py
- [ ] T009 [US1] Add --agents parameter to analysis command in src/cli.py
- [ ] T010 [US1] Validate agent names and show valid options on error in src/cli.py
- [ ] T011 [US1] Integrate AgentSelector into orchestrator in src/core/orchestrator.py
- [ ] T012 [US1] Handle `--agents none` (disable optional agents) in src/core/agent_selector.py
- [ ] T013 [US1] Handle `--agents core` (6 base agents only) in src/core/agent_selector.py

**Checkpoint**: Selective agent analysis working

---

## Phase 3: User Story 2 - Targeted Fix (Priority: P1)

- [ ] T014 [US2] Create CategoryFilter class in src/core/fix_categories.py
- [ ] T015 [US2] Implement filter_issues_by_category() in src/core/fix_categories.py
- [ ] T016 [US2] Add --category parameter to fix command in src/cli.py
- [ ] T017 [US2] Integrate CategoryFilter into fix workflow in src/core/orchestrator.py
- [ ] T018 [US2] Preserve non-targeted issues in report (skip, don't delete) in src/core/orchestrator.py
- [ ] T019 [US2] Handle `--category compliance --compliance gdpr` in src/cli.py

**Checkpoint**: Targeted fix by category working

---

## Phase 4: User Story 3 - Presets (Priority: P2)

- [ ] T020 [US3] Implement load_presets() from JSON and config.json in src/core/presets.py
- [ ] T021 [US3] Implement get_preset() by name with ConfigHierarchy lookup in src/core/presets.py
- [ ] T022 [US3] Add --preset parameter to analysis command in src/cli.py
- [ ] T023 [US3] Implement preset + agents merge (union) in src/core/agent_selector.py
- [ ] T024 [US3] Support custom presets from config.json (user-defined) in src/core/presets.py
- [ ] T025 [US3] Add preset descriptions to --help output in src/cli.py
- [ ] T026 [US3] Add "Presets" tab to settings UI in src/core/settings_ui.py

**Checkpoint**: Presets working with config.json integration

---

## Phase 5: User Story 4 - Interactive Mode (Priority: P2)

- [ ] T027 [US4] Create InteractiveAgentSelector class in src/core/interactive_select.py
- [ ] T028 [US4] Implement checkbox menu with Rich in src/core/interactive_select.py
- [ ] T029 [US4] Display agent descriptions in menu in src/core/interactive_select.py
- [ ] T030 [US4] Add --interactive parameter to analysis command in src/cli.py
- [ ] T031 [US4] Pre-select preset agents when --preset combined in src/core/interactive_select.py
- [ ] T032 [US4] Handle non-interactive terminals (skip menu) in src/core/interactive_select.py

**Checkpoint**: Interactive selection working

---

## Phase 6: User Story 5 - Progress Reporting (Priority: P3)

- [ ] T033 [US5] Implement CategoryProgress tracking in src/core/fix_categories.py
- [ ] T034 [US5] Display per-category progress bars during fix in src/cli.py
- [ ] T035 [US5] Generate category summary table at fix completion in src/cli.py

**Checkpoint**: Category progress visible

---

## Phase 7: Polish & Edge Cases

- [ ] T036 Handle invalid preset name with list of valid options in src/cli.py
- [ ] T037 Handle `--category` with no matching issues (warning, not error) in src/core/orchestrator.py
- [ ] T038 Handle `--agents none` without `--compliance` (error with helpful message) in src/core/agent_selector.py
- [ ] T039 Add agent selection defaults to settings UI in src/core/settings_ui.py
- [ ] T040 Document all presets in README in README.md
- [ ] T041 Update pyproject.toml version to 3.0.2

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 41 |
| Phase 1 (Setup) | 5 tasks |
| US1 (Selective Agent) | 8 tasks |
| US2 (Targeted Fix) | 6 tasks |
| US3 (Presets) | 7 tasks |
| US4 (Interactive) | 6 tasks |
| US5 (Progress) | 3 tasks |
| Phase 7 (Polish) | 6 tasks |
| Files Created | 5 |
| Files Modified | 4 |
