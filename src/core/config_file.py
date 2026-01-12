"""
Configuration File Management for Aetheris (v2.9)

Handles loading, saving, and merging configuration from multiple sources:
- CLI arguments (highest priority)
- Local config.json (project-specific)
- Global config.json (~/.aetheris/config.json)
- Environment variables (.env)
- Default values (lowest priority)
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.core.config_schema import (
    ConfigSchema,
    get_default_config,
    validate_no_secrets,
)
from src.core.logger import log_print
from src.i18n import t


class ConfigFileError(Exception):
    """Exception raised for configuration file errors"""

    pass


class ConfigValidationError(Exception):
    """Exception raised for configuration validation errors"""

    pass


@dataclass
class ConfigSource:
    """Represents the source of a configuration value"""

    source: str  # 'cli', 'local', 'global', 'env', 'default'
    path: Optional[str] = None  # File path if applicable


class ConfigFile:
    """
    Handles loading and saving of config.json files

    Supports:
    - Local project config: ./config.json
    - Global user config: ~/.aetheris/config.json
    """

    LOCAL_CONFIG_NAME = "config.json"
    GLOBAL_CONFIG_DIR = ".aetheris"
    GLOBAL_CONFIG_NAME = "config.json"

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir).resolve()
        self._local_config: Optional[Dict[str, Any]] = None
        self._global_config: Optional[Dict[str, Any]] = None
        self._local_path: Optional[Path] = None
        self._global_path: Optional[Path] = None

    @property
    def local_config_path(self) -> Path:
        """Path to local config.json"""
        return self.root_dir / self.LOCAL_CONFIG_NAME

    @property
    def global_config_path(self) -> Path:
        """Path to global config.json (~/.aetheris/config.json)"""
        home = Path.home()
        return home / self.GLOBAL_CONFIG_DIR / self.GLOBAL_CONFIG_NAME

    def load_local_config(self) -> Optional[Dict[str, Any]]:
        """
        Load configuration from local config.json

        Returns:
            Configuration dictionary or None if file doesn't exist
        """
        if self._local_config is not None:
            return self._local_config

        config_path = self.local_config_path
        if not config_path.exists():
            return None

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                self._local_config = json.load(f)
                self._local_path = config_path

                # Validate no secrets in config
                warnings = validate_no_secrets(self._local_config)
                for warning in warnings:
                    log_print(warning)

                return self._local_config
        except json.JSONDecodeError as e:
            raise ConfigFileError(
                t(
                    "config.invalid_json",
                    path=str(config_path),
                    error=str(e),
                    fallback=f"Invalid JSON in {config_path}: {e}",
                )
            )
        except PermissionError:
            log_print(
                t(
                    "config.permission_denied",
                    path=str(config_path),
                    fallback=f"⚠️  Permission denied reading {config_path}",
                )
            )
            return None

    def load_global_config(self) -> Optional[Dict[str, Any]]:
        """
        Load configuration from global config.json

        Returns:
            Configuration dictionary or None if file doesn't exist
        """
        if self._global_config is not None:
            return self._global_config

        config_path = self.global_config_path
        if not config_path.exists():
            return None

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                self._global_config = json.load(f)
                self._global_path = config_path

                # Validate no secrets in config
                warnings = validate_no_secrets(self._global_config)
                for warning in warnings:
                    log_print(warning)

                return self._global_config
        except json.JSONDecodeError as e:
            # For global config, warn and use defaults instead of failing
            log_print(
                t(
                    "config.global_corrupted",
                    path=str(config_path),
                    fallback=f"⚠️  Global config corrupted ({config_path}): {e}. Using defaults.",
                )
            )
            return None
        except PermissionError:
            log_print(
                t(
                    "config.permission_denied",
                    path=str(config_path),
                    fallback=f"⚠️  Permission denied reading {config_path}. Using local config only.",
                )
            )
            return None

    def save_local_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to local config.json"""
        config_path = self.local_config_path

        # Sort keys for git-friendly diffs
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, sort_keys=True, ensure_ascii=False)
            f.write("\n")  # Trailing newline

        self._local_config = config
        self._local_path = config_path

    def save_global_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to global config.json"""
        config_path = self.global_config_path

        # Create directory if needed
        config_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Sort keys for git-friendly diffs
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, sort_keys=True, ensure_ascii=False)
                f.write("\n")

            self._global_config = config
            self._global_path = config_path
        except PermissionError:
            raise ConfigFileError(
                t(
                    "config.save_permission_denied",
                    path=str(config_path),
                    fallback=f"Permission denied writing to {config_path}",
                )
            )

    def config_exists(self, scope: str = "local") -> bool:
        """Check if config file exists"""
        if scope == "local":
            return self.local_config_path.exists()
        elif scope == "global":
            return self.global_config_path.exists()
        return False


class ConfigHierarchy:
    """
    Manages configuration priority hierarchy

    Priority (highest to lowest):
    1. CLI arguments
    2. Local config.json (./config.json)
    3. Global config.json (~/.aetheris/config.json)
    4. Environment variables (.env)
    5. Built-in defaults
    """

    def __init__(self, root_dir: str = "."):
        self.config_file = ConfigFile(root_dir)
        self._merged_config: Optional[ConfigSchema] = None
        self._value_sources: Dict[str, ConfigSource] = {}

    def load(self, cli_overrides: Optional[Dict[str, Any]] = None) -> ConfigSchema:
        """
        Load and merge configuration from all sources

        Args:
            cli_overrides: Dictionary of CLI argument overrides

        Returns:
            Merged ConfigSchema with all settings
        """
        # Start with defaults
        merged = get_default_config().to_dict()
        self._value_sources = self._track_sources(merged, "default")

        # Layer 1: Global config (lowest priority after defaults)
        global_config = self.config_file.load_global_config()
        if global_config:
            merged = self._deep_merge(merged, global_config)
            self._update_sources(global_config, "global", self.config_file.global_config_path)

        # Layer 2: Local config
        local_config = self.config_file.load_local_config()
        if local_config:
            merged = self._deep_merge(merged, local_config)
            self._update_sources(local_config, "local", self.config_file.local_config_path)

        # Layer 3: CLI overrides (highest priority)
        if cli_overrides:
            merged = self._deep_merge(merged, cli_overrides)
            self._update_sources(cli_overrides, "cli")

        self._merged_config = ConfigSchema.from_dict(merged)
        return self._merged_config

    def get_value_source(self, key_path: str) -> ConfigSource:
        """
        Get the source of a configuration value

        Args:
            key_path: Dot-separated path to config value (e.g., 'ai.provider')

        Returns:
            ConfigSource indicating where the value came from
        """
        return self._value_sources.get(key_path, ConfigSource(source="default"))

    def get_merged_config(self) -> Optional[ConfigSchema]:
        """Get the last loaded merged configuration"""
        return self._merged_config

    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries

        Args:
            base: Base dictionary
            override: Dictionary with values to override

        Returns:
            Merged dictionary
        """
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dicts
                result[key] = self._deep_merge(result[key], value)
            else:
                # Override value
                result[key] = value

        return result

    def _track_sources(
        self, config: Dict[str, Any], source: str, path: str = "", file_path: Optional[Path] = None
    ) -> Dict[str, ConfigSource]:
        """Track the source of each configuration value"""
        sources = {}
        for key, value in config.items():
            current_path = f"{path}.{key}" if path else key
            sources[current_path] = ConfigSource(
                source=source, path=str(file_path) if file_path else None
            )
            if isinstance(value, dict):
                sources.update(self._track_sources(value, source, current_path, file_path))
        return sources

    def _update_sources(
        self, config: Dict[str, Any], source: str, file_path: Optional[Path] = None, path: str = ""
    ) -> None:
        """Update source tracking for overridden values"""
        for key, value in config.items():
            current_path = f"{path}.{key}" if path else key
            self._value_sources[current_path] = ConfigSource(
                source=source, path=str(file_path) if file_path else None
            )
            if isinstance(value, dict):
                self._update_sources(value, source, file_path, current_path)


