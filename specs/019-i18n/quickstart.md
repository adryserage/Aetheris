# Quickstart: Internationalization (i18n)

**Feature**: 019-i18n | **Date**: 2026-01-10

## User Guide

### Using Aetheris in Different Languages

#### Automatic Language Detection

Aetheris automatically detects your system language:

```bash
# On a French system (LANG=fr_FR.UTF-8)
aetheris analysis
# Output appears in French

# On an English system (LANG=en_US.UTF-8)
aetheris analysis
# Output appears in English
```

#### Explicit Language Selection

Override the detected language with `--lang`:

```bash
# Force French output
aetheris analysis --lang fr

# Force English output
aetheris analysis --lang en

# Works with any command
aetheris stats --lang fr
aetheris fix --lang en
```

#### Environment Variable

Set a persistent preference without modifying system locale:

```bash
# Set in shell profile (.bashrc, .zshrc)
export AETHERIS_LANG=fr

# Then use normally
aetheris analysis  # French output
```

#### View Available Languages

```bash
aetheris --list-languages

# Output:
# Available languages:
# - en (English) [default]
# - fr (Français)
```

---

## Developer Guide

### Using Translations in Code

```python
from src.i18n import t

# Basic usage
print(t("cli.analysis.start"))

# With interpolation
print(t("error.file_not_found", path="/some/file.py"))

# With Rich markup (preserved in translation)
console.print(t("success.complete"))
```

### Adding a New Translatable String

1. **Add to English file** (`src/locales/en.json`):
```json
{
  "my.new.message": "Hello, {name}!"
}
```

2. **Add to French file** (`src/locales/fr.json`):
```json
{
  "my.new.message": "Bonjour, {name} !"
}
```

3. **Use in code**:
```python
print(t("my.new.message", name="World"))
```

### Adding a New Language

1. **Create translation file** (`src/locales/es.json`):
```json
{
  "_meta": {
    "language": "es",
    "name": "Español",
    "version": "1.0"
  },
  "cli.analysis.help": "Analizar código fuente",
  "cli.analysis.start": "🔍 Iniciando análisis..."
}
```

2. **Test**:
```bash
aetheris --lang es analysis
```

That's it! No code changes required.

### Key Naming Convention

Use dot-notation with these prefixes:

| Prefix | Usage |
|--------|-------|
| `cli.*` | CLI messages |
| `progress.*` | Progress indicators |
| `error.*` | Error messages |
| `success.*` | Success messages |
| `warning.*` | Warnings |
| `table.*` | Table headers |

Example: `cli.analysis.scanning_files`

### Interpolation

Use `{variable}` syntax:

```json
{
  "progress.analyzing": "Analyzing {current}/{total} files..."
}
```

```python
t("progress.analyzing", current=5, total=10)
# "Analyzing 5/10 files..."
```

### Testing Translations

```python
from src.i18n import set_language, t

def test_french_translation():
    set_language("fr")
    assert t("cli.analysis.start") == "🔍 Démarrage de l'analyse..."

def test_fallback_to_english():
    set_language("fr")
    # Key missing in French, falls back to English
    assert t("some.missing.key") == "English fallback"
```

---

## API Reference

### `t(key: str, **kwargs) -> str`

Get translated string for the current language.

```python
t("error.file_not_found", path="/foo.py")
```

### `set_language(lang: str) -> None`

Set the active language.

```python
set_language("fr")
```

### `get_language() -> str`

Get the current language code.

```python
lang = get_language()  # "fr"
```

### `get_available_languages() -> list[LanguageInfo]`

List all available languages.

```python
for lang in get_available_languages():
    print(f"{lang.code}: {lang.name}")
```

### `detect_language(cli_lang: str | None = None) -> str`

Detect language from CLI flag, env var, or system locale.

```python
lang = detect_language(cli_lang="fr")  # "fr"
lang = detect_language()  # Auto-detect
```
