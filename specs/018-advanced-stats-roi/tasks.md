# Tasks: Advanced Statistics & ROI

**Input**: Design documents from `/specs/018-advanced-stats-roi/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/
**Version Target**: v2.6.5

## Summary

| Phase | User Story | Task Count | Priority |
|-------|------------|------------|----------|
| 1 | Setup | 3 | - |
| 2 | Foundational | 4 | - |
| 3 | US1: Dashboard | 5 | P1 🎯 MVP |
| 4 | US2: ROI Metrics | 3 | P2 |
| 5 | US3: Export | 4 | P2 |
| 6 | US4: Period Filter | 3 | P3 |
| 7 | US5: Category Breakdown | 3 | P3 |
| 8 | US6: Compare Over Time | 3 | P4 |
| 9 | Polish | 4 | - |
| **Total** | | **32** | |

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create stats_models.py file in src/models/stats_models.py
- [ ] T002 [P] Create statistics_service.py file in src/services/statistics_service.py
- [ ] T003 [P] Create stats_config.py file in src/config/stats_config.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data models and base service that MUST be complete before ANY user story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Implement AnalysisRecord dataclass with validation in src/models/stats_models.py
- [ ] T005 [P] Implement ROIParameters dataclass with defaults in src/models/stats_models.py
- [ ] T006 [P] Implement StatisticsStorage dataclass in src/models/stats_models.py
- [ ] T007 Implement base StatisticsService with storage load/save in src/services/statistics_service.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - View Analysis Statistics Dashboard (Priority: P1) 🎯 MVP

**Goal**: Display comprehensive dashboard showing total analyses, files scanned, issues detected

**Independent Test**: Run `aetheris stats` after one analysis and verify metrics display

### Implementation for User Story 1

- [ ] T008 [US1] Implement StatisticsAggregate dataclass in src/models/stats_models.py
- [ ] T009 [US1] Implement aggregate_statistics() method in StatisticsService
- [ ] T010 [US1] Implement format_dashboard() method with Rich panels in StatisticsService
- [ ] T011 [US1] Add `stats` command to CLI in src/cli.py
- [ ] T012 [US1] Implement record_analysis() hook in CodeAnalyzer to store results after each analysis

**Checkpoint**: User Story 1 fully functional - `aetheris stats` shows dashboard

---

## Phase 4: User Story 2 - Calculate and Display ROI Metrics (Priority: P2)

**Goal**: Show estimated time saved, cost savings, and incidents avoided

**Independent Test**: View ROI section in stats output and verify calculations

### Implementation for User Story 2

- [ ] T013 [US2] Implement ROICalculation dataclass in src/models/stats_models.py
- [ ] T014 [US2] Implement calculate_roi() method in StatisticsService
- [ ] T015 [US2] Add ROI panel to dashboard output in format_dashboard()

**Checkpoint**: ROI metrics displayed in dashboard

---

## Phase 5: User Story 3 - Export Statistics to Various Formats (Priority: P2)

**Goal**: Export stats to JSON, CSV, and Markdown formats

**Independent Test**: Run `aetheris stats --export json` and verify valid output file

### Implementation for User Story 3

- [ ] T016 [US3] Implement ExportReport dataclass in src/models/stats_models.py
- [ ] T017 [US3] Implement export_json() method in StatisticsService
- [ ] T018 [US3] Implement export_csv() and export_markdown() methods in StatisticsService
- [ ] T019 [US3] Add --export and --output flags to stats CLI command

**Checkpoint**: Export to JSON/CSV/MD working

---

## Phase 6: User Story 4 - Filter Statistics by Time Period (Priority: P3)

**Goal**: Filter statistics by week, month, or all time

**Independent Test**: Run `aetheris stats --period week` and verify only last 7 days shown

### Implementation for User Story 4

- [ ] T020 [US4] Implement filter_by_period() method in StatisticsService
- [ ] T021 [US4] Add --period flag to stats CLI command
- [ ] T022 [US4] Update aggregate_statistics() to accept optional period filter

**Checkpoint**: Period filtering working for week/month/all

---

## Phase 7: User Story 5 - View Metrics by Category Breakdown (Priority: P3)

**Goal**: Show issue breakdown by security, performance, quality, tech debt

**Independent Test**: View detailed stats and verify category columns in output

### Implementation for User Story 5

- [ ] T023 [US5] Implement CategoryMetrics dataclass in src/models/stats_models.py
- [ ] T024 [US5] Implement get_category_breakdown() method in StatisticsService
- [ ] T025 [US5] Add category table to dashboard output

**Checkpoint**: Category breakdown displayed in dashboard

---

## Phase 8: User Story 6 - Compare Analysis Results Over Time (Priority: P4)

**Goal**: Compare metrics between different time periods with trend indicators

**Independent Test**: Request comparison and verify delta calculations shown

### Implementation for User Story 6

- [ ] T026 [US6] Implement compare_periods() method in StatisticsService
- [ ] T027 [US6] Add trend calculation (improving/stable/regressing)
- [ ] T028 [US6] Add comparison panel to dashboard when multiple periods exist

**Checkpoint**: Comparison and trends displayed

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Edge cases, error handling, documentation

- [ ] T029 [P] Handle missing/corrupted storage file gracefully (recreate with warning)
- [ ] T030 [P] Handle empty statistics case with friendly message
- [ ] T031 [P] Add config commands for ROI parameters (aetheris config get/set stats.*)
- [ ] T032 Update models/__init__.py to export new stats models

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup
- **User Stories (Phase 3-8)**: All depend on Foundational completion
- **Polish (Phase 9)**: Can run after US1 minimum

### User Story Dependencies

- **US1 (P1)**: Can start after Phase 2 - No dependencies
- **US2 (P2)**: Can start after Phase 2 - Uses aggregate from US1
- **US3 (P2)**: Can start after Phase 2 - Uses aggregate + ROI
- **US4 (P3)**: Can start after Phase 2 - Modifies aggregate
- **US5 (P3)**: Can start after Phase 2 - Extends aggregate
- **US6 (P4)**: Depends on US4 (period filtering)

### Recommended Order

1. T001-T003 (Setup) → T004-T007 (Foundation)
2. T008-T012 (US1 - MVP Dashboard)
3. T013-T015 (US2 - ROI) + T016-T019 (US3 - Export) in parallel
4. T020-T022 (US4 - Period) + T023-T025 (US5 - Category) in parallel
5. T026-T028 (US6 - Compare)
6. T029-T032 (Polish)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 + 2: Setup and Foundation
2. Complete Phase 3: Dashboard (US1)
3. **STOP and VALIDATE**: Test `aetheris stats` independently
4. Deploy v2.6.5-alpha if needed

### Full Implementation

1. Complete all phases in order
2. Each story adds value without breaking previous
3. Commit after each user story phase

---

## Notes

- Storage files: `~/.aetheris/statistics.json` (global), `./aetheris-stats.json` (project)
- Rich library for terminal UI (already a dependency)
- Pydantic for data validation
- Default ROI params: $75/hr, 4h/critical, 2h/high, 1h/medium, 0.5h/low
