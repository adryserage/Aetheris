"""
Configuration Schema for Aetheris (v2.9)

Defines the structure and validation for config.json files.
Supports hierarchical configuration with CLI > local > global > defaults priority.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from src.i18n import t


@dataclass
class AIConfigSchema:
    """AI provider configuration section"""

    provider: str = "gemini"
    model: str = "default"
    timeout: int = 120
    max_retries: int = 3


@dataclass
class AnalysisConfigSchema:
    """Analysis settings configuration section"""

    default_preset: str = "comprehensive"
    enabled_agents: List[str] = field(default_factory=lambda: ["all"])
    skip_agents: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(
        default_factory=lambda: [
            "**/node_modules/**",
            "**/.git/**",
            "**/venv/**",
            "**/__pycache__/**",
            "**/dist/**",
            "**/build/**",
            "**/.venv/**",
            "**/coverage/**",
        ]
    )
    analyze_changed_files_only: bool = False
    max_dependency_depth: int = 2
    enable_cache: bool = True
    cache_ttl_seconds: int = 604800  # 7 days


@dataclass
class SafetyConfigSchema:
    """Safety settings configuration section"""

    default_profile: str = "safe"
    custom_allowlist: List[str] = field(default_factory=list)
    audit_log_path: str = "aetheris-audit.jsonl"


@dataclass
class PresetSchema:
    """Custom preset definition"""

    description: str = ""
    agents: List[str] = field(default_factory=list)


@dataclass
class OutputConfigSchema:
    """Output settings configuration section"""

    format: str = "markdown"
    directory: str = "docs/analyses"
    architecture_report_path: str = "docs/architecture_overview.md"


@dataclass
class ConfigSchema:
    """
    Complete configuration schema for config.json

    Represents all configurable options for Aetheris.
    Used for validation and providing defaults.
    """

    ai: AIConfigSchema = field(default_factory=AIConfigSchema)
    analysis: AnalysisConfigSchema = field(default_factory=AnalysisConfigSchema)
    safety: SafetyConfigSchema = field(default_factory=SafetyConfigSchema)
    presets: Dict[str, PresetSchema] = field(default_factory=dict)
    output: OutputConfigSchema = field(default_factory=OutputConfigSchema)

    def to_dict(self) -> Dict[str, Any]:
        """Convert schema to dictionary for JSON serialization"""
        return {
            "ai": {
                "provider": self.ai.provider,
                "model": self.ai.model,
                "timeout": self.ai.timeout,
                "max_retries": self.ai.max_retries,
            },
            "analysis": {
                "default_preset": self.analysis.default_preset,
                "enabled_agents": self.analysis.enabled_agents,
                "skip_agents": self.analysis.skip_agents,
                "exclude_patterns": self.analysis.exclude_patterns,
                "analyze_changed_files_only": self.analysis.analyze_changed_files_only,
                "max_dependency_depth": self.analysis.max_dependency_depth,
                "enable_cache": self.analysis.enable_cache,
                "cache_ttl_seconds": self.analysis.cache_ttl_seconds,
            },
            "safety": {
                "default_profile": self.safety.default_profile,
                "custom_allowlist": self.safety.custom_allowlist,
                "audit_log_path": self.safety.audit_log_path,
            },
            "presets": {
                name: {"description": preset.description, "agents": preset.agents}
                for name, preset in self.presets.items()
            },
            "output": {
                "format": self.output.format,
                "directory": self.output.directory,
                "architecture_report_path": self.output.architecture_report_path,
            },
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConfigSchema":
        """Create ConfigSchema from dictionary (parsed JSON)"""
        ai_data = data.get("ai", {})
        analysis_data = data.get("analysis", {})
        safety_data = data.get("safety", {})
        presets_data = data.get("presets", {})
        output_data = data.get("output", {})

        ai = AIConfigSchema(
            provider=ai_data.get("provider", "gemini"),
            model=ai_data.get("model", "default"),
            timeout=ai_data.get("timeout", 120),
            max_retries=ai_data.get("max_retries", 3),
        )

        analysis = AnalysisConfigSchema(
            default_preset=analysis_data.get("default_preset", "comprehensive"),
            enabled_agents=analysis_data.get("enabled_agents", ["all"]),
            skip_agents=analysis_data.get("skip_agents", []),
            exclude_patterns=analysis_data.get(
                "exclude_patterns",
                [
                    "**/node_modules/**",
                    "**/.git/**",
                    "**/venv/**",
                    "**/__pycache__/**",
                ],
            ),
            analyze_changed_files_only=analysis_data.get("analyze_changed_files_only", False),
            max_dependency_depth=analysis_data.get("max_dependency_depth", 2),
            enable_cache=analysis_data.get("enable_cache", True),
            cache_ttl_seconds=analysis_data.get("cache_ttl_seconds", 604800),
        )

        safety = SafetyConfigSchema(
            default_profile=safety_data.get("default_profile", "safe"),
            custom_allowlist=safety_data.get("custom_allowlist", []),
            audit_log_path=safety_data.get("audit_log_path", "aetheris-audit.jsonl"),
        )

        presets = {}
        for name, preset_data in presets_data.items():
            presets[name] = PresetSchema(
                description=preset_data.get("description", ""),
                agents=preset_data.get("agents", []),
            )

        output = OutputConfigSchema(
            format=output_data.get("format", "markdown"),
            directory=output_data.get("directory", "docs/analyses"),
            architecture_report_path=output_data.get(
                "architecture_report_path", "docs/architecture_overview.md"
            ),
        )

        return cls(ai=ai, analysis=analysis, safety=safety, presets=presets, output=output)


# List of keys that should NEVER be in config.json (secrets only in .env)
SECRET_KEYS = [
    "api_key",
    "api_secret",
    "token",
    "password",
    "secret",
    "credential",
    "GEMINI_API_KEY",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GITHUB_TOKEN",
]


def get_default_config() -> ConfigSchema:
    """Returns default configuration schema"""
    return ConfigSchema()


def validate_no_secrets(config_dict: Dict[str, Any], path: str = "") -> List[str]:
    """
    Check if config dictionary contains any secret keys

    Args:
        config_dict: Configuration dictionary to validate
        path: Current path in config (for error messages)

    Returns:
        List of warning messages for detected secrets
    """
    warnings = []

    for key, value in config_dict.items():
        current_path = f"{path}.{key}" if path else key

        # Check if key matches any secret pattern
        key_lower = key.lower()
        for secret_key in SECRET_KEYS:
            if secret_key.lower() in key_lower:
                warnings.append(
                    t(
                        "config.secret_detected",
                        key=current_path,
                        fallback=f"⚠️  Secret detected in config.json: '{current_path}'. "
                        f"Move to .env file for security.",
                    )
                )
                break

        # Recursively check nested objects
        if isinstance(value, dict):
            warnings.extend(validate_no_secrets(value, current_path))

    return warnings
