# Implementation Plan: Internationalization (i18n)

**Branch**: `019-i18n` | **Date**: 2026-01-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/019-i18n/spec.md`

## Summary

Add multi-language support to Aetheris CLI with English (default) and French initially. Implement a lightweight translation system using JSON files with locale detection (CLI flag > env var > system locale > default). All user-facing messages will be translatable via a simple `t("key")` function that loads translations lazily and falls back to English for missing keys.

## Technical Context

**Language/Version**: Python 3.9+ (compatible with existing codebase)
**Primary Dependencies**: None new required (use stdlib `json`, `locale`, `os`)
**Storage**: JSON files in `src/locales/` directory (bundled with package)
**Testing**: pytest with locale mocking
**Target Platform**: Linux, macOS, Windows (cross-platform CLI)
**Project Type**: Single project (existing CLI structure)
**Performance Goals**: <50ms overhead for i18n initialization and lookups
**Constraints**: No external i18n libraries (keep lightweight), fallback to English always works
**Scale/Scope**: ~100-200 translatable message keys initially

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Note**: Project constitution is not configured (template only). Proceeding with standard best practices:
- ✅ No new external dependencies required
- ✅ Backward compatible (existing behavior unchanged)
- ✅ Testable (unit tests for translator, integration tests for CLI)
- ✅ Simple implementation (single module, JSON files)

## Project Structure

### Documentation (this feature)

```text
specs/019-i18n/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (via /speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── i18n/                    # NEW: i18n module
│   ├── __init__.py          # Public API: t(), get_translator(), set_language()
│   ├── translator.py        # Translator class with lazy loading
│   └── locale_detector.py   # Locale detection logic
├── locales/                 # NEW: Translation files
│   ├── en.json              # English (default/fallback)
│   └── fr.json              # French translation
├── cli.py                   # MODIFY: Add --lang flag, use t() for messages
├── agents/                  # MODIFY: Use t() for user-facing messages
└── core/                    # MODIFY: Use t() for progress/error messages

tests/
├── unit/
│   └── test_i18n.py         # NEW: Unit tests for translator
└── integration/
    └── test_cli_i18n.py     # NEW: CLI integration tests
```

**Structure Decision**: Single project structure maintained. New `src/i18n/` module for translation logic, `src/locales/` for translation files. Minimal changes to existing modules (wrap strings with `t()`).

## Complexity Tracking

No constitution violations. Implementation is straightforward:
- Single new module (`src/i18n/`)
- No new dependencies
- Minimal changes to existing code (string wrapping)

## Integration Points

### CLI Integration (`src/cli.py`)

1. Add global `--lang` option to Typer app
2. Initialize translator early in CLI startup
3. Replace hardcoded strings with `t("key")` calls

### Message Categories

| Category | Example Keys | Location |
|----------|--------------|----------|
| CLI Help | `cli.help.analysis`, `cli.help.fix` | `src/cli.py` |
| Progress | `progress.analyzing`, `progress.complete` | `src/core/analyzer.py` |
| Errors | `error.file_not_found`, `error.api_failed` | Throughout |
| Success | `success.report_generated` | `src/cli.py` |
| Tables | `table.header.file`, `table.header.issues` | Reports |

## Key Design Decisions

1. **Lazy Loading**: Translation files loaded on first `t()` call, not at import
2. **Singleton Pattern**: Single global translator instance per process
3. **Fallback Chain**: Missing key → English value → Key itself (never crash)
4. **No Pluralization Library**: Use simple `_plural` suffix convention for now
5. **Rich Markup Preserved**: Translation strings can contain Rich markup
