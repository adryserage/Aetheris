# Tasks: Internationalization (i18n)

**Input**: Design documents from `/specs/019-i18n/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Not explicitly requested - tests included for core i18n module only.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Summary

| Phase | Description | Tasks |
|-------|-------------|-------|
| Phase 1 | Setup | 3 |
| Phase 2 | Foundational (i18n Core) | 6 |
| Phase 3 | User Story 1 & 2 - Language Detection & CLI (P1) | 5 |
| Phase 4 | User Story 3 - Environment Variable (P2) | 2 |
| Phase 5 | User Story 4 & 5 - Developer API (P3) | 3 |
| Phase 6 | Polish & Cross-Cutting | 4 |
| **Total** | | **23** |

---

## Phase 1: Setup

**Purpose**: Create i18n module structure and translation file templates

- [ ] T001 Create i18n module directory structure: `src/i18n/__init__.py`, `src/i18n/translator.py`, `src/i18n/locale_detector.py`
- [ ] T002 Create locales directory: `src/locales/`
- [ ] T003 [P] Add `src/locales/*.json` to package data in `pyproject.toml`

---

## Phase 2: Foundational (i18n Core Module)

**Purpose**: Core translation infrastructure that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Implement `Translator` class with lazy loading in `src/i18n/translator.py`:
  - `_translations: dict[str, dict[str, str]]` cache
  - `_current_lang: str` state
  - `load(lang: str)` method
  - `get(key: str, **kwargs) -> str` with fallback chain
- [ ] T005 [P] Implement `LocaleDetector` class in `src/i18n/locale_detector.py`:
  - `from_system() -> str | None` parse LANG/LC_ALL/LC_MESSAGES
  - `from_env() -> str | None` read AETHERIS_LANG
  - `detect(cli_lang: str | None) -> str` priority chain
- [ ] T006 [P] Create public API in `src/i18n/__init__.py`:
  - `t(key: str, **kwargs) -> str` function
  - `set_language(lang: str) -> None`
  - `get_language() -> str`
  - `get_available_languages() -> list[LanguageInfo]`
  - `detect_language(cli_lang: str | None) -> str`
- [ ] T007 [P] Create English translation file `src/locales/en.json` with `_meta` and all message keys
- [ ] T008 [P] Create French translation file `src/locales/fr.json` with `_meta` and all message keys
- [ ] T009 Add unit tests for Translator and LocaleDetector in `tests/unit/test_i18n.py`

**Checkpoint**: i18n core module ready - CLI integration can now begin

---

## Phase 3: User Story 1 & 2 - Automatic Detection & CLI Override (P1) 🎯 MVP

**Goal**: French users get native experience automatically; any user can override with `--lang` flag

**Independent Test**:
- Set `LANG=fr_FR.UTF-8`, run `aetheris --help`, verify French output
- Run `aetheris --lang fr --help` on English system, verify French output

### Implementation

- [ ] T010 [US1] [US2] Add `--lang` global option to Typer app in `src/cli.py`:
  - Add callback to initialize translator with detected/specified language
  - Integrate `detect_language()` at CLI startup
- [ ] T011 [US1] [US2] Extract all hardcoded strings from `src/cli.py` to translation keys:
  - Replace with `t("key")` calls
  - Add keys to `en.json` and `fr.json`
- [ ] T012 [P] [US1] [US2] Extract strings from `src/core/analyzer.py` (progress messages):
  - Replace with `t("key")` calls
  - Add keys to translation files
- [ ] T013 [P] [US1] [US2] Extract strings from `src/core/change_detector.py`:
  - Replace with `t("key")` calls
  - Add keys to translation files
- [ ] T014 [US1] [US2] Handle invalid `--lang` value: show available languages, fallback to English

**Checkpoint**: User Stories 1 & 2 complete - automatic detection and CLI override work

---

## Phase 4: User Story 3 - Environment Variable Configuration (P2)

**Goal**: Users can set `AETHERIS_LANG` for persistent language preference

**Independent Test**: Set `AETHERIS_LANG=fr`, run `aetheris analysis --help`, verify French output

### Implementation

- [ ] T015 [US3] Ensure `LocaleDetector.from_env()` reads `AETHERIS_LANG` correctly in `src/i18n/locale_detector.py`
- [ ] T016 [US3] Add warning message when `AETHERIS_LANG` contains unsupported value in `src/i18n/translator.py`

**Checkpoint**: User Story 3 complete - environment variable works with correct priority

---

## Phase 5: User Story 4 & 5 - Developer API & Language Listing (P3)

**Goal**: Developers can add new languages; users can discover available languages

**Independent Test**:
- Create `src/locales/es.json`, run `aetheris --lang es`, verify Spanish output
- Run `aetheris --list-languages`, verify list shows en, fr

### Implementation

- [ ] T017 [US4] [US5] Implement `get_available_languages()` to scan `src/locales/` directory in `src/i18n/translator.py`
- [ ] T018 [US5] Add `--list-languages` flag to CLI in `src/cli.py`:
  - Display table with code, name, default marker
- [ ] T019 [US4] Add translation file validation on load in `src/i18n/translator.py`:
  - Check `_meta` section exists
  - Validate JSON structure
  - Log clear error for malformed files

**Checkpoint**: All user stories complete - full i18n functionality available

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, cleanup, and validation

- [ ] T020 [P] Update README.md with i18n usage section (--lang flag, AETHERIS_LANG)
- [ ] T021 [P] Add i18n section to CHANGELOG.md for v2.7
- [ ] T022 Run lint and typecheck: `python -m black src/ --check` and `python -m mypy src/`
- [ ] T023 Validate quickstart.md scenarios work as documented
- [ ] T024 [P] [FUTURE] Document agent string extraction plan for v2.8 iteration

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 - BLOCKS all user stories
- **Phase 3 (US1 & US2)**: Depends on Phase 2
- **Phase 4 (US3)**: Depends on Phase 2 (can run in parallel with Phase 3)
- **Phase 5 (US4 & US5)**: Depends on Phase 2 (can run in parallel with Phases 3-4)
- **Phase 6 (Polish)**: Depends on all user story phases

### User Story Dependencies

| Story | Depends On | Can Parallel With |
|-------|------------|-------------------|
| US1 & US2 | Phase 2 (Foundational) | US3, US4, US5 |
| US3 | Phase 2 | US1, US2, US4, US5 |
| US4 & US5 | Phase 2 | US1, US2, US3 |

### Within Each Phase

- Translation files (T007, T008) can be written in parallel
- String extraction tasks (T011-T013) can run in parallel (different files)
- Polish tasks (T020, T021) can run in parallel

---

## Parallel Execution Examples

### Phase 2 (Foundational):
```bash
# These can run in parallel (different files):
T005: LocaleDetector in src/i18n/locale_detector.py
T006: Public API in src/i18n/__init__.py
T007: English translations in src/locales/en.json
T008: French translations in src/locales/fr.json
```

### Phase 3 (US1 & US2):
```bash
# These can run in parallel (different files):
T012: Extract strings from src/core/analyzer.py
T013: Extract strings from src/core/change_detector.py
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T009)
3. Complete Phase 3: US1 & US2 (T010-T014)
4. **STOP and VALIDATE**: Test `--lang fr` and automatic locale detection
5. Deploy v2.7-beta if ready

### Full Implementation

1. Complete Phases 1-3 → MVP ready
2. Add Phase 4: US3 → Environment variable works
3. Add Phase 5: US4 & US5 → Developer API and --list-languages
4. Complete Phase 6: Polish → Documentation updated
5. Release v2.7

---

## Notes

- All translation keys use dot-notation: `cli.analysis.start`, `error.file_not_found`
- Rich markup preserved in translation strings
- Fallback chain: current language → English → key itself
- No external i18n dependencies (stdlib only)
- Message extraction is incremental - start with cli.py, expand to other modules
