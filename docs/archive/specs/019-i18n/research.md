# Research: Internationalization (i18n)

**Feature**: 019-i18n | **Date**: 2026-01-10

## Research Summary

This document captures research findings for implementing i18n in Aetheris CLI.

---

## 1. Translation File Format

**Decision**: JSON files with flat key-value structure

**Rationale**:
- JSON is Python stdlib (no dependencies)
- Human-readable and editable
- Easy to validate programmatically
- Widely supported by translation tools

**Alternatives Considered**:
- YAML: Requires `pyyaml` dependency
- gettext (.po): More complex, overkill for CLI
- TOML: Less common for translations

**Format Structure**:
```json
{
  "_meta": {
    "language": "fr",
    "name": "Français",
    "version": "1.0"
  },
  "cli.analysis.help": "Analyser le code source",
  "cli.analysis.start": "🔍 Démarrage de l'analyse...",
  "error.file_not_found": "❌ Fichier non trouvé: {path}"
}
```

---

## 2. Locale Detection Strategy

**Decision**: Priority chain (CLI > env > system > default)

**Rationale**:
- CLI flag gives immediate control
- Env var enables persistent preference without system change
- System locale is intuitive fallback
- English default ensures always-working state

**Detection Order**:
1. `--lang` CLI flag (e.g., `--lang fr`)
2. `AETHERIS_LANG` environment variable
3. System locale (`LANG`, `LC_ALL`, `LC_MESSAGES`)
4. Default: `en`

**System Locale Parsing**:
```python
# LANG=fr_FR.UTF-8 → "fr"
# LANG=en_US → "en"
# LANG=C → "en" (fallback)
locale_str = os.environ.get("LANG", "")
lang_code = locale_str.split("_")[0].split(".")[0] or "en"
```

---

## 3. Translation API Design

**Decision**: Simple `t(key, **kwargs)` function with global translator

**Rationale**:
- Minimal boilerplate for developers
- Familiar pattern from other i18n systems
- Supports string interpolation with `.format()`

**API**:
```python
from src.i18n import t, set_language, get_available_languages

# Basic usage
print(t("cli.analysis.start"))

# With interpolation
print(t("error.file_not_found", path="/some/file.py"))

# Language control
set_language("fr")
print(get_available_languages())  # ["en", "fr"]
```

---

## 4. Fallback Behavior

**Decision**: Three-level fallback chain

**Rationale**:
- Never crash due to missing translation
- Log warnings for missing keys (debugging)
- Key as final fallback enables graceful degradation

**Fallback Chain**:
1. Current language translation
2. English translation (always complete)
3. Key itself (e.g., `"cli.analysis.start"`)

**Warning Logging**:
```python
if key not in translations[lang]:
    logger.warning(f"Missing translation: {key} for lang={lang}")
    return translations["en"].get(key, key)
```

---

## 5. Rich Markup Handling

**Decision**: Preserve Rich markup in translation strings

**Rationale**:
- Aetheris uses Rich for terminal UI
- Translators can adjust emphasis per language
- No additional processing needed

**Example**:
```json
{
  "cli.analysis.complete": "[green]✅ Analyse terminée![/green]",
  "error.critical": "[bold red]ERREUR CRITIQUE:[/bold red] {message}"
}
```

---

## 6. Message Key Naming Convention

**Decision**: Dot-notation namespacing

**Rationale**:
- Hierarchical organization
- Easy to locate in codebase
- Avoids key collisions

**Convention**:
```
{module}.{context}.{action}

Examples:
- cli.analysis.help
- cli.analysis.start
- cli.analysis.complete
- error.file_not_found
- error.api.timeout
- progress.scanning_files
- success.report_saved
- table.header.severity
```

---

## 7. Performance Considerations

**Decision**: Lazy loading with in-memory cache

**Rationale**:
- No startup penalty if i18n not used
- Single load per language per process
- O(1) lookups from dict

**Implementation**:
```python
class Translator:
    _translations: dict[str, dict[str, str]] = {}
    _current_lang: str = "en"

    def load(self, lang: str) -> None:
        if lang not in self._translations:
            path = LOCALES_DIR / f"{lang}.json"
            self._translations[lang] = json.loads(path.read_text())
```

---

## 8. Testing Strategy

**Decision**: Unit tests + integration tests with locale mocking

**Rationale**:
- Unit tests verify translator logic
- Integration tests verify CLI output
- Mocking avoids system locale dependencies

**Test Categories**:
1. **Unit**: `test_i18n.py`
   - Translator initialization
   - Key lookup with fallback
   - Interpolation
   - Language switching

2. **Integration**: `test_cli_i18n.py`
   - `--lang` flag works
   - `AETHERIS_LANG` env var works
   - `--list-languages` output

---

## 9. Package Data Inclusion

**Decision**: Include `src/locales/*.json` in package

**Rationale**:
- Translations must be bundled
- Works with pip install

**pyproject.toml Addition**:
```toml
[tool.setuptools.package-data]
"*" = ["locales/*.json"]
```

---

## 10. Existing Hardcoded Strings Audit

**Findings**: cli.py contains mixed English/French strings

**Current State**:
- Some French strings already present (fix command)
- Most strings are English
- Rich markup used extensively
- ~100 user-facing strings estimated

**Migration Strategy**:
1. Extract all strings to `en.json`
2. Replace with `t()` calls
3. Create `fr.json` from extracted + existing French
4. Review and polish French translations
