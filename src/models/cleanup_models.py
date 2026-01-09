"""Data models for artifact cleanup and security scanning."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class ConfidenceLevel(Enum):
    """Confidence level for secret detection."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ExclusionConfig:
    """Configuration for file exclusion during cleanup/build."""

    patterns: list[str] = field(default_factory=list)
    deep_clean: bool = False
    custom_patterns: list[str] = field(default_factory=list)
    whitelist: list[str] = field(default_factory=lambda: [".env.example"])

    def all_patterns(self) -> list[str]:
        """Return all exclusion patterns combined."""
        return self.patterns + self.custom_patterns


@dataclass
class CleanupConfig:
    """Configuration for the cleanup process."""

    dry_run: bool = False
    deep: bool = False
    minify: bool = False
    strip_docstrings: bool = False
    custom_patterns: list[str] = field(default_factory=list)
    follow_symlinks: bool = False


@dataclass
class SecretPattern:
    """Pattern definition for secret detection."""

    name: str
    regex: str
    description: str
    confidence: ConfidenceLevel = ConfidenceLevel.HIGH
    examples: list[str] = field(default_factory=list)


@dataclass
class SecretMatch:
    """A detected secret match in a file."""

    file: Path
    line_number: int
    line_content: str
    pattern_name: str
    masked_value: str
    confidence: ConfidenceLevel

    def __str__(self) -> str:
        """Return formatted string representation."""
        return (
            f"{self.file}:{self.line_number} - [{self.pattern_name}] "
            f"({self.confidence.value} confidence): {self.masked_value}"
        )


@dataclass
class CleanupResult:
    """Result of a cleanup operation."""

    files_deleted: list[Path] = field(default_factory=list)
    directories_deleted: list[Path] = field(default_factory=list)
    bytes_freed: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def total_items_deleted(self) -> int:
        """Return total count of deleted items."""
        return len(self.files_deleted) + len(self.directories_deleted)

    @property
    def size_freed_mb(self) -> float:
        """Return size freed in megabytes."""
        return self.bytes_freed / (1024 * 1024)


@dataclass
class ValidationReport:
    """Report from package validation."""

    size_bytes: int = 0
    size_mb: float = 0.0
    max_size_mb: float = 50.0
    excluded_files_found: list[Path] = field(default_factory=list)
    secrets_found: list[SecretMatch] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    is_valid: bool = True

    def __post_init__(self) -> None:
        """Calculate derived fields and validity."""
        self.size_mb = self.size_bytes / (1024 * 1024)
        self._update_validity()

    def _update_validity(self) -> None:
        """Update validity based on current state."""
        self.is_valid = (
            len(self.secrets_found) == 0
            and len(self.excluded_files_found) == 0
            and self.size_mb <= self.max_size_mb
        )

    def add_secret(self, match: SecretMatch) -> None:
        """Add a secret match and update validity."""
        self.secrets_found.append(match)
        self._update_validity()

    def add_excluded_file(self, path: Path) -> None:
        """Add an excluded file and update validity."""
        self.excluded_files_found.append(path)
        self._update_validity()


@dataclass
class ScanConfig:
    """Configuration for secret scanning."""

    ignore_file: Optional[Path] = None
    scan_hidden: bool = False
    max_file_size_mb: float = 10.0
    exclude_patterns: list[str] = field(default_factory=list)
    include_low_confidence: bool = False
