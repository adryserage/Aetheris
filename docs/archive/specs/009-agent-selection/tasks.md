# Tasks: Agent Selection & Targeted Fix

**Input**: Design documents from `/specs/009-agent-selection/`
**Target Version**: v2.11
**Estimated LOC**: ~400-500

---

## Phase 1: Setup

- [x] T001 Create AgentPreset dataclass in src/core/presets.py
- [x] T002 [P] Create FixCategory dataclass in src/core/fix_categories.py
- [x] T003 [P] Create config/presets.json with default presets
- [x] T004 Create CategoryProgress dataclass for reporting in src/core/fix_categories.py
- [x] T005 Add preset schema to ConfigSchema (default_preset, custom_presets) in src/core/config_schema.py

**Checkpoint**: Data models ready

---

## Phase 2: User Story 1 - Selective Agent Analysis (Priority: P1)

- [x] T006 [US1] Create AgentSelector class in src/core/agent_selector.py
- [x] T007 [US1] Implement parse_agents() for comma-separated list in src/core/agent_selector.py
- [x] T008 [US1] Implement get_selected_agents() returning agent list in src/core/agent_selector.py
- [x] T009 [US1] Add --agents parameter to analysis command in src/cli.py
- [x] T010 [US1] Validate agent names and show valid options on error in src/cli.py
- [x] T011 [US1] Integrate AgentSelector into orchestrator in src/core/orchestrator.py
- [x] T012 [US1] Handle `--agents none` (disable optional agents) in src/core/agent_selector.py
- [x] T013 [US1] Handle `--agents core` (6 base agents only) in src/core/agent_selector.py

**Checkpoint**: Selective agent analysis working

---

## Phase 3: User Story 2 - Targeted Fix (Priority: P1)

- [x] T014 [US2] Create CategoryFilter class in src/core/fix_categories.py
- [x] T015 [US2] Implement filter_issues_by_category() in src/core/fix_categories.py
- [x] T016 [US2] Add --category parameter to fix command in src/cli.py
- [x] T017 [US2] Integrate CategoryFilter into fix workflow in src/core/orchestrator.py
- [x] T018 [US2] Preserve non-targeted issues in report (skip, don't delete) in src/core/orchestrator.py
- [x] T019 [US2] Handle `--category compliance --compliance gdpr` in src/cli.py

**Checkpoint**: Targeted fix by category working

---

## Phase 4: User Story 3 - Presets (Priority: P2)

- [x] T020 [US3] Implement load_presets() from JSON and config.json in src/core/presets.py
- [x] T021 [US3] Implement get_preset() by name with ConfigHierarchy lookup in src/core/presets.py
- [x] T022 [US3] Add --preset parameter to analysis command in src/cli.py
- [x] T023 [US3] Implement preset + agents merge (union) in src/core/agent_selector.py
- [x] T024 [US3] Support custom presets from config.json (user-defined) in src/core/presets.py
- [x] T025 [US3] Add preset descriptions to --help output in src/cli.py
- [x] T026 [US3] Add "Presets" tab to settings UI in src/core/settings_ui.py

**Checkpoint**: Presets working with config.json integration

---

## Phase 5: User Story 4 - Interactive Mode (Priority: P2)

- [x] T027 [US4] Create InteractiveAgentSelector class in src/core/interactive_select.py
- [x] T028 [US4] Implement checkbox menu with Rich in src/core/interactive_select.py
- [x] T029 [US4] Display agent descriptions in menu in src/core/interactive_select.py
- [x] T030 [US4] Add --interactive parameter to analysis command in src/cli.py
- [x] T031 [US4] Pre-select preset agents when --preset combined in src/core/interactive_select.py
- [x] T032 [US4] Handle non-interactive terminals (skip menu) in src/core/interactive_select.py

**Checkpoint**: Interactive selection working

---

## Phase 6: User Story 5 - Progress Reporting (Priority: P3)

- [x] T033 [US5] Implement CategoryProgress tracking in src/core/fix_categories.py
- [x] T034 [US5] Display per-category progress bars during fix in src/cli.py
- [x] T035 [US5] Generate category summary table at fix completion in src/cli.py

**Checkpoint**: Category progress visible

---

## Phase 7: Documentation Update

- [x] T036 [DOC] Create docs/commands/agents.md with --agents flag usage and examples
- [x] T037 [DOC] Create docs/commands/presets.md with preset definitions and customization
- [x] T038 [DOC] Update docs/commands/README.md command table with new flags
- [x] T039 [DOC] Update README.md with agent selection feature section
- [x] T040 [DOC] Update README.md roadmap to mark v2.11 as implemented
- [x] T041 [DOC] Add CHANGELOG.md entry for v2.11 release

**Checkpoint**: Documentation complete

---

## Phase 8: Polish & Edge Cases

- [x] T042 Handle invalid preset name with list of valid options in src/cli.py
- [x] T043 Handle `--category` with no matching issues (warning, not error) in src/core/orchestrator.py
- [x] T044 Handle `--agents none` without `--compliance` (error with helpful message) in src/core/agent_selector.py
- [x] T045 Add agent selection defaults to settings UI in src/core/settings_ui.py
- [x] T046 Update pyproject.toml version to 2.11.0

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 46 |
| Phase 1 (Setup) | 5 tasks |
| US1 (Selective Agent) | 8 tasks |
| US2 (Targeted Fix) | 6 tasks |
| US3 (Presets) | 7 tasks |
| US4 (Interactive) | 6 tasks |
| US5 (Progress) | 3 tasks |
| Phase 7 (Documentation) | 6 tasks |
| Phase 8 (Polish) | 5 tasks |
| Files Created | 5 |
| Files Modified | 6 |
