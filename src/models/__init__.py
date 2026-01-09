"""
Modèles de données (dataclasses)
"""

from .cleanup_models import (
    CleanupConfig,
    CleanupResult,
    ConfidenceLevel,
    ExclusionConfig,
    ScanConfig,
    SecretMatch,
    SecretPattern,
    ValidationReport,
)

__all__ = [
    "CleanupConfig",
    "CleanupResult",
    "ConfidenceLevel",
    "ExclusionConfig",
    "ScanConfig",
    "SecretMatch",
    "SecretPattern",
    "ValidationReport",
]
