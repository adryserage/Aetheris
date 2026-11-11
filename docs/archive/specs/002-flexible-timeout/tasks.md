# Tasks: Flexible Timeout Management

**Input**: Design documents from `/specs/002-flexible-timeout/`
**Prerequisites**: plan.md ✓, spec.md ✓
**Target Version**: v2.6.1
**Estimated LOC**: ~150-200

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel
- **[Story]**: Which user story (US1, US2, US3)

---

## Phase 1: Setup

**Purpose**: Create base types and infrastructure

- [X] T001 Create TimeoutConfig dataclass with value, enabled fields in src/core/config.py
- [X] T002 [P] Add parse() classmethod to TimeoutConfig for parsing CLI strings in src/core/config.py
- [X] T003 Add DEFAULT_TIMEOUT_SECONDS = 3600 constant in src/core/config.py
- [X] T004 Add timeout validation (reject negative, validate format) in src/core/config.py

**Checkpoint**: TimeoutConfig can parse "30m", "2h", "3600", "0", "no-limit"

---

## Phase 2: User Story 1 - Default Timeout Extension (Priority: P1)

**Goal**: Extend default timeout to 60 minutes

**Independent Test**: Run analysis without --timeout, verify 60-minute default applies

- [X] T005 [US1] Update AnalysisConfig to include timeout_config field in src/core/config.py
- [X] T006 [US1] Set default timeout to 60 minutes in AnalysisConfig in src/core/config.py
- [X] T007 [US1] Apply timeout using asyncio.wait_for() in orchestrator run() in src/core/orchestrator.py
- [X] T008 [US1] Add graceful timeout handling with context save attempt in src/core/orchestrator.py

**Checkpoint**: Default 60-minute timeout working

---

## Phase 3: User Story 2 - Custom Timeout Configuration (Priority: P1)

**Goal**: Add --timeout/-t CLI parameter

**Independent Test**: Run `aetheris analysis --timeout 30m` and verify 30-minute timeout

- [X] T009 [US2] Add --timeout/-t parameter to analysis command in src/cli.py
- [X] T010 [US2] Parse timeout value using TimeoutConfig.parse() in src/cli.py
- [X] T011 [US2] Pass parsed timeout to AnalysisConfig in src/cli.py
- [X] T012 [US2] Display active timeout in analysis start message in src/cli.py
- [X] T013 [US2] Handle timeout=0 as unlimited (skip asyncio.wait_for) in src/core/orchestrator.py

**Checkpoint**: Custom timeout via CLI working

---

## Phase 4: User Story 3 - Progress Heartbeat (Priority: P2)

**Goal**: Add heartbeat indicator every 10 minutes

**Independent Test**: Run long analysis, verify heartbeat message every 10 minutes

- [X] T014 [P] [US3] Create HeartbeatMonitor class in src/core/heartbeat.py
- [X] T015 [US3] Implement start() method with asyncio background task in src/core/heartbeat.py
- [X] T016 [US3] Implement stop() method to cancel background task in src/core/heartbeat.py
- [X] T017 [US3] Add heartbeat message format with elapsed time in src/core/heartbeat.py
- [X] T018 [US3] Integrate HeartbeatMonitor into orchestrator run() in src/core/orchestrator.py
- [X] T019 [US3] Start heartbeat at analysis begin, stop at end in src/core/orchestrator.py

**Checkpoint**: Heartbeat messages appearing every 10 minutes

---

## Phase 5: Polish & Edge Cases

**Purpose**: Handle edge cases and finalization

- [X] T020 Handle negative timeout values with clear error message in src/core/config.py
- [X] T021 Handle invalid timeout format with helpful error in src/core/config.py
- [X] T022 Handle Ctrl+C graceful interruption during long analysis in src/core/orchestrator.py
- [X] T023 Handle memory exhaustion before timeout (catch MemoryError, log and exit gracefully) in src/core/orchestrator.py
- [X] T024 [P] Add timeout info to --help output in src/cli.py
- [X] T025 Update pyproject.toml version to 2.6.1

**Checkpoint**: All edge cases handled, ready for release

---

## Dependencies & Execution Order

```
Phase 1: Setup ────────────────────►
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                    ▼                             ▼
Phase 2: US1 (Default)              Phase 3: US2 (Custom)
    [P1]                                 [P1]
                    │                             │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                        Phase 4: US3 (Heartbeat)
                                 [P2]
                                   │
                                   ▼
                          Phase 5: Polish
```

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 25 |
| Phase 1 (Setup) | 4 tasks |
| US1 (Default Timeout) | 4 tasks |
| US2 (Custom Timeout) | 5 tasks |
| US3 (Heartbeat) | 6 tasks |
| Phase 5 (Polish) | 6 tasks |
| Files Modified | 4 |
| Files Created | 1 |
