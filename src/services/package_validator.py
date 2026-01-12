"""Package validator service for pre-publish checks."""

import logging
import os
from pathlib import Path

from ..config.exclusion_patterns import DEFAULT_EXCLUSIONS
from ..models.cleanup_models import ScanConfig, SecretMatch, ValidationReport
from .cleanup_service import get_excluded_files
from .secret_scanner import SecretScanner

logger = logging.getLogger(__name__)


class PackageValidator:
    """Validator for checking packages before publication."""

    def __init__(
        self,
        max_size_mb: float = 50.0,
        exclusion_patterns: list[str] | None = None,
        secrets_ignore_file: str | Path | None = None,
    ):
        """Initialize the package validator.

        Args:
            max_size_mb: Maximum allowed package size in MB
            exclusion_patterns: Custom exclusion patterns
            secrets_ignore_file: Path to .secretsignore file
        """
        self.max_size_mb = max_size_mb
        self.exclusion_patterns = exclusion_patterns or DEFAULT_EXCLUSIONS

        # Initialize secret scanner
        scan_config = ScanConfig(
            ignore_file=Path(secrets_ignore_file) if secrets_ignore_file else None,
            exclude_patterns=["*.pyc", "__pycache__", ".git"],
        )
        self.secret_scanner = SecretScanner(config=scan_config)

    def check_exclusions(self, directory: str | Path) -> list[Path]:
        """Check for files that should be excluded from the package.

        Args:
            directory: Directory to check

        Returns:
            List of files that should be excluded but are present
        """
        return get_excluded_files(directory, self.exclusion_patterns)

    def check_size(self, directory: str | Path) -> tuple[float, bool]:
        """Check the total size of the package directory.

        Args:
            directory: Directory to measure

        Returns:
            Tuple of (size_mb, is_within_limit)
        """
        directory = Path(directory)
        total_size = 0

        for root, dirs, files in os.walk(directory):
            # Skip common non-package directories
            dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", "node_modules"}]

            for filename in files:
                filepath = Path(root) / filename
                try:
                    total_size += filepath.stat().st_size
                except OSError:
                    pass

        size_mb = total_size / (1024 * 1024)
        return size_mb, size_mb <= self.max_size_mb

    def check_secrets(self, directory: str | Path) -> list[SecretMatch]:
        """Scan directory for secrets.

        Args:
            directory: Directory to scan

        Returns:
            List of detected secrets
        """
        return self.secret_scanner.scan_directory(directory)

    def validate(self, directory: str | Path) -> ValidationReport:
        """Run all validation checks on a directory.

        Args:
            directory: Directory to validate

        Returns:
            ValidationReport with all check results
        """
        directory = Path(directory)

        if not directory.exists():
            report = ValidationReport(max_size_mb=self.max_size_mb)
            report.warnings.append(f"Directory does not exist: {directory}")
            report.is_valid = False
            return report

        logger.info(f"Validating package at {directory}")

        # Calculate size
        size_mb, size_ok = self.check_size(directory)

        # Check for excluded files
        excluded_files = self.check_exclusions(directory)

        # Scan for secrets
        secrets = self.check_secrets(directory)

        # Build report
        report = ValidationReport(
            size_bytes=int(size_mb * 1024 * 1024),
            max_size_mb=self.max_size_mb,
            excluded_files_found=excluded_files,
            secrets_found=secrets,
        )

        # Add warnings
        if not size_ok:
            report.warnings.append(
                f"Package size ({size_mb:.1f} MB) exceeds limit ({self.max_size_mb} MB)"
            )

        if excluded_files:
            report.warnings.append(f"Found {len(excluded_files)} files that should be excluded")

        if secrets:
            high_confidence = [s for s in secrets if s.confidence.value == "high"]
            if high_confidence:
                report.warnings.append(f"Found {len(high_confidence)} high-confidence secrets!")

        return report

    def fix_issues(self, directory: str | Path, report: ValidationReport) -> list[str]:
        """Attempt to fix issues found during validation.

        Args:
            directory: Directory to fix
            report: Validation report with issues

        Returns:
            List of actions taken
        """
        actions: list[str] = []
        directory = Path(directory)

        # Remove excluded files
        for filepath in report.excluded_files_found:
            try:
                if filepath.is_dir():
                    import shutil

                    shutil.rmtree(filepath)
                    actions.append(f"Removed directory: {filepath}")
                else:
                    filepath.unlink()
                    actions.append(f"Removed file: {filepath}")
            except OSError as e:
                actions.append(f"Failed to remove {filepath}: {e}")

        # We cannot automatically fix secrets - they need manual review
        if report.secrets_found:
            actions.append(
                f"WARNING: {len(report.secrets_found)} secrets detected - "
                "manual review required!"
            )

        return actions

    def format_report(self, report: ValidationReport) -> str:
        """Format validation report as a string.

        Args:
            report: ValidationReport to format

        Returns:
            Formatted report string
        """
        lines = [
            "Package Validation Report",
            "=" * 50,
            "",
            f"Size: {report.size_mb:.2f} MB (limit: {report.max_size_mb} MB)",
            f"Status: {'PASS' if report.is_valid else 'FAIL'}",
            "",
        ]

        if report.warnings:
            lines.append("Warnings:")
            for warning in report.warnings:
                lines.append(f"  - {warning}")
            lines.append("")

        if report.excluded_files_found:
            lines.append(f"Excluded files found ({len(report.excluded_files_found)}):")
            for f in report.excluded_files_found[:20]:  # Limit to first 20
                lines.append(f"  - {f}")
            if len(report.excluded_files_found) > 20:
                lines.append(f"  ... and {len(report.excluded_files_found) - 20} more")
            lines.append("")

        if report.secrets_found:
            lines.append(f"Secrets detected ({len(report.secrets_found)}):")
            for secret in report.secrets_found[:10]:  # Limit to first 10
                lines.append(f"  - {secret}")
            if len(report.secrets_found) > 10:
                lines.append(f"  ... and {len(report.secrets_found) - 10} more")
            lines.append("")

        if report.is_valid:
            lines.append("Package is ready for publication.")
        else:
            lines.append("Package has issues that must be resolved before publication.")

        return "\n".join(lines)
