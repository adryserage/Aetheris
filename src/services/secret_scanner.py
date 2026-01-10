"""Secret scanner service for detecting credentials in code."""

import fnmatch
import logging
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Generator

from ..config.secret_patterns import (
    SECRET_PATTERNS,
    SecretPatternDef,
    compile_patterns,
    get_patterns_by_confidence,
)
from ..models.cleanup_models import ConfidenceLevel, ScanConfig, SecretMatch

logger = logging.getLogger(__name__)

# Binary file extensions to skip
BINARY_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".so",
    ".dll",
    ".exe",
    ".bin",
    ".o",
    ".a",
    ".lib",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".bz2",
    ".7z",
    ".rar",
    ".mp3",
    ".mp4",
    ".avi",
    ".mov",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".otf",
}


def mask_secret(value: str, show_start: int = 4, show_end: int = 2) -> str:
    """Mask a secret value, showing only start and end characters.

    Args:
        value: The secret value to mask
        show_start: Number of characters to show at start
        show_end: Number of characters to show at end

    Returns:
        Masked string like "AKIA****xy"
    """
    if len(value) <= show_start + show_end:
        return "*" * len(value)

    start = value[:show_start]
    end = value[-show_end:] if show_end > 0 else ""
    middle_len = len(value) - show_start - show_end
    middle = "*" * min(middle_len, 8)  # Cap at 8 asterisks

    return f"{start}{middle}{end}"


