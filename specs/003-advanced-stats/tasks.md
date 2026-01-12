# Tasks: Advanced Statistics Command

**Input**: Design documents from `/specs/003-advanced-stats/`
**Prerequisites**: plan.md ✓, spec.md ✓
**Target Version**: v2.7
**Estimated LOC**: ~300-400

## Format: `[ID] [P?] [Story?] Description`

---

## Phase 1: Setup

**Purpose**: Create data models and infrastructure

- [X] T001 Create ProjectStats dataclass in src/core/stats.py
- [X] T002 [P] Create PerformanceMetrics dataclass in src/core/stats.py
- [X] T003 [P] Create ROIMetrics dataclass in src/core/stats.py
- [X] T004 Create HeuristicConfig dataclass with bug time defaults in src/core/heuristics.py
- [X] T005 Implement get_regional_rate() with locale detection in src/core/heuristics.py

**Checkpoint**: All data models defined

---

## Phase 2: User Story 1 - Project Metrics (Priority: P1)

**Goal**: Display files analyzed and lines of code

**Independent Test**: Run `aetheris stats` and see file/LOC counts

- [X] T006 [US1] Create StatsCollector class in src/core/stats_collector.py
- [X] T007 [US1] Implement load_stats() to read from JSON cache in src/core/stats_collector.py
- [X] T008 [US1] Implement save_stats() to persist to JSON cache in src/core/stats_collector.py
- [X] T009 [US1] Add stats command to CLI with Rich table output in src/cli.py
- [X] T010 [US1] Display "No analyses found" message when stats empty in src/cli.py

**Checkpoint**: Basic stats command working

---

## Phase 3: User Story 2 - Performance Metrics (Priority: P1)

**Goal**: Display bugs detected/resolved and time spent

**Independent Test**: Run `aetheris stats` and see bug counts and times

- [X] T011 [US2] Add record_analysis() method to StatsCollector in src/core/stats_collector.py
- [X] T012 [US2] Add record_bug_detected() method to StatsCollector in src/core/stats_collector.py
- [X] T013 [US2] Add record_bug_resolved() method to StatsCollector in src/core/stats_collector.py
- [X] T014 [US2] Integrate StatsCollector into orchestrator analysis flow in src/core/orchestrator.py
- [X] T015 [US2] Display performance metrics in stats table in src/cli.py

**Checkpoint**: Performance metrics displayed

---

## Phase 4: User Story 3 - ROI Metrics (Priority: P2)

**Goal**: Calculate and display time/money saved

**Independent Test**: Run `aetheris stats` and see ROI calculations

- [X] T016 [US3] Implement calculate_human_time_saved() in src/core/heuristics.py
- [X] T017 [US3] Implement calculate_money_saved() in src/core/heuristics.py
- [X] T018 [US3] Add --hourly-rate parameter to stats command in src/cli.py
- [X] T019 [US3] Display ROI metrics section in stats table in src/cli.py
- [X] T020 [US3] Format currency based on region (€, $CAD, $USD) in src/cli.py

**Checkpoint**: ROI calculations displayed

---

## Phase 5: User Story 4 - Regenerate Statistics (Priority: P3)

**Goal**: Allow recalculation of ROI with updated heuristics

**Independent Test**: Run `aetheris stats --regenerate` and see recalculated values

- [X] T021 [US4] Add --regenerate flag to stats command in src/cli.py
- [X] T022 [US4] Implement regenerate_roi() method in StatsCollector in src/core/stats_collector.py
- [X] T023 [US4] Display confirmation message after regeneration in src/cli.py

**Checkpoint**: Regeneration working

---

## Phase 6: Polish & Edge Cases

**Purpose**: Handle edge cases and finalization

- [X] T024 Handle corrupted stats file gracefully (reset with warning) in src/core/stats_collector.py
- [X] T025 Handle partial/interrupted analyses in stats collection in src/core/stats_collector.py
- [X] T026 Validate hourly rate (reject negative values) in src/cli.py
- [X] T027 [P] Add stats info to --help output in src/cli.py
- [X] T028 Update pyproject.toml version to 2.7

**Checkpoint**: All edge cases handled, ready for release

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 28 |
| Phase 1 (Setup) | 5 tasks |
| US1 (Project Metrics) | 5 tasks |
| US2 (Performance Metrics) | 5 tasks |
| US3 (ROI Metrics) | 5 tasks |
| US4 (Regenerate) | 3 tasks |
| Phase 6 (Polish) | 5 tasks |
| Files Created | 3 |
| Files Modified | 2 |
