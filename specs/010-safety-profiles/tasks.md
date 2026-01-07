# Tasks: Safety Profiles

**Input**: Design documents from `/specs/010-safety-profiles/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, quickstart.md ✓
**Target Version**: v3.0.3
**Estimated LOC**: ~500-700 across 7 files

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- All paths relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create base types and infrastructure used by all profiles

- [ ] T001 Create ProfileType enum and ProfileConfig dataclass in src/core/profiles.py
- [ ] T002 [P] Create DiffBoundary dataclass in src/core/profiles.py
- [ ] T003 Add profile field to AnalysisConfig in src/core/config.py
- [ ] T004 [P] Add `--profile` CLI flag with choices (safe/ci/yolo) in src/cli.py
- [ ] T005 Display active profile at analysis start in src/cli.py

**Checkpoint**: Profile selection works, `--profile safe` accepted, profile displayed at start

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core constraint enforcement that ALL profiles need

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Create get_profile_config() function returning ProfileConfig for given ProfileType in src/core/profiles.py
- [ ] T007 Add profile constraint check hooks to AnalysisOrchestrator in src/core/orchestrator.py
- [ ] T008 [P] Create default_allowlist.json with safe command patterns in config/default_allowlist.json
- [ ] T009 Implement profile validation (reject invalid profile names with helpful error) in src/cli.py

**Checkpoint**: Foundation ready - ProfileConfig accessible, orchestrator has hooks, CLI validates input

---

## Phase 3: User Story 1 - Safe Mode (Priority: P1) 🎯 MVP

**Goal**: Implement safe profile with network blocking, allowlist, diff limits, repair loop limits, and mandatory tests

**Independent Test**: Run `aetheris analysis --profile safe` and verify:
- Auxiliary network calls blocked (web search disabled)
- Commands validated against allowlist
- Diff size enforced (500 lines max)
- Repair loops limited to 3

### Implementation for User Story 1

- [ ] T010 [P] [US1] Create AllowlistConfig dataclass with is_allowed() method in src/core/allowlist.py
- [ ] T011 [P] [US1] Create NetworkGuard context manager for network blocking in src/services/network_guard.py
- [ ] T012 [US1] Implement load_allowlist() to read and merge default + user allowlists in src/core/allowlist.py
- [ ] T013 [US1] Implement validate_command() to check command against allowlist in src/core/allowlist.py
- [ ] T014 [US1] Add ALLOWED_HOSTS list for AI providers in src/services/network_guard.py
- [ ] T015 [US1] Integrate NetworkGuard into orchestrator when profile=safe in src/core/orchestrator.py
- [ ] T016 [US1] Add diff size check before applying changes in src/core/orchestrator.py
- [ ] T017 [US1] Add repair loop counter with max=3 enforcement in src/core/orchestrator.py
- [ ] T018 [US1] Add mandatory test step before applying changes in src/core/orchestrator.py
- [ ] T019 [US1] Block changes if test step fails with clear error message in src/core/orchestrator.py

**Checkpoint**: Safe mode fully functional - network blocked, allowlist enforced, limits applied

---

## Phase 4: User Story 2 - CI Mode (Priority: P1)

**Goal**: Implement CI profile with fail-fast, no prompts, and audit logging

**Independent Test**: Run `aetheris analysis --profile ci` in headless environment and verify:
- No interactive prompts appear
- Exits with non-zero on error
- Audit log written to aetheris-audit.jsonl

### Implementation for User Story 2

- [ ] T020 [P] [US2] Create AuditLogEntry dataclass with to_jsonl() method in src/core/audit_log.py
- [ ] T021 [P] [US2] Create AuditLogger class with log_event() and flush() methods in src/core/audit_log.py
- [ ] T022 [US2] Implement is_ci_environment() detection function in src/core/profiles.py
- [ ] T023 [US2] Add fail-fast error handling (sys.exit(1) on error) for CI profile in src/core/orchestrator.py
- [ ] T024 [US2] Replace all interactive prompts with safe defaults when profile=ci in src/cli.py
- [ ] T025 [US2] Integrate AuditLogger into orchestrator for CI profile in src/core/orchestrator.py
- [ ] T026 [US2] Log analysis_started event with session_id at run start in src/core/orchestrator.py
- [ ] T027 [US2] Log file_analyzed event for each processed file in src/core/orchestrator.py
- [ ] T028 [US2] Log analysis_completed/analysis_failed at run end in src/core/orchestrator.py
- [ ] T029 [US2] Add --output json flag for machine-readable output in src/cli.py

**Checkpoint**: CI mode fully functional - no prompts, fail-fast, audit log generated

---

## Phase 5: User Story 3 - Yolo Mode (Priority: P2)

**Goal**: Implement yolo profile with risk warning, extended limits, and full network access

**Independent Test**: Run `aetheris analysis --profile yolo` and verify:
- Warning displayed and confirmation required
- Network access unrestricted
- Extended repair loops (10 iterations)
- No diff size limits

### Implementation for User Story 3

- [ ] T030 [US3] Create display_yolo_warning() function with rich formatting in src/cli.py
- [ ] T031 [US3] Add --yes flag to skip yolo confirmation in src/cli.py
- [ ] T032 [US3] Require explicit confirmation before proceeding with yolo profile in src/cli.py
- [ ] T033 [US3] Set max_repair_loops=10 for yolo profile in src/core/profiles.py
- [ ] T034 [US3] Disable diff size limit for yolo profile in src/core/orchestrator.py
- [ ] T035 [US3] Enable full network access (skip NetworkGuard) for yolo profile in src/core/orchestrator.py
- [ ] T036 [US3] Log extended operations to audit log for yolo profile in src/core/orchestrator.py
- [ ] T037 [US3] Emit warning if yolo used in CI environment in src/cli.py

**Checkpoint**: Yolo mode fully functional - warning shown, extended capabilities enabled

---

## Phase 6: User Story 4 - Default Profile Config (Priority: P3)

**Goal**: Allow project-level default profile configuration

**Independent Test**: Set `default_profile: ci` in .aetheris.json and verify profile used without --profile flag

### Implementation for User Story 4

- [ ] T038 [US4] Add default_profile field to project config schema in src/core/config.py
- [ ] T039 [US4] Implement load_project_config() to read .aetheris.json in src/core/config.py
- [ ] T040 [US4] Apply default profile from config when --profile not specified in src/cli.py
- [ ] T041 [US4] Ensure explicit --profile flag overrides config default in src/cli.py
- [ ] T042 [US4] Fall back to safe profile when no default configured in src/cli.py

**Checkpoint**: Default profile configuration works from project file

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Edge cases, documentation, and refinements

- [ ] T043 Handle invalid profile name with clear error listing valid options in src/cli.py
- [ ] T044 [P] Handle missing/malformed allowlist file gracefully (use defaults, warn) in src/core/allowlist.py
- [ ] T045 [P] Add profile info to existing --help output in src/cli.py
- [ ] T046 Validate all edge cases from spec.md work correctly
- [ ] T047 Update pyproject.toml version to 3.0.3

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup ──────────────────►
                                  │
                                  ▼
Phase 2: Foundational ───────────► BLOCKS ALL USER STORIES
                                  │
         ┌────────────────────────┼────────────────────────┐
         │                        │                        │
         ▼                        ▼                        ▼
Phase 3: US1 (Safe)     Phase 4: US2 (CI)      Phase 5: US3 (Yolo)
    [P1 MVP]                 [P1]                   [P2]
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
                                  ▼
                        Phase 6: US4 (Config)
                                [P3]
                                  │
                                  ▼
                        Phase 7: Polish
```

