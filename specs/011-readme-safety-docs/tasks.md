# Tasks: README Safety & Trust Documentation

**Input**: Design documents from `/specs/011-readme-safety-docs/`
**Prerequisites**: plan.md ✓, spec.md ✓
**Target Version**: v2.12
**Estimated Effort**: ~100-150 lines of markdown

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- All paths relative to repository root

---

## Phase 1: Setup

**Purpose**: Understand current README structure and fix command behavior

- [ ] T001 Review current README.md structure and identify insertion point (after Commands, before Features)
- [ ] T002 [P] Review src/cli.py fix command to understand actual execution boundaries
- [ ] T003 [P] Review docs/commands/fix.md for existing documentation

**Checkpoint**: Understand exactly what to document and where to place it

---

## Phase 2: User Story 1 - Safety & Execution Model Section (Priority: P1) 🎯 MVP

**Goal**: Add Safety & Execution Model section explaining execution boundaries and dangerous flags

**Independent Test**: Read the Safety section and answer: "What runs? Where? With what permissions?"

### Implementation for User Story 1

- [ ] T004 [US1] Add "## 🔒 Safety & Execution Model" heading after Commands section in README.md
- [ ] T005 [US1] Write "Local-Only by Default" subsection (no cloud, no telemetry) in README.md
- [ ] T006 [US1] Write "Safety Profiles" subsection documenting --profile safe|ci|yolo in README.md
- [ ] T007 [US1] Write "Execution Boundaries" subsection describing fix command scope in README.md
- [ ] T008 [US1] Write "--dangerously-skip-permissions" subsection explaining the flag in README.md
- [ ] T009 [US1] Add warning emoji/formatting to dangerous flag documentation in README.md

**Checkpoint**: Safety section complete with execution model and profiles documented

---

## Phase 3: User Story 2 - Safe Usage Examples (Priority: P1)

**Goal**: Provide actionable safe usage patterns

**Independent Test**: Follow Docker example and verify sandboxed execution works

### Implementation for User Story 2

- [ ] T010 [US2] Write "Configuring Safety via config.json" subsection in README.md
- [ ] T011 [US2] Document default_profile setting in config.json in README.md
- [ ] T012 [US2] Write "Running Safely" subsection in README.md
- [ ] T013 [US2] Add Docker sandboxed execution example (copy-paste ready) in README.md
- [ ] T014 [US2] Add recommended practices bullet points in README.md

**Checkpoint**: Safe usage examples complete with config.json reference

---

## Phase 4: User Story 3 - Fix Guarantees Section (Priority: P2)

**Goal**: Document explicit guarantees and limitations

**Independent Test**: Read guarantees and verify they match actual behavior

### Implementation for User Story 3

- [ ] T015 [US3] Add "## ✅ Fix Guarantees" heading after Safety section in README.md
- [ ] T016 [US3] Write "What We Guarantee" subsection with checkmarks in README.md
- [ ] T017 [US3] Document guarantee: Never force-push to remote in README.md
- [ ] T018 [US3] Document guarantee: Always run tests (unless disabled) in README.md
- [ ] T019 [US3] Document guarantee: Creates branch per bug fix in README.md
- [ ] T020 [US3] Write "What We Don't Guarantee" subsection with warnings in README.md
- [ ] T021 [US3] Document limitation: May fail (won't silently continue) in README.md
- [ ] T022 [US3] Document limitation: Not all bugs found/fixed in README.md

**Checkpoint**: Guarantees section complete with clear promises and limitations

---

## Phase 5: Polish & Finalization

**Purpose**: Final touches and version bump

- [ ] T023 Review full Safety + Guarantees sections for clarity and consistency
- [ ] T024 [P] Verify markdown renders correctly on GitHub
- [ ] T025 [P] Update version to 2.12.1 in pyproject.toml
- [ ] T026 Update CHANGELOG.md with v2.12 documentation improvements

**Checkpoint**: README updated, version bumped, ready for release

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup ────────────────────►
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         │                         │                         │
         ▼                         ▼                         ▼
Phase 2: US1 (Safety)    Phase 3: US2 (Examples)   Phase 4: US3 (Guarantees)
    [P1 MVP]                  [P1]                      [P2]
         │                         │                         │
         └─────────────────────────┼─────────────────────────┘
                                   │
                                   ▼
                          Phase 5: Polish
```

### User Story Dependencies

| Story | Depends On | Can Run Parallel With |
|-------|------------|----------------------|
| US1 (Safety Model) | Phase 1 | US3 (Guarantees) |
| US2 (Safe Examples) | US1 | - |
| US3 (Guarantees) | Phase 1 | US1 (Safety Model) |

### Parallel Opportunities

```bash
# Phase 1 parallel:
T002 [P] Review fix command
T003 [P] Review fix docs

# Phase 5 parallel:
T024 [P] Verify markdown rendering
T025 [P] Update version
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: US1 - Safety Model (T004-T008)
3. **STOP and VALIDATE**: Is the safety model clear?
4. Publish if ready

### Full Release

1. Setup → Safety Model → Safe Examples → Guarantees → Polish
2. All sections reviewed
3. Version bumped to 2.12.1
4. Release

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 26 |
| Phase 1 (Setup) | 3 tasks |
| US1 (Safety Model) | 6 tasks |
| US2 (Safe Examples) | 5 tasks |
| US3 (Guarantees) | 8 tasks |
| Phase 5 (Polish) | 4 tasks |
| Parallel Opportunities | 5 tasks marked [P] |
| Files Modified | 3 (README.md, pyproject.toml, CHANGELOG.md) |

---

## Notes

- This is a documentation-only feature (no code changes)
- All changes go to README.md except version bump
- Examples should be copy-paste ready
- Dangerous flags must be visually distinct
- MVP = Phase 1 + Phase 2 (Safety Model only)
