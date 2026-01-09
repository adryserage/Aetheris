"""Cleanup service for artifact and file management."""

import fnmatch
import logging
import os
import shutil
from pathlib import Path
from typing import Generator

from ..config.exclusion_patterns import (
    DEFAULT_EXCLUSIONS,
    DEEP_CLEAN_EXCLUSIONS,
    get_exclusions,
)
from ..models.cleanup_models import CleanupConfig, CleanupResult, ExclusionConfig

logger = logging.getLogger(__name__)


def matches_exclusion_pattern(filepath: str | Path, patterns: list[str]) -> bool:
    """Check if a filepath matches any exclusion pattern.

    Args:
        filepath: Path to check (relative or absolute)
        patterns: List of glob patterns to match against

    Returns:
        True if the filepath matches any pattern
    """
    filepath_str = str(filepath)
    filepath_parts = Path(filepath).parts

    for pattern in patterns:
        # Handle negation patterns (whitelist)
        if pattern.startswith("!"):
            continue

        # Handle directory patterns (ending with /)
        if pattern.endswith("/"):
            dir_pattern = pattern.rstrip("/")
            if any(fnmatch.fnmatch(part, dir_pattern) for part in filepath_parts):
                return True

        # Handle recursive patterns (**)
        if "**" in pattern:
            # Convert ** pattern to work with fnmatch
            glob_pattern = pattern.replace("**", "*")
            if fnmatch.fnmatch(filepath_str, glob_pattern):
                return True
            # Also check if any path component matches
            if fnmatch.fnmatch(Path(filepath).name, pattern.replace("**/", "")):
                return True

        # Standard pattern matching
        if fnmatch.fnmatch(filepath_str, pattern):
            return True
        if fnmatch.fnmatch(Path(filepath).name, pattern):
            return True

    return False


def is_whitelisted(filepath: str | Path, patterns: list[str]) -> bool:
    """Check if a filepath is whitelisted (negation pattern).

    Args:
        filepath: Path to check
        patterns: List of patterns including negation patterns starting with !

    Returns:
        True if the filepath is explicitly whitelisted
    """
    filepath_str = str(filepath)
    filename = Path(filepath).name

    for pattern in patterns:
        if pattern.startswith("!"):
            whitelist_pattern = pattern[1:]  # Remove the !
            if fnmatch.fnmatch(filepath_str, whitelist_pattern):
                return True
            if fnmatch.fnmatch(filename, whitelist_pattern):
                return True

    return False


def get_excluded_files(
    directory: str | Path,
    patterns: list[str] | None = None,
    deep: bool = False,
) -> list[Path]:
    """Get list of files matching exclusion patterns.

    Args:
        directory: Root directory to scan
        patterns: Custom patterns (uses defaults if None)
        deep: Include deep clean patterns

    Returns:
        List of Path objects for matched files
    """
    if patterns is None:
        patterns = get_exclusions(deep=deep)

    directory = Path(directory)
    matched_files: list[Path] = []

    for root, dirs, files in os.walk(directory):
        root_path = Path(root)
        rel_root = root_path.relative_to(directory)

        # Check directories for exclusion
        dirs_to_remove = []
        for d in dirs:
            dir_path = rel_root / d
            if matches_exclusion_pattern(dir_path, patterns) and not is_whitelisted(
                dir_path, patterns
            ):
                dirs_to_remove.append(d)
                matched_files.append(root_path / d)

        # Remove excluded directories from traversal
        for d in dirs_to_remove:
            dirs.remove(d)

        # Check files
        for f in files:
            file_path = rel_root / f
            if matches_exclusion_pattern(file_path, patterns) and not is_whitelisted(
                file_path, patterns
            ):
                matched_files.append(root_path / f)

    return matched_files


