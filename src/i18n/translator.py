"""
Translation service for Aetheris i18n.

Provides lazy-loading translation with fallback chain:
1. Current language translation
2. English translation (always complete)
3. Key itself (never crash)
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Path to locales directory (relative to this file's package)
LOCALES_DIR = Path(__file__).parent.parent / "locales"
DEFAULT_LANGUAGE = "en"
FALLBACK_LANGUAGE = "en"


@dataclass
class LanguageInfo:
    """Information about an available language."""

    code: str
    name: str
    is_default: bool = False


class Translator:
    """
    Translation service with lazy loading and fallback support.

    Translations are loaded on first access and cached in memory.
    Missing keys fall back to English, then to the key itself.
    """

    _instance: Optional["Translator"] = None

    def __init__(self) -> None:
        self._translations: dict[str, dict[str, str]] = {}
        self._current_lang: str = DEFAULT_LANGUAGE
        self._loaded_languages: set[str] = set()

    @classmethod
    def get_instance(cls) -> "Translator":
        """Get or create singleton instance."""
        if cls._instance is None:
            cls._instance = Translator()
        return cls._instance

    def _get_locale_path(self, lang: str) -> Path:
        """Get path to translation file for a language."""
        return LOCALES_DIR / f"{lang}.json"

    def load(self, lang: str) -> bool:
        """
        Load translation file for a language.

        Args:
            lang: Language code (e.g., 'en', 'fr')

        Returns:
            True if loaded successfully, False otherwise
        """
        if lang in self._loaded_languages:
            return True

        path = self._get_locale_path(lang)
        if not path.exists():
            logger.warning(f"Translation file not found: {path}")
            return False

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Validate structure
            if not isinstance(data, dict):
                logger.error(f"Invalid translation file format: {path} (expected dict)")
                return False

            # Check for _meta section
            if "_meta" not in data:
                logger.warning(f"Translation file missing _meta section: {path}")

            self._translations[lang] = data
            self._loaded_languages.add(lang)
            logger.debug(f"Loaded translation file: {path} ({len(data)} keys)")
            return True

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in translation file {path}: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to load translation file {path}: {e}")
            return False

    def set_language(self, lang: str) -> None:
        """
        Set the current language.

        Args:
            lang: Language code
        """
        self._current_lang = lang
        # Preload the language
        self.load(lang)
        # Always ensure fallback is loaded
        if lang != FALLBACK_LANGUAGE:
            self.load(FALLBACK_LANGUAGE)

    def get_language(self) -> str:
        """Get current language code."""
        return self._current_lang

    def get(self, key: str, **kwargs: Any) -> str:
        """
        Get translated string for a key.

        Falls back to English if key not found in current language,
        then to the key itself if not found in English.

        Args:
            key: Message key (e.g., 'cli.analysis.start')
            **kwargs: Interpolation variables

        Returns:
            Translated string with variables interpolated
        """
        # Ensure current language is loaded
        self.load(self._current_lang)

        # Try current language
        translations = self._translations.get(self._current_lang, {})
        value = translations.get(key)

        # Fallback to English
        if value is None and self._current_lang != FALLBACK_LANGUAGE:
            self.load(FALLBACK_LANGUAGE)
            fallback_translations = self._translations.get(FALLBACK_LANGUAGE, {})
            value = fallback_translations.get(key)
            if value is not None:
                logger.debug(
                    f"Missing translation for '{key}' in {self._current_lang}, "
                    f"using {FALLBACK_LANGUAGE}"
                )

        # Fallback to key itself
        if value is None:
            logger.warning(f"Missing translation key: {key}")
            return key

        # Interpolate variables
        if kwargs:
            try:
                value = value.format(**kwargs)
            except KeyError as e:
                logger.warning(f"Missing interpolation variable in '{key}': {e}")
            except Exception as e:
                logger.warning(f"Interpolation error in '{key}': {e}")

        return value

    def get_available_languages(self) -> list[LanguageInfo]:
        """
        Get list of available languages.

        Scans the locales directory for translation files.

        Returns:
            List of LanguageInfo objects
        """
        languages: List[LanguageInfo] = []

        if not LOCALES_DIR.exists():
            logger.warning(f"Locales directory not found: {LOCALES_DIR}")
            return languages

        for path in sorted(LOCALES_DIR.glob("*.json")):
            lang_code = path.stem
            # Load to get _meta info
            self.load(lang_code)
            translations = self._translations.get(lang_code, {})
            meta: Dict[str, Any] = {}
            if isinstance(translations, dict):
                meta_value: Any = translations.get("_meta", {})
                if isinstance(meta_value, dict):
                    meta = meta_value

            languages.append(
                LanguageInfo(
                    code=lang_code,
                    name=meta.get("name", lang_code.upper()),
                    is_default=(lang_code == DEFAULT_LANGUAGE),
                )
            )

        return languages


# Global translator instance
_translator: Optional[Translator] = None


def get_translator() -> Translator:
    """Get the global translator instance."""
    global _translator
    if _translator is None:
        _translator = Translator.get_instance()
    return _translator


def t(key: str, **kwargs: Any) -> str:
    """
    Translate a message key.

    This is the main function for getting translated strings.

    Args:
        key: Message key (e.g., 'cli.analysis.start')
        **kwargs: Interpolation variables

    Returns:
        Translated string

    Example:
        >>> t("cli.analysis.start")
        "Starting analysis..."
        >>> t("error.file_not_found", path="/foo.py")
        "File not found: /foo.py"
    """
    return get_translator().get(key, **kwargs)


def set_language(lang: str) -> None:
    """
    Set the current language.

    Args:
        lang: Language code (e.g., 'en', 'fr')
    """
    get_translator().set_language(lang)


def get_language() -> str:
    """
    Get the current language code.

    Returns:
        Current language code
    """
    return get_translator().get_language()


def get_available_languages() -> list[LanguageInfo]:
    """
    Get list of available languages.

    Returns:
        List of LanguageInfo objects with code, name, and is_default
    """
    return get_translator().get_available_languages()
