# Tasks: Nettoyage des Artefacts & Sécurisation des Paquets

**Input**: Design documents from `/specs/012-artifact-cleanup/`
**Prerequisites**: plan.md ✓, spec.md ✓
**Target Version**: v2.6.2
**Estimated LOC**: ~500-600 across 8 files
**Total Tasks**: 53

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US5)
- All paths relative to repository root

---

## Summary

| Phase | Tasks | Count | Dependencies |
|-------|-------|-------|--------------|
| Phase 1: Setup | T001-T005 | 5 | None |
| Phase 2: Exclusion (US1) | T006-T012 | 7 | Phase 1 |
| Phase 3: Cleanup (US2) | T013-T020 | 8 | Phase 1 |
| Phase 4: Secret Scan (US3) | T021-T030 | 10 | Phase 1 |
| Phase 5: Minification (US4) | T031-T034 | 4 | Phase 3 |
| Phase 6: Validation (US5) | T035-T040 | 6 | Phase 2, 4 |
| Phase 7: Polish & Edge Cases | T041-T048 | 8 | All previous |
| Phase 7: Tests & Docs | T049-T053 | 5 | All previous |
| **Total** | **T001-T053** | **53 tasks** | |

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create base types and file structure used by all components

- [X] T001 Create `src/models/cleanup_models.py` with ExclusionConfig dataclass
- [X] T002 [P] Create `src/config/exclusion_patterns.py` with DEFAULT_EXCLUSIONS dict
- [X] T003 [P] Create `src/config/secret_patterns.py` with SECRET_PATTERNS list
- [X] T004 Add cleanup and validate-package command stubs to `src/cli.py`
- [X] T005 [P] Create test fixtures directory `tests/fixtures/sample_project/` with sample files

**Checkpoint**: File structure created, CLI commands registered (no-op), fixtures ready

---

## Phase 2: Automatic File Exclusion (US1) 🎯 MVP

**Goal**: Implement default exclusion patterns for package builds

**Independent Test**: Build package and verify excluded files are not present

### Implementation for User Story 1

- [X] T006 [US1] Define SECURITY_EXCLUSIONS patterns (.env, .git/, etc.) in `src/config/exclusion_patterns.py`
- [X] T007 [P] [US1] Define OS_ARTIFACT_EXCLUSIONS patterns (.DS_Store, Thumbs.db, etc.) in `src/config/exclusion_patterns.py`
- [X] T008 [P] [US1] Define DEV_TOOLING_EXCLUSIONS patterns (tsconfig.tsbuildinfo, .eslintrc, etc.) in `src/config/exclusion_patterns.py`
- [X] T009 [P] [US1] Define TEST_EXCLUSIONS patterns (tests/, __tests__/, *_test.py, etc.) in `src/config/exclusion_patterns.py`
- [X] T010 [P] [US1] Define DEEP_CLEAN_EXCLUSIONS patterns (dist/, build/, *.egg-info/) in `src/config/exclusion_patterns.py`
- [X] T011 [US1] Implement `matches_exclusion_pattern(filepath, patterns)` function in `src/services/cleanup_service.py`
- [X] T012 [US1] Implement `get_excluded_files(directory, patterns)` returning list of matched files in `src/services/cleanup_service.py`

**Checkpoint**: Exclusion patterns defined, pattern matching works

---

## Phase 3: Cleanup Command (US2)

**Goal**: Implement `aetheris cleanup` command with dry-run and deep clean

**Independent Test**: Run `aetheris cleanup --dry-run` and verify file list, run without flag and verify deletion

### Implementation for User Story 2

- [X] T013 [US2] Create `CleanupService` class with `__init__(config: ExclusionConfig)` in `src/services/cleanup_service.py`
- [X] T014 [US2] Implement `get_files_to_clean(directory, deep=False)` method in CleanupService
- [X] T015 [US2] Implement `calculate_size(files)` returning total size in bytes in CleanupService
- [X] T016 [US2] Implement `delete_files(files)` with error handling in CleanupService
- [X] T017 [US2] Implement `cleanup_dry_run()` returning formatted preview in CleanupService
- [X] T018 [US2] Wire CLI `aetheris cleanup` command to CleanupService in `src/cli.py`
- [X] T019 [US2] Add `--dry-run` flag to cleanup command in `src/cli.py`
- [X] T020 [US2] Add `--deep` flag to cleanup command in `src/cli.py`

**Checkpoint**: `aetheris cleanup` works with --dry-run and --deep flags

---

## Phase 4: Secret Scanner (US3) 🔒 Critical

**Goal**: Implement secret detection engine to prevent credential leaks

**Independent Test**: Create file with `API_KEY=secret123` and verify scanner detects it

### Implementation for User Story 3

