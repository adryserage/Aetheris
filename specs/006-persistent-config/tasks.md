# Tasks: Persistent Configuration & Local Config File

**Input**: Design documents from `/specs/006-persistent-config/`
**Target Version**: v3.0
**Estimated LOC**: ~500-600

---

## Phase 1: Setup

- [ ] T001 Create ConfigSchema dataclass with all options in src/core/config_schema.py
- [ ] T002 [P] Create config/default.json with default values
- [ ] T003 Create ConfigFile class for loading/saving in src/core/config_file.py
- [ ] T004 Create ConfigHierarchy class for priority resolution in src/core/config_file.py

**Checkpoint**: Base config infrastructure ready

---

## Phase 2: User Story 1 - Configuration Cascade (Priority: P1)

- [ ] T005 [US1] Implement load_local_config() in src/core/config_file.py
- [ ] T006 [US1] Implement load_global_config() in src/core/config_file.py
- [ ] T007 [US1] Implement merge_configs() with priority in src/core/config_file.py
- [ ] T008 [US1] Integrate ConfigHierarchy into CLI argument parsing in src/cli.py
- [ ] T009 [US1] Ensure secrets read from .env only in src/core/config_file.py

**Checkpoint**: Configuration cascade working

---

## Phase 3: User Story 2 - Initialize Config (Priority: P1)

- [ ] T010 [US2] Add `aetheris init` command in src/cli.py
- [ ] T011 [US2] Generate config.json from default template in src/cli.py
- [ ] T012 [US2] Add confirmation prompt if config.json exists in src/cli.py
- [ ] T013 [US2] Add --force flag to skip confirmation in src/cli.py

**Checkpoint**: Init command working

---

## Phase 4: User Story 3 - Complex Types (Priority: P2)

- [ ] T014 [US3] Support array types (exclude_patterns) in ConfigSchema
- [ ] T015 [US3] Support nested objects (ai, analysis, output sections) in ConfigSchema
- [ ] T016 [US3] Implement deep merge for nested configs in src/core/config_file.py

**Checkpoint**: Complex config types working

---

## Phase 5: User Story 4 - Secrets Separation (Priority: P2)

- [ ] T017 [US4] Define SECRET_KEYS list in src/core/config_file.py
- [ ] T018 [US4] Detect secrets in config.json and warn in src/core/config_file.py
- [ ] T019 [US4] Ensure API keys only from .env in src/core/config_file.py

**Checkpoint**: Secrets properly separated

---

## Phase 6: User Story 5 - Interactive Settings (Priority: P2)

- [ ] T020 [US5] Create SettingsUI class with Rich/Textual in src/core/settings_ui.py
- [ ] T021 [US5] Implement tabbed category navigation in src/core/settings_ui.py
- [ ] T022 [US5] Implement option editing with validation in src/core/settings_ui.py
- [ ] T023 [US5] Add `aetheris settings` command in src/cli.py
- [ ] T024 [US5] Add --global flag for global config editing in src/cli.py
- [ ] T025 [US5] Display current value and source for each option in src/core/settings_ui.py
- [ ] T026 [US5] Add option descriptions/help text in src/core/settings_ui.py

**Checkpoint**: Interactive settings UI working

---

## Phase 7: User Story 6 - Version Control (Priority: P3)

- [ ] T027 [US6] Ensure config.json format is git-friendly (sorted keys)
- [ ] T028 [US6] Add .gitignore recommendation for secrets

**Checkpoint**: Config versionable

---

## Phase 8: Polish

- [ ] T029 Handle malformed JSON with clear error in src/core/config_file.py
- [ ] T030 Warn on unknown config keys (typos) in src/core/config_file.py
- [ ] T031 Handle non-interactive terminals (skip settings UI) in src/core/settings_ui.py
- [ ] T032 Update pyproject.toml version to 3.0

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 32 |
| Files Created | 4 |
| Files Modified | 2 |