class SecretScanner:
    """Scanner for detecting secrets and credentials in files."""

    def __init__(
        self,
        config: ScanConfig | None = None,
        patterns: list[SecretPatternDef] | None = None,
    ):
        """Initialize the secret scanner.

        Args:
            config: Scanner configuration
            patterns: Custom patterns (uses defaults if None)
        """
        self.config = config or ScanConfig()
        self._patterns = patterns or SECRET_PATTERNS

        # Filter patterns by confidence if configured
        if not self.config.include_low_confidence:
            self._patterns = [p for p in self._patterns if p.confidence != "low"]

        # Compile all patterns
        self._compiled_patterns = [(p, re.compile(p.regex)) for p in self._patterns]

        # Load ignore patterns
        self._ignore_patterns: set[str] = set()
        if self.config.ignore_file:
            self._load_secrets_ignore(self.config.ignore_file)

    def _load_secrets_ignore(self, filepath: Path) -> None:
        """Load patterns from .secretsignore file.

        Args:
            filepath: Path to the ignore file
        """
        if not filepath.exists():
            logger.debug(f"Ignore file not found: {filepath}")
            return

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if line and not line.startswith("#"):
                        self._ignore_patterns.add(line)

            logger.info(f"Loaded {len(self._ignore_patterns)} ignore patterns")
        except OSError as e:
            logger.warning(f"Could not load ignore file: {e}")

    def load_secrets_ignore(self, filepath: str | Path) -> None:
        """Public method to load secrets ignore file.

        Args:
            filepath: Path to the .secretsignore file
        """
        self._load_secrets_ignore(Path(filepath))

    def _is_ignored(self, file_path: Path, line_content: str) -> bool:
        """Check if a potential secret should be ignored.

        Args:
            file_path: Path to the file
            line_content: The line containing the potential secret

        Returns:
            True if the match should be ignored
        """
        file_str = str(file_path)

        for pattern in self._ignore_patterns:
            # Check if it's a file pattern
            if fnmatch.fnmatch(file_str, pattern):
                return True
            if fnmatch.fnmatch(file_path.name, pattern):
                return True
            # Check if it's a content pattern (exact match)
            if pattern in line_content:
                return True

        return False

    def _is_binary_file(self, filepath: Path) -> bool:
        """Check if file appears to be binary.

        Args:
            filepath: Path to check

        Returns:
            True if file is likely binary
        """
        # Check extension first
        if filepath.suffix.lower() in BINARY_EXTENSIONS:
            return True

        # Check first bytes for null character
        try:
            with open(filepath, "rb") as f:
                chunk = f.read(1024)
                return b"\x00" in chunk
        except OSError:
            return True

    def scan_file(self, filepath: str | Path) -> list[SecretMatch]:
        """Scan a single file for secrets.

        Args:
            filepath: Path to the file to scan

        Returns:
            List of SecretMatch objects for detected secrets
        """
        filepath = Path(filepath)
        matches: list[SecretMatch] = []

        # Skip binary files
        if self._is_binary_file(filepath):
            return matches

        # Check file size
        try:
            size_mb = filepath.stat().st_size / (1024 * 1024)
            if size_mb > self.config.max_file_size_mb:
                logger.debug(f"Skipping large file: {filepath} ({size_mb:.1f} MB)")
                return matches
        except OSError:
            return matches

        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                for line_number, line in enumerate(f, start=1):
                    line_matches = self._scan_line(filepath, line_number, line)
                    matches.extend(line_matches)
        except OSError as e:
            logger.warning(f"Could not scan file {filepath}: {e}")

        return matches

    def _scan_line(self, filepath: Path, line_number: int, line: str) -> list[SecretMatch]:
        """Scan a single line for secrets.

        Args:
            filepath: Path to the source file
            line_number: Line number (1-indexed)
            line: The line content

        Returns:
            List of matches found in this line
        """
        matches: list[SecretMatch] = []

        for pattern_def, compiled_regex in self._compiled_patterns:
            for match in compiled_regex.finditer(line):
                # Get the matched value
                matched_value = match.group(1) if match.groups() else match.group(0)

                # Check if ignored
                if self._is_ignored(filepath, line):
                    continue

                # Create masked value
                masked = mask_secret(matched_value)

                # Determine confidence level
                confidence = ConfidenceLevel(pattern_def.confidence)

                matches.append(
                    SecretMatch(
                        file=filepath,
                        line_number=line_number,
                        line_content=line.strip()[:100],  # Truncate long lines
                        pattern_name=pattern_def.name,
                        masked_value=masked,
                        confidence=confidence,
                    )
                )

        return matches

    def scan_directory(
        self,
        directory: str | Path,
        max_workers: int = 4,
    ) -> list[SecretMatch]:
        """Scan a directory for secrets using parallel processing.

        Args:
            directory: Root directory to scan
            max_workers: Number of parallel workers

        Returns:
            List of all SecretMatch objects found
        """
        directory = Path(directory)
        all_matches: list[SecretMatch] = []
        files_to_scan = list(self._get_scannable_files(directory))

        logger.info(f"Scanning {len(files_to_scan)} files for secrets...")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {executor.submit(self.scan_file, f): f for f in files_to_scan}

            for future in as_completed(future_to_file):
                filepath = future_to_file[future]
                try:
                    matches = future.result()
                    all_matches.extend(matches)
                except Exception as e:
                    logger.error(f"Error scanning {filepath}: {e}")

        # Sort by confidence (high first) then by file
        all_matches.sort(
            key=lambda m: (
                {"high": 0, "medium": 1, "low": 2}[m.confidence.value],
                str(m.file),
                m.line_number,
            )
        )

        return all_matches

    def _get_scannable_files(self, directory: Path) -> Generator[Path, None, None]:
        """Get all files that should be scanned.

        Args:
            directory: Root directory

        Yields:
            Paths to files that should be scanned
        """
        for root, dirs, files in os.walk(directory):
            # Skip hidden directories unless configured
            if not self.config.scan_hidden:
                dirs[:] = [d for d in dirs if not d.startswith(".")]

            # Skip excluded patterns
            for pattern in self.config.exclude_patterns:
                dirs[:] = [d for d in dirs if not fnmatch.fnmatch(d, pattern)]

            for filename in files:
                if not self.config.scan_hidden and filename.startswith("."):
                    continue

                filepath = Path(root) / filename

                # Skip excluded patterns
                should_skip = False
                for pattern in self.config.exclude_patterns:
                    if fnmatch.fnmatch(filename, pattern):
                        should_skip = True
                        break
                if should_skip:
                    continue

                yield filepath

    def format_report(self, matches: list[SecretMatch]) -> str:
        """Format scan results as a report.

        Args:
            matches: List of secret matches

        Returns:
            Formatted report string
        """
        if not matches:
            return "No secrets detected."

        lines = [
            f"Found {len(matches)} potential secret(s):",
            "",
        ]

        # Group by confidence
        high = [m for m in matches if m.confidence == ConfidenceLevel.HIGH]
        medium = [m for m in matches if m.confidence == ConfidenceLevel.MEDIUM]
        low = [m for m in matches if m.confidence == ConfidenceLevel.LOW]

        if high:
            lines.append("HIGH CONFIDENCE (likely real secrets):")
            for m in high:
                lines.append(f"  {m}")
            lines.append("")

        if medium:
            lines.append("MEDIUM CONFIDENCE (review recommended):")
            for m in medium:
                lines.append(f"  {m}")
            lines.append("")

        if low:
            lines.append("LOW CONFIDENCE (may be false positives):")
            for m in low:
                lines.append(f"  {m}")
            lines.append("")

        return "\n".join(lines)