class CleanupService:
    """Service for cleaning up development artifacts and build files."""

    def __init__(self, config: CleanupConfig | None = None):
        """Initialize cleanup service.

        Args:
            config: Cleanup configuration options
        """
        self.config = config or CleanupConfig()
        self._patterns = get_exclusions(
            deep=self.config.deep, custom=self.config.custom_patterns
        )

    def get_files_to_clean(
        self, directory: str | Path, deep: bool | None = None
    ) -> list[Path]:
        """Get list of files that would be cleaned.

        Args:
            directory: Directory to scan
            deep: Override deep clean setting

        Returns:
            List of paths to be cleaned
        """
        use_deep = deep if deep is not None else self.config.deep
        patterns = get_exclusions(deep=use_deep, custom=self.config.custom_patterns)
        return get_excluded_files(directory, patterns, deep=use_deep)

    def calculate_size(self, files: list[Path]) -> int:
        """Calculate total size of files in bytes.

        Args:
            files: List of file paths

        Returns:
            Total size in bytes
        """
        total_size = 0
        for path in files:
            try:
                if path.is_file():
                    total_size += path.stat().st_size
                elif path.is_dir():
                    total_size += sum(
                        f.stat().st_size for f in path.rglob("*") if f.is_file()
                    )
            except (OSError, PermissionError) as e:
                logger.warning(f"Could not get size of {path}: {e}")

        return total_size

    def delete_files(self, files: list[Path]) -> CleanupResult:
        """Delete specified files and directories.

        Args:
            files: List of paths to delete

        Returns:
            CleanupResult with deletion statistics
        """
        result = CleanupResult()

        for path in files:
            try:
                if path.is_symlink():
                    if not self.config.follow_symlinks:
                        logger.debug(f"Skipping symlink: {path}")
                        continue
                    path.unlink()
                    result.files_deleted.append(path)
                elif path.is_file():
                    size = path.stat().st_size
                    path.unlink()
                    result.files_deleted.append(path)
                    result.bytes_freed += size
                elif path.is_dir():
                    size = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
                    shutil.rmtree(path)
                    result.directories_deleted.append(path)
                    result.bytes_freed += size
            except PermissionError as e:
                error_msg = f"Permission denied: {path} - {e}"
                logger.warning(error_msg)
                result.errors.append(error_msg)
            except OSError as e:
                error_msg = f"Error deleting {path}: {e}"
                logger.warning(error_msg)
                result.errors.append(error_msg)

        return result

    def cleanup_dry_run(self, directory: str | Path) -> str:
        """Preview cleanup without actually deleting files.

        Args:
            directory: Directory to preview

        Returns:
            Formatted string showing what would be deleted
        """
        files = self.get_files_to_clean(directory)
        total_size = self.calculate_size(files)

        if not files:
            return "No files match the exclusion patterns."

        lines = ["Files/directories that would be deleted:", ""]

        # Group by type
        dirs = [f for f in files if f.is_dir()]
        regular_files = [f for f in files if f.is_file()]

        if dirs:
            lines.append("Directories:")
            for d in sorted(dirs):
                dir_size = sum(f.stat().st_size for f in d.rglob("*") if f.is_file())
                lines.append(f"  {d}/ ({self._format_size(dir_size)})")

        if regular_files:
            lines.append("\nFiles:")
            for f in sorted(regular_files):
                try:
                    size = f.stat().st_size
                    lines.append(f"  {f} ({self._format_size(size)})")
                except OSError:
                    lines.append(f"  {f} (size unknown)")

        lines.append("")
        lines.append(f"Total: {len(files)} items, {self._format_size(total_size)}")

        return "\n".join(lines)

    def cleanup(self, directory: str | Path) -> CleanupResult:
        """Execute cleanup on directory.

        Args:
            directory: Directory to clean

        Returns:
            CleanupResult with statistics
        """
        if self.config.dry_run:
            # For dry run, return empty result with files that would be deleted
            files = self.get_files_to_clean(directory)
            result = CleanupResult()
            result.bytes_freed = self.calculate_size(files)
            return result

        files = self.get_files_to_clean(directory)
        return self.delete_files(files)

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format byte size as human-readable string."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
