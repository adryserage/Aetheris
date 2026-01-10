# Data Model: Internationalization (i18n)

**Feature**: 019-i18n | **Date**: 2026-01-10

## Entities

### 1. TranslationFile

Represents a language-specific translation file.

| Field | Type | Description |
|-------|------|-------------|
| `_meta.language` | `str` | ISO 639-1 language code (e.g., "en", "fr") |
| `_meta.name` | `str` | Human-readable language name (e.g., "English", "Français") |
| `_meta.version` | `str` | Translation file version |
| `{key}` | `str` | Translation value for message key |

**File Location**: `src/locales/{lang}.json`

**Example**:
```json
{
  "_meta": {
    "language": "fr",
    "name": "Français",
    "version": "1.0"
  },
  "cli.analysis.help": "Analyser le code source pour la qualité et la sécurité",
  "cli.analysis.start": "🔍 Démarrage de l'analyse...",
  "error.file_not_found": "❌ Fichier non trouvé: {path}"
}
```

---

### 2. Translator

Singleton service managing translations.

| Attribute | Type | Description |
|-----------|------|-------------|
| `_translations` | `dict[str, dict[str, str]]` | Cached translations per language |
| `_current_lang` | `str` | Active language code |
| `_fallback_lang` | `str` | Fallback language (always "en") |

**Methods**:

| Method | Signature | Description |
|--------|-----------|-------------|
| `get` | `(key: str, **kwargs) -> str` | Get translated string with interpolation |
| `set_language` | `(lang: str) -> None` | Set active language |
| `get_language` | `() -> str` | Get current language code |
| `get_available_languages` | `() -> list[LanguageInfo]` | List available languages |
| `load` | `(lang: str) -> None` | Load translation file (lazy) |

---

### 3. LanguageInfo

Information about an available language.

| Field | Type | Description |
|-------|------|-------------|
| `code` | `str` | ISO 639-1 code (e.g., "fr") |
| `name` | `str` | Native name (e.g., "Français") |
| `is_default` | `bool` | Whether this is the default language |

---

### 4. LocaleDetector

Detects user's preferred language.

| Method | Signature | Description |
|--------|-----------|-------------|
| `detect` | `(cli_lang: str | None) -> str` | Detect language from all sources |
| `from_system` | `() -> str | None` | Parse system locale |
| `from_env` | `() -> str | None` | Read AETHERIS_LANG |

**Detection Priority**:
1. CLI flag (`--lang`)
2. Environment variable (`AETHERIS_LANG`)
3. System locale (`LANG`, `LC_ALL`, `LC_MESSAGES`)
4. Default (`en`)

---

## Relationships

```
┌─────────────────┐
│  LocaleDetector │
│                 │
│  detect() ──────┼──► Returns language code
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌─────────────────┐
│   Translator    │      │ TranslationFile │
│                 │      │   (en.json)     │
│  set_language() │◄─────│   (fr.json)     │
│  get()          │      │   (*.json)      │
└────────┬────────┘      └─────────────────┘
         │
         ▼
┌─────────────────┐
│  t() function   │  ◄── Public API
│                 │
│  Usage:         │
│  t("key", ...)  │
└─────────────────┘
```

---

## Message Key Schema

Keys follow dot-notation namespacing:

```
{module}.{context}.{identifier}
```

### Namespace Registry

| Prefix | Usage | Example |
|--------|-------|---------|
| `cli.*` | CLI command messages | `cli.analysis.help` |
| `progress.*` | Progress indicators | `progress.scanning` |
| `error.*` | Error messages | `error.file_not_found` |
| `success.*` | Success messages | `success.complete` |
| `warning.*` | Warning messages | `warning.deprecated` |
| `table.*` | Table headers/labels | `table.header.file` |
| `prompt.*` | User prompts | `prompt.confirm` |

### Interpolation Variables

Variables use `{name}` syntax:

| Key | Variables | Example Output |
|-----|-----------|----------------|
| `error.file_not_found` | `{path}` | "File not found: /foo.py" |
| `progress.analyzing` | `{count}`, `{total}` | "Analyzing 3/10 files" |
| `success.saved` | `{path}` | "Report saved to docs/report.md" |

---

## Validation Rules

### Translation File Validation

| Rule | Validation |
|------|------------|
| Valid JSON | File parses without error |
| Has `_meta` | `_meta.language` and `_meta.name` required |
| No empty values | All values are non-empty strings |
| Interpolation balanced | All `{var}` have matching `}` |

### Runtime Validation

| Scenario | Behavior |
|----------|----------|
| Missing language file | Warning logged, fallback to English |
| Missing key | Warning logged, fallback to English or key |
| Invalid interpolation | Return unformatted string |
| Malformed Rich markup | Pass through (Rich handles gracefully) |
