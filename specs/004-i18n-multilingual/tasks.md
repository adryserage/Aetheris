# Tasks: Internationalization & Multilingual Support

**Input**: Design documents from `/specs/004-i18n-multilingual/`
**Target Version**: v2.8
**Estimated LOC**: ~250-350

---

## Phase 1: Setup

- [ ] T001 Create src/i18n/ directory structure
- [ ] T002 [P] Create messages_fr.yaml with all French messages in src/i18n/
- [ ] T003 [P] Create messages_en.yaml with English translations in src/i18n/
- [ ] T004 Create LanguageConfig dataclass in src/i18n/language.py

**Checkpoint**: Message files and base types ready

---

## Phase 2: User Story 1 - Language Detection (Priority: P1)

- [ ] T005 [US1] Implement detect_language_from_env() in src/i18n/language.py
- [ ] T006 [US1] Set French as default language in src/i18n/language.py
- [ ] T007 [US1] Create MessageDictionary class with get() method in src/i18n/loader.py
- [ ] T008 [US1] Implement load_messages() to read YAML files in src/i18n/loader.py
- [ ] T009 [US1] Add fallback to key name if message not found in src/i18n/loader.py

**Checkpoint**: Language auto-detection working

---

## Phase 3: User Story 2 - CLI Language Override (Priority: P1)

- [ ] T010 [US2] Add --lang/-l parameter to CLI in src/cli.py
- [ ] T011 [US2] Validate language parameter (fr, en only) in src/cli.py
- [ ] T012 [US2] Display supported languages error for invalid input in src/cli.py
- [ ] T013 [US2] Pass language config to all commands in src/cli.py

**Checkpoint**: CLI language override working

---

## Phase 4: User Story 3 - AI Response Language (Priority: P1)

- [ ] T014 [US3] Create AI_LANGUAGE_INSTRUCTION dictionary in src/i18n/language.py
- [ ] T015 [US3] Implement get_ai_language_instruction() in src/i18n/language.py
- [ ] T016 [US3] Inject language instruction in AIProvider base class in src/core/ai_providers.py
- [ ] T017 [US3] Test AI responses in both languages in src/core/ai_providers.py

**Checkpoint**: AI responds in configured language

---

## Phase 5: User Story 4 - Static Text Externalization (Priority: P2)

- [ ] T018 [US4] Extract all hardcoded strings from src/cli.py to messages
- [ ] T019 [US4] Extract all hardcoded strings from src/core/ to messages
- [ ] T020 [US4] Extract all hardcoded strings from src/agents/ to messages
- [ ] T021 [US4] Replace hardcoded strings with MessageDictionary.get() calls
- [ ] T022 [US4] Verify no hardcoded user-facing strings remain

**Checkpoint**: All static text externalized

---

## Phase 6: Polish & Edge Cases

- [ ] T023 Handle corrupted message files gracefully in src/i18n/loader.py
- [ ] T024 Handle partial translations (fallback to French) in src/i18n/loader.py
- [ ] T025 Implement AI response language validation (retry with stronger instruction if wrong language) in src/core/ai_providers.py
- [ ] T026 Define TECHNICAL_TERMS list (file names, commands, variables) that must not be translated in src/i18n/language.py
- [ ] T027 Add post-processing to preserve technical terms in AI responses in src/core/ai_providers.py
- [ ] T028 [P] Add language info to --help output in src/cli.py
- [ ] T029 Update pyproject.toml version to 2.8

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 29 |
| Phase 1 (Setup) | 4 tasks |
| US1 (Language Detection) | 5 tasks |
| US2 (CLI Override) | 4 tasks |
| US3 (AI Response) | 4 tasks |
| US4 (Externalization) | 5 tasks |
| Phase 6 (Polish) | 7 tasks |
| Files Created | 5 |
| Files Modified | 3 |