- [X] T021 [US3] Create `SecretPattern` dataclass (name, regex, description, confidence) in `src/models/cleanup_models.py`
- [X] T022 [US3] Create `SecretMatch` dataclass (file, line, pattern_name, masked_value) in `src/models/cleanup_models.py`
- [X] T023 [P] [US3] Define HIGH_CONFIDENCE_PATTERNS (AWS keys, generic API keys, passwords) in `src/config/secret_patterns.py`
- [X] T024 [P] [US3] Define MEDIUM_CONFIDENCE_PATTERNS (JWT, private keys, GitHub tokens) in `src/config/secret_patterns.py`
- [X] T025 [P] [US3] Define PROVIDER_PATTERNS (GCP, Stripe, SendGrid, Twilio) in `src/config/secret_patterns.py`
- [X] T026 [US3] Create `SecretScanner` class with `__init__(patterns, ignore_file)` in `src/services/secret_scanner.py`
- [X] T027 [US3] Implement `load_secrets_ignore(filepath)` parsing .secretsignore format in SecretScanner
- [X] T028 [US3] Implement `scan_file(filepath)` returning list of SecretMatch in SecretScanner
- [X] T029 [US3] Implement `scan_directory(directory)` with parallel file scanning in SecretScanner
- [X] T030 [US3] Implement `mask_secret(value)` showing first 4 + last 2 chars only in SecretScanner

**Checkpoint**: Secret scanner detects all pattern types, respects .secretsignore

---

## Phase 5: Optional Minification (US4)

**Goal**: Implement optional Python minification (comments, docstrings removal)

**Independent Test**: Run with `--minify` and verify comments removed, size reduced

### Implementation for User Story 4

- [X] T031 [US4] Create `Minifier` class with `__init__(strip_docstrings=False)` in `src/services/minifier.py`
- [X] T032 [US4] Implement `remove_comments(source)` using tokenize module in Minifier
- [X] T033 [US4] Implement `remove_docstrings(source, keep_public=True)` using ast module in Minifier
- [X] T034 [US4] Add `--minify` and `--strip-docstrings` flags to cleanup command in `src/cli.py`

**Checkpoint**: Minification works, code remains functional

---

## Phase 6: Package Validation (US5)

**Goal**: Implement `aetheris validate-package` command for pre-publish checks

**Independent Test**: Run `aetheris validate-package` on package with secrets, verify blocked

### Implementation for User Story 5

- [X] T035 [US5] Create `ValidationReport` dataclass (size_mb, excluded_found, secrets_found, is_valid) in `src/models/cleanup_models.py`
- [X] T036 [US5] Create `PackageValidator` class with `__init__(config)` in `src/services/package_validator.py`
- [X] T037 [US5] Implement `check_exclusions(directory)` returning list of files that should be excluded in PackageValidator
- [X] T038 [US5] Implement `check_size(directory, max_mb)` returning size and status in PackageValidator
- [X] T039 [US5] Implement `validate(directory)` combining all checks into ValidationReport in PackageValidator
- [X] T040 [US5] Wire CLI `aetheris validate-package` command with `--fix` flag in `src/cli.py`

**Checkpoint**: `aetheris validate-package` catches all security issues

---

## Phase 7: Polish & Edge Cases

**Goal**: Handle edge cases, improve UX, add documentation

### Edge Case Handling

- [X] T041 [Edge] Handle `.env.example` inclusion (whitelist specific patterns) in exclusion_patterns.py
- [X] T042 [Edge] Handle symlinks in cleanup (skip or follow based on config) in CleanupService
- [X] T043 [Edge] Handle permission errors gracefully (log warning, continue) in CleanupService
- [X] T044 [Edge] Add `--patterns` CLI option for custom exclusion patterns in cleanup command
- [X] T045 [Edge] Add warning when .secretsignore excludes test fixtures secrets (potential false negatives)
- [X] T046 [Edge] Add dry-run for minification to preview changes before applying
- [X] T047 [Edge] Handle contradictory patterns (log warning, apply most restrictive)
- [X] T048 [Edge] Add pre-build hook integration option (optional) per FR-014

### Documentation & Tests

- [X] T049 Create unit tests for all services in `tests/unit/test_cleanup_service.py`
- [X] T050 [P] Create unit tests for secret scanner in `tests/unit/test_secret_scanner.py`
- [X] T051 [P] Create unit tests for package validator in `tests/unit/test_package_validator.py`
- [X] T052 Create integration test for full cleanup flow in `tests/integration/test_cleanup_flow.py`
- [X] T053 Add `.secretsignore.example` template file in repository root

**Checkpoint**: All edge cases handled, tests pass, documentation complete

---

## Verification Checklist

Before marking feature complete:

- [X] All unit tests pass (`pytest tests/unit/test_cleanup*.py tests/unit/test_secret*.py tests/unit/test_package*.py`)
- [X] Integration tests pass (`pytest tests/integration/test_cleanup_flow.py`)
- [X] `aetheris cleanup --dry-run` shows correct files
- [X] `aetheris cleanup --deep` removes build artifacts
- [X] `aetheris validate-package` detects test secrets
- [X] `.secretsignore` properly excludes false positives
- [X] Package size reduced after cleanup (measure before/after)
- [X] No secrets in final package (`aetheris validate-package` passes)
- [X] CLI help text is clear and complete (`aetheris cleanup --help`)

---

## Task Dependencies Graph

```
Phase 1 (Setup)
    │
    ├──────────────────┬──────────────────┐
    ▼                  ▼                  ▼
Phase 2 (Exclusion)  Phase 3 (Cleanup)  Phase 4 (Scanner)
    │                  │                  │
    │                  ▼                  │
    │              Phase 5 (Minify)       │
    │                  │                  │
    └──────────────────┼──────────────────┘
                       ▼
                Phase 6 (Validation)
                       │
                       ▼
                Phase 7 (Polish)
```
