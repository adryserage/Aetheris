"""
Locale detection for Aetheris i18n.

Detects user's preferred language from multiple sources with priority:
1. CLI flag (--lang)
2. AETHERIS_LANG environment variable
3. System locale (LANG, LC_ALL, LC_MESSAGES)
4. Default (English)
"""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

# Supported language codes
SUPPORTED_LANGUAGES = {"en", "fr"}
DEFAULT_LANGUAGE = "en"


class LocaleDetector:
    """Detects user's preferred language from various sources."""

    @staticmethod
    def from_system() -> Optional[str]:
        """
        Parse language from system locale environment variables.

        Checks LC_ALL, LC_MESSAGES, LANG in order.
        Extracts language code from formats like 'fr_FR.UTF-8' -> 'fr'.

        Returns:
            Language code if detected and supported, None otherwise.
        """
        for var in ("LC_ALL", "LC_MESSAGES", "LANG"):
            value = os.environ.get(var, "")
            if value and value != "C" and value != "POSIX":
                # Extract language code: fr_FR.UTF-8 -> fr
                lang_code = value.split("_")[0].split(".")[0].lower()
                if lang_code and lang_code in SUPPORTED_LANGUAGES:
                    logger.debug(f"Detected system locale: {lang_code} from {var}={value}")
                    return lang_code
        return None

    @staticmethod
    def from_env() -> Optional[str]:
        """
        Read language from AETHERIS_LANG environment variable.

        Returns:
            Language code if set and supported, None otherwise.
        """
        value = os.environ.get("AETHERIS_LANG", "").strip().lower()
        if value:
            if value in SUPPORTED_LANGUAGES:
                logger.debug(f"Detected AETHERIS_LANG: {value}")
                return value
            else:
                logger.warning(
                    f"AETHERIS_LANG='{value}' is not supported. "
                    f"Available: {', '.join(sorted(SUPPORTED_LANGUAGES))}. "
                    f"Falling back to default."
                )
        return None

    @staticmethod
    def detect(cli_lang: Optional[str] = None) -> str:
        """
        Detect language with priority chain.

        Priority: CLI flag > AETHERIS_LANG > system locale > default (en)

        Args:
            cli_lang: Language code from --lang CLI flag (highest priority)

        Returns:
            Detected language code (always returns a valid code)
        """
        # Priority 1: CLI flag
        if cli_lang:
            cli_lang = cli_lang.strip().lower()
            if cli_lang in SUPPORTED_LANGUAGES:
                logger.debug(f"Using CLI language: {cli_lang}")
                return cli_lang
            else:
                logger.warning(
                    f"--lang '{cli_lang}' is not supported. "
                    f"Available: {', '.join(sorted(SUPPORTED_LANGUAGES))}. "
                    f"Falling back to default."
                )

        # Priority 2: AETHERIS_LANG environment variable
        env_lang = LocaleDetector.from_env()
        if env_lang:
            return env_lang

        # Priority 3: System locale
        system_lang = LocaleDetector.from_system()
        if system_lang:
            return system_lang

        # Priority 4: Default
        logger.debug(f"Using default language: {DEFAULT_LANGUAGE}")
        return DEFAULT_LANGUAGE


def detect_language(cli_lang: Optional[str] = None) -> str:
    """
    Convenience function to detect language.

    Args:
        cli_lang: Language code from --lang CLI flag

    Returns:
        Detected language code
    """
    return LocaleDetector.detect(cli_lang)
