"""
Safety Profiles for Aetheris (v2.12)

Defines configurable safety profiles to control analysis execution boundaries:
- SAFE: Conservative mode with maximum guardrails (default)
- CI: Strict CI/CD mode, non-interactive, fail-fast
- YOLO: Full autonomy, extended capabilities with warnings
"""

import os
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ProfileType(str, Enum):
    """Available safety profile types"""

    SAFE = "safe"
    CI = "ci"
    YOLO = "yolo"

    @classmethod
    def from_string(cls, value: str) -> "ProfileType":
        """Convert string to ProfileType with validation"""
        value_lower = value.lower().strip()
        for profile in cls:
            if profile.value == value_lower:
                return profile
        valid_profiles = ", ".join(p.value for p in cls)
        raise ValueError(
            f"Invalid profile '{value}'. Valid profiles: {valid_profiles}"
        )


@dataclass
class DiffBoundary:
    """Configuration for diff size limits"""

    max_lines_changed: Optional[int] = 500
    max_files_changed: Optional[int] = None
    max_lines_per_file: Optional[int] = None

    def exceeds(self, lines: int, files: int = 1, lines_per_file: int = 0) -> bool:
        """
        Check if proposed changes exceed boundaries

        Args:
            lines: Total lines changed
            files: Number of files modified
            lines_per_file: Maximum lines in any single file

        Returns:
            True if any boundary is exceeded
        """
        if self.max_lines_changed is not None and lines > self.max_lines_changed:
            return True
        if self.max_files_changed is not None and files > self.max_files_changed:
            return True
        if self.max_lines_per_file is not None and lines_per_file > self.max_lines_per_file:
            return True
        return False

    def get_exceeded_message(self, lines: int, files: int = 1, lines_per_file: int = 0) -> str:
        """Get a human-readable message about which boundary was exceeded"""
        messages = []
        if self.max_lines_changed is not None and lines > self.max_lines_changed:
            messages.append(f"Total lines ({lines}) exceeds max ({self.max_lines_changed})")
        if self.max_files_changed is not None and files > self.max_files_changed:
            messages.append(f"Files changed ({files}) exceeds max ({self.max_files_changed})")
        if self.max_lines_per_file is not None and lines_per_file > self.max_lines_per_file:
            messages.append(
                f"Lines per file ({lines_per_file}) exceeds max ({self.max_lines_per_file})"
            )
        return "; ".join(messages) if messages else "No boundaries exceeded"


@dataclass
class ProfileConfig:
    """Configuration values for a specific safety profile"""

    profile_type: ProfileType

    # Network access controls
    network_allowed: bool  # Auxiliary network calls (web search, etc.)
    ai_network_allowed: bool  # AI provider calls (always True for all profiles)

    # Diff size limits
    max_diff_lines: Optional[int]  # Maximum total lines changed (None = unlimited)

    # Repair loop limits
    max_repair_loops: int  # Maximum iterations for fix attempts

    # Behavior controls
    require_tests: bool  # Require tests to pass before applying changes
    interactive_prompts: bool  # Allow interactive prompts
    fail_fast: bool  # Exit immediately on error (for CI)
    audit_logging: bool  # Write structured audit logs

    # Safety controls
    require_acknowledgment: bool  # Require explicit confirmation (for yolo)
    allowlist_enabled: bool  # Enforce command allowlist

    @property
    def diff_boundary(self) -> DiffBoundary:
        """Get DiffBoundary configuration for this profile"""
        return DiffBoundary(
            max_lines_changed=self.max_diff_lines,
            max_files_changed=None,  # Not configurable per profile yet
            max_lines_per_file=None,  # Not configurable per profile yet
        )


# Pre-defined profile configurations
PROFILE_CONFIGS = {
    ProfileType.SAFE: ProfileConfig(
        profile_type=ProfileType.SAFE,
        network_allowed=False,  # Block auxiliary network (web search)
        ai_network_allowed=True,  # AI calls always allowed
        max_diff_lines=500,  # Conservative limit
        max_repair_loops=3,  # Limited iterations
        require_tests=True,  # Must pass tests
        interactive_prompts=True,  # Allow prompts
        fail_fast=False,  # Continue on non-critical errors
        audit_logging=False,  # No audit log by default
        require_acknowledgment=False,  # No extra confirmation
        allowlist_enabled=True,  # Enforce allowlist
    ),
    ProfileType.CI: ProfileConfig(
        profile_type=ProfileType.CI,
        network_allowed=True,  # Allow network for CI
        ai_network_allowed=True,  # AI calls always allowed
        max_diff_lines=500,  # Same limit as safe
        max_repair_loops=3,  # Same as safe
        require_tests=True,  # Must pass tests
        interactive_prompts=False,  # No prompts in CI
        fail_fast=True,  # Exit on error
        audit_logging=True,  # Always log in CI
        require_acknowledgment=False,  # No confirmation needed
        allowlist_enabled=False,  # No allowlist in CI
    ),
    ProfileType.YOLO: ProfileConfig(
        profile_type=ProfileType.YOLO,
        network_allowed=True,  # Full network access
        ai_network_allowed=True,  # AI calls always allowed
        max_diff_lines=None,  # No limits
        max_repair_loops=10,  # Extended iterations
        require_tests=False,  # Tests optional
        interactive_prompts=True,  # Allow prompts
        fail_fast=False,  # Continue on errors
        audit_logging=True,  # Log for accountability
        require_acknowledgment=True,  # Require explicit confirmation
        allowlist_enabled=False,  # No restrictions
    ),
}


def get_profile_config(profile_type: ProfileType) -> ProfileConfig:
    """
    Get the configuration for a specific profile

    Args:
        profile_type: The profile type to get configuration for

    Returns:
        ProfileConfig for the specified profile
    """
    return PROFILE_CONFIGS[profile_type]


def is_ci_environment() -> bool:
    """
    Detect if running in a CI/CD environment

    Checks common CI environment variables:
    - CI (generic)
    - GITHUB_ACTIONS
    - GITLAB_CI
    - JENKINS_URL
    - CIRCLECI
    - TRAVIS
    - AZURE_PIPELINES

    Returns:
        True if CI environment detected
    """
    ci_env_vars = [
        "CI",
        "GITHUB_ACTIONS",
        "GITLAB_CI",
        "JENKINS_URL",
        "CIRCLECI",
        "TRAVIS",
        "BUILD_ID",  # Jenkins/Azure
        "TF_BUILD",  # Azure Pipelines
        "BUILDKITE",
        "CODEBUILD_BUILD_ID",  # AWS CodeBuild
    ]
    return any(os.environ.get(var) for var in ci_env_vars)


def is_interactive_terminal() -> bool:
    """
    Check if running in an interactive terminal

    Returns:
        True if stdin and stdout are TTYs
    """
    return sys.stdin.isatty() and sys.stdout.isatty()


def get_default_profile() -> ProfileType:
    """
    Get the default profile based on environment

    - In CI environment: returns CI profile
    - In interactive terminal: returns SAFE profile
    - Otherwise: returns SAFE profile

    Returns:
        Default ProfileType for the current environment
    """
    if is_ci_environment():
        return ProfileType.CI
    return ProfileType.SAFE


def validate_profile_name(name: str) -> tuple:
    """
    Validate a profile name and return the ProfileType if valid

    Args:
        name: Profile name to validate

    Returns:
        Tuple of (is_valid: bool, profile_or_error: ProfileType | str)
    """
    try:
        profile = ProfileType.from_string(name)
        return (True, profile)
    except ValueError as e:
        return (False, str(e))