def get_known_config_keys() -> List[str]:
    """Get list of all known configuration keys for typo detection"""
    default = get_default_config().to_dict()
    keys = []

    def collect_keys(d: Dict[str, Any], prefix: str = "") -> None:
        for key, value in d.items():
            full_key = f"{prefix}.{key}" if prefix else key
            keys.append(full_key)
            if isinstance(value, dict):
                collect_keys(value, full_key)

    collect_keys(default)
    return keys


def warn_unknown_keys(config: Dict[str, Any], known_keys: Optional[List[str]] = None) -> List[str]:
    """
    Warn about unknown configuration keys (possible typos)

    Args:
        config: Configuration dictionary to check
        known_keys: List of known valid keys

    Returns:
        List of warning messages
    """
    if known_keys is None:
        known_keys = get_known_config_keys()

    warnings = []

    def check_keys(d: Dict[str, Any], prefix: str = "") -> None:
        for key, value in d.items():
            full_key = f"{prefix}.{key}" if prefix else key

            # Check if this key or any parent is known
            is_known = False
            for known in known_keys:
                if full_key == known or known.startswith(f"{full_key}."):
                    is_known = True
                    break

            if not is_known and not prefix.startswith("presets"):
                # Custom presets are allowed, so skip warning for presets section
                warnings.append(
                    t(
                        "config.unknown_key",
                        config_key=full_key,
                        fallback=f"⚠️  Unknown config key: '{full_key}'. Possible typo?",
                    )
                )

            if isinstance(value, dict):
                check_keys(value, full_key)

    check_keys(config)
    return warnings
