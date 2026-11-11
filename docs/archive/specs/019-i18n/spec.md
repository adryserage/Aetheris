# Feature Specification: Internationalization (i18n)

**Feature Branch**: `019-i18n`
**Created**: 2026-01-10
**Status**: Draft
**Version**: v2.7
**Input**: User description: "Add multi-language support to Aetheris CLI. Support English (en) as default and French (fr) initially. All user-facing messages, prompts, help texts, progress messages, and error messages should be translatable. Use a locale detection mechanism (system locale, env var, CLI flag --lang). Store translations in JSON/YAML files. Provide a clean API for developers to add new languages."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - French User Gets Native Experience (Priority: P1)

A French-speaking user runs Aetheris on their system configured with French locale. All CLI messages, progress indicators, error messages, and help texts appear in French without any manual configuration.

**Why this priority**: Core value proposition - automatic language detection enables seamless localized experience for non-English users.

**Independent Test**: Can be fully tested by setting system locale to `fr_FR` and running `aetheris analysis --help`, verifying all output is in French.

**Acceptance Scenarios**:

1. **Given** a system with `LANG=fr_FR.UTF-8`, **When** user runs `aetheris analysis`, **Then** all progress messages and output appear in French
2. **Given** a system with French locale, **When** user runs `aetheris --help`, **Then** help text displays in French
3. **Given** a system with French locale and an analysis error occurs, **When** the error is displayed, **Then** error message appears in French

---

### User Story 2 - Explicit Language Override via CLI (Priority: P1)

A user wants to run Aetheris in a specific language regardless of their system settings. They use the `--lang` flag to explicitly set the output language.

**Why this priority**: Essential for CI/CD environments where system locale may differ from desired output language, and for users preferring a specific language.

**Independent Test**: Run `aetheris analysis --lang fr` on an English system and verify French output.

**Acceptance Scenarios**:

1. **Given** an English system, **When** user runs `aetheris analysis --lang fr`, **Then** all output appears in French
2. **Given** a French system, **When** user runs `aetheris analysis --lang en`, **Then** all output appears in English
3. **Given** user specifies invalid language code `--lang xyz`, **When** command runs, **Then** system shows error listing available languages and falls back to English

---

### User Story 3 - Environment Variable Configuration (Priority: P2)

A user wants to set their preferred language once via environment variable rather than using `--lang` every time.

**Why this priority**: Convenience feature for users who prefer a consistent language across all Aetheris commands without modifying system locale.

**Independent Test**: Set `AETHERIS_LANG=fr` and run any command, verify French output.

**Acceptance Scenarios**:

1. **Given** `AETHERIS_LANG=fr` is set, **When** user runs `aetheris analysis`, **Then** output appears in French
2. **Given** `AETHERIS_LANG=fr` is set, **When** user runs `aetheris --lang en analysis`, **Then** `--lang` flag takes precedence and output appears in English
3. **Given** `AETHERIS_LANG` contains unsupported value, **When** command runs, **Then** system warns about invalid language and uses fallback

---

### User Story 4 - Developer Adds New Language (Priority: P3)

A developer contributor wants to add support for a new language (e.g., Spanish). They should be able to create a translation file following the existing pattern and have it automatically detected.

**Why this priority**: Enables community contributions and future language expansion without code changes.

**Independent Test**: Create `locales/es.json` with translations, run `aetheris --lang es`, verify Spanish output.

**Acceptance Scenarios**:

1. **Given** a new translation file `locales/es.json` exists with proper structure, **When** user runs `aetheris --lang es`, **Then** Spanish messages are displayed
2. **Given** a new translation file with missing keys, **When** message lookup fails, **Then** system falls back to English for missing keys
3. **Given** developer creates malformed translation file, **When** Aetheris loads, **Then** clear error message indicates which file has issues

---

### User Story 5 - View Available Languages (Priority: P3)

A user wants to know which languages are available in their Aetheris installation.

**Why this priority**: Discovery feature helping users know their options.

**Independent Test**: Run `aetheris --list-languages` and verify list of available languages.

**Acceptance Scenarios**:

1. **Given** default installation, **When** user runs `aetheris --list-languages`, **Then** list shows "en (English) [default]" and "fr (Français)"
2. **Given** custom translation file added, **When** user runs `aetheris --list-languages`, **Then** new language appears in list

---

### Edge Cases

- What happens when a translation file is partially complete (some keys missing)?
  - System falls back to English for missing keys, no crash or error
- What happens when system locale is not recognized (e.g., `LANG=xyz_XY`)?
  - System defaults to English with optional warning
- What happens when translation file contains syntax errors?
  - Clear error message identifying the problematic file, fall back to English
- What happens when Rich markup in translation strings is malformed?
  - Graceful degradation: show raw text without markup
- What happens during long-running analysis when language changes mid-process?
  - Language is determined at startup and remains consistent throughout execution

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST detect user's preferred language from system locale (`LANG`, `LC_ALL`, `LC_MESSAGES` environment variables)
- **FR-002**: System MUST support explicit language selection via `--lang <code>` CLI flag
- **FR-003**: System MUST support language configuration via `AETHERIS_LANG` environment variable
- **FR-004**: System MUST apply language priority: CLI flag > `AETHERIS_LANG` > system locale > default (English)
- **FR-005**: System MUST support English (en) and French (fr) languages at launch
- **FR-006**: System MUST translate all user-facing messages including:
  - CLI help texts and command descriptions
  - Progress messages and spinners
  - Error messages and warnings
  - Success/completion messages
  - Table headers and labels
- **FR-007**: System MUST fall back to English when requested translation key is missing
- **FR-008**: System MUST store translations in human-readable files (JSON format)
- **FR-009**: System MUST provide `--list-languages` flag to display available languages
- **FR-010**: System MUST log a warning when falling back due to missing translation
- **FR-011**: System MUST validate translation file structure on load and report errors clearly
- **FR-012**: System MUST preserve Rich console markup in translated strings

### Key Entities

- **Locale**: Represents a language/region combination (e.g., `en`, `fr`, `fr_CA`), maps to translation file
- **Translation File**: JSON file containing key-value pairs for all translatable strings in a language
- **Message Key**: Unique identifier for each translatable string (e.g., `cli.analysis.start`, `error.file_not_found`)
- **Translator**: Service responsible for loading translations and resolving message keys to localized strings

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of user-facing CLI messages are translatable (no hardcoded strings remain)
- **SC-002**: French translation covers 100% of message keys with native-quality text
- **SC-003**: Adding a new language requires only creating a translation file (zero code changes)
- **SC-004**: Language detection and message lookup adds less than 50ms to CLI startup time
- **SC-005**: All existing CLI commands continue to function identically with i18n enabled
- **SC-006**: Translation file validation catches 100% of structural errors before runtime

## Assumptions

- Translation files will be bundled with the package (not downloaded at runtime)
- Message keys will use dot-notation namespacing (e.g., `cli.analysis.start`)
- Regional variants (e.g., `fr_CA`) will fall back to base language (`fr`) if specific variant unavailable
- AI-generated analysis content (from Gemini/Claude) will NOT be translated - only CLI chrome is translated
- Pluralization will use simple suffix convention:
  - Keys ending in `_one` for singular (e.g., `files.count_one` = "1 file")
  - Keys ending in `_other` for plural (e.g., `files.count_other` = "{count} files")
  - Code selects suffix based on count: `t(f"files.count_{'one' if n == 1 else 'other'}", count=n)`