### User Story Dependencies

| Story | Depends On | Can Run Parallel With |
|-------|------------|----------------------|
| US1 (Safe) | Phase 2 | US2, US3 |
| US2 (CI) | Phase 2 | US1, US3 |
| US3 (Yolo) | Phase 2 | US1, US2 |
| US4 (Config) | Phase 2 | US1, US2, US3 |

### Within Each User Story

1. Dataclasses/types first (T010, T020, etc.)
2. Core logic second (T012-T015, T022-T024, etc.)
3. Orchestrator integration third (T015-T019, T025-T028, etc.)
4. CLI updates last (T029, T030-T032, T040-T042)

---

## Parallel Execution Examples

### Phase 1 Parallel Group

```bash
# Can run together:
T002 [P] Create DiffBoundary dataclass
T004 [P] Add --profile CLI flag
```

### User Story 1 Parallel Group

```bash
# Can run together:
T010 [P] [US1] Create AllowlistConfig dataclass
T011 [P] [US1] Create NetworkGuard context manager
```

### User Story 2 Parallel Group

```bash
# Can run together:
T020 [P] [US2] Create AuditLogEntry dataclass
T021 [P] [US2] Create AuditLogger class
```

### Cross-Story Parallel (after Phase 2)

```bash
# Different stories can run in parallel:
Developer A: T010-T019 (US1 Safe Mode)
Developer B: T020-T029 (US2 CI Mode)
Developer C: T030-T037 (US3 Yolo Mode)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. ✅ Complete Phase 1: Setup (T001-T005)
2. ✅ Complete Phase 2: Foundational (T006-T009)
3. ✅ Complete Phase 3: User Story 1 - Safe Mode (T010-T019)
4. **STOP and VALIDATE**: Test `--profile safe` independently
5. Deploy v3.0.3-alpha if ready

### Full Release

1. Setup + Foundational → Foundation ready
2. US1 (Safe) → Test → **MVP Ready**
3. US2 (CI) → Test → CI/CD integration ready
4. US3 (Yolo) → Test → Power user features ready
5. US4 (Config) → Test → Team configuration ready
6. Polish → Final testing → **Release v3.0.3**

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 47 |
| Phase 1 (Setup) | 5 tasks |
| Phase 2 (Foundation) | 4 tasks |
| US1 (Safe Mode) | 10 tasks |
| US2 (CI Mode) | 10 tasks |
| US3 (Yolo Mode) | 8 tasks |
| US4 (Config) | 5 tasks |
| Phase 7 (Polish) | 5 tasks |
| Parallel Opportunities | 12 tasks marked [P] |
| Files Modified | 7 |
| Files Created | 4 |

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [US#] label maps task to specific user story for traceability
- Each user story independently testable after completion
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- MVP = Phase 1 + Phase 2 + Phase 3 (Safe Mode only)
