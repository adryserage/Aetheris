# Implementation Plan: Internationalization & Multilingual Support

**Branch**: `004-i18n-multilingual` | **Date**: 2025-01-07 | **Spec**: [spec.md](./spec.md)
**Target Version**: v2.8

## Summary

Add French (FR) and English (EN) language support. Auto-detect language from system locale, allow CLI override, and ensure AI responses match the selected language.

## Technical Context

**Language/Version**: Python 3.9+
**Primary Dependencies**: locale (detection), YAML/JSON (message dictionaries)
**Storage**: Message files in `src/i18n/` directory
**Constraints**: Prompts remain in French (single source), AI instruction injected for other languages

## Project Structure

```text
src/i18n/                    # NEW: Internationalization module
├── __init__.py
├── messages_fr.yaml         # French messages (default)
├── messages_en.yaml         # English messages
├── language.py              # LanguageConfig, detection logic
└── loader.py                # MessageDictionary loader

src/cli.py                   # MODIFY: Add --lang/-l parameter
src/core/ai_providers.py     # MODIFY: Inject language instruction to AI
```

## Data Model

### LanguageConfig
```python
@dataclass
class LanguageConfig:
    code: str  # "fr" or "en"
    source: str  # "cli", "env", "default"
```

### MessageDictionary
```python
class MessageDictionary:
    def get(self, key: str, **kwargs) -> str:
        """Get translated message with optional formatting"""
```

## AI Language Instruction

```python
AI_LANGUAGE_INSTRUCTION = {
    "en": "IMPORTANT: Respond entirely in English.",
    "fr": ""  # No instruction needed, prompts already in French
}
```

## Next Steps

1. Generate tasks.md
2. Create message dictionaries
3. Implement language detection
4. Add CLI parameter
5. Inject AI instructions
