# Tasks: Architecture Headless Déterministe

**Input**: Design documents from `/specs/017-headless-deterministic/`
**Target Version**: v3.1
**Estimated LOC**: ~600 (Python + JSON schemas)

---

## Phase 1: Setup

- [ ] T001 Create src/runner/ directory for headless runner module
- [ ] T002 [P] Create src/runner/__init__.py with module exports
- [ ] T003 [P] Create src/schemas/ directory for JSON schemas
- [ ] T004 [P] Create src/schemas/__init__.py

**Checkpoint**: Directory structure ready

---

## Phase 2: User Story 1 - Task File Input (Priority: P1)

- [ ] T005 [US1] Create task_file_schema.json in src/schemas/
- [ ] T006 [US1] Create TaskFile dataclass in src/runner/task_parser.py
- [ ] T007 [US1] Implement JSON parsing in TaskFileParser class
- [ ] T008 [US1] Implement YAML parsing in TaskFileParser class
- [ ] T009 [US1] Add schema validation using jsonschema library
- [ ] T010 [US1] Handle relative and absolute paths for task files
- [ ] T011 [US1] Add file size limit check (max 1MB)
- [ ] T012 [US1] Add UTF-8 encoding validation
- [ ] T013 [US1] Return JSON error for invalid task files

**Checkpoint**: Task files can be parsed and validated

---

## Phase 3: User Story 2 - Structured JSON Output (Priority: P1)

- [ ] T014 [US2] Create output_schema.json in src/schemas/
- [ ] T015 [US2] Create ExecutionResult dataclass in src/runner/output_formatter.py
- [ ] T016 [US2] Implement OutputFormatter class with to_json() method
- [ ] T017 [US2] Include status field (success/error/timeout/interrupted)
- [ ] T018 [US2] Include exit_code field (0=success, 1=error, 2=warning)
- [ ] T019 [US2] Include duration_ms field with timing
- [ ] T020 [US2] Include logs field with execution messages
- [ ] T021 [US2] Include diff field for code modifications
- [ ] T022 [US2] Include error field with message and type on failure
- [ ] T023 [US2] Add --output-file flag to write JSON to file

**Checkpoint**: All executions produce valid JSON output

---

## Phase 4: User Story 3 - Non-Interactive Mode (Priority: P1)

- [ ] T024 [US3] Create TaskRunner class in src/runner/executor.py
- [ ] T025 [US3] Add --headless flag to CLI
- [ ] T026 [US3] Disable all user prompts in headless mode
- [ ] T027 [US3] Resolve confirmations via security profile (v3.0 config integration)
- [ ] T028 [US3] Use default values for optional parameters
- [ ] T029 [US3] Return blocked operations in JSON without waiting
- [ ] T030 [US3] Ensure no TTY requirement in headless mode

**Checkpoint**: Full execution without user interaction

---

## Phase 5: User Story 4 - Stdout/Stderr Capture (Priority: P2)

- [ ] T031 [US4] Capture stdout during execution
- [ ] T032 [US4] Capture stderr during execution
- [ ] T033 [US4] Include captured output in logs field
- [ ] T034 [US4] Add --verbose flag for detailed logs
- [ ] T035 [US4] Separate error messages in stderr field

**Checkpoint**: All outputs captured and structured

---

## Phase 6: User Story 5 - Deterministic Execution (Priority: P2)

- [ ] T036 [US5] Add --seed flag for reproducible randomness
- [ ] T037 [US5] Add --no-timestamps flag to disable temporal metadata
- [ ] T038 [US5] Document non-deterministic sources (API calls)
- [ ] T039 [US5] Ensure same inputs produce same outputs (hors API)

**Checkpoint**: Reproducible executions with seed

---

## Phase 7: CLI Integration

- [ ] T040 Create `aetheris run <task-file>` command in cli.py
- [ ] T041 Add --dry-run flag for validation without execution
- [ ] T042 Add --profile flag for security profile selection
- [ ] T043 Add --timeout flag for execution timeout
- [ ] T044 Return appropriate exit codes (0/1/2)

**Checkpoint**: CLI command fully functional

---

## Phase 8: Signal Handling & Edge Cases

- [ ] T045 Implement SIGINT handler for graceful shutdown
- [ ] T046 Implement SIGTERM handler for graceful shutdown
- [ ] T047 Return valid JSON on interrupt (status: interrupted)
- [ ] T048 Handle timeout with partial results (status: timeout)
- [ ] T049 Handle disk full with minimal JSON in memory
- [ ] T050 Handle file not found with JSON error
- [ ] T051 Handle parse errors with detailed JSON error
- [ ] T052 Detect circular dependencies in task files

**Checkpoint**: All edge cases handled gracefully

---

## Phase 9: Testing & Documentation

- [ ] T053 Create tests/test_task_parser.py with unit tests
- [ ] T054 Create tests/test_executor.py with unit tests
- [ ] T055 Create tests/test_output_formatter.py with unit tests
- [ ] T056 Add integration tests for full headless flow
- [ ] T057 Update pyproject.toml version to 3.2
- [ ] T058 Document task file format in docs/headless.md
- [ ] T059 Add example task files in examples/tasks/

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 59 |
| Phase 1 (Setup) | 4 tasks |
| US1 (Task File Input) | 9 tasks |
| US2 (JSON Output) | 10 tasks |
| US3 (Non-Interactive) | 7 tasks |
| US4 (Capture) | 5 tasks |
| US5 (Determinism) | 4 tasks |
| Phase 7 (CLI) | 5 tasks |
| Phase 8 (Edge Cases) | 8 tasks |
| Phase 9 (Testing) | 7 tasks |
| Files Created | ~10 |
