"""Default exclusion patterns for artifact cleanup and package building.

IMPORTANT: This file defines TWO distinct sets of patterns:

1. PACKAGE EXCLUSIONS (get_exclusions):
   - Files to EXCLUDE from PyPI packages
   - These files should NOT be deleted, just excluded from distribution
   - Includes: .env, .git/, tests/, specs/, etc.

2. CLEANUP PATTERNS (get_cleanup_patterns):
   - Files that are SAFE to DELETE from disk
   - Only temporary/cache files that can be regenerated
   - Includes: __pycache__/, *.pyc, .DS_Store, etc.

Pattern syntax:
- Use ** for recursive directory matching
- Use * for single-level wildcard
- Patterns are case-sensitive
"""

# Security-sensitive files that should NEVER be in packages
SECURITY_EXCLUSIONS: list[str] = [
    # Environment files (except templates)
    ".env",
    ".env.*",
    "!.env.example",  # Whitelist template
    "!.env.template",
    # Git
    ".git/",
    ".gitconfig",
    # SSH and credentials
    ".ssh/",
    "*.pem",
    "*.key",
    "id_rsa*",
    "id_ed25519*",
    # Config files with potential secrets
    "secrets.json",
    "secrets.yaml",
    "secrets.yml",
    "credentials.json",
    ".secrets",
    # IDE configs that may contain tokens
    ".vscode/settings.json",
    ".idea/",
]

# OS-generated artifacts
OS_ARTIFACT_EXCLUSIONS: list[str] = [
    # macOS
    ".DS_Store",
    ".AppleDouble",
    ".LSOverride",
    "._*",
    # Windows
    "Thumbs.db",
    "Thumbs.db:encryptable",
    "ehthumbs.db",
    "ehthumbs_vista.db",
    "desktop.ini",
    # Linux
    "*~",
    ".directory",
    ".Trash-*",
]

# Development tooling files not needed in production
DEV_TOOLING_EXCLUSIONS: list[str] = [
    # TypeScript/JavaScript
    "tsconfig.tsbuildinfo",
    "*.tsbuildinfo",
    ".eslintrc*",
    ".prettierrc*",
    "eslint.config.js",
    "prettier.config.js",
    ".babelrc*",
    "babel.config.*",
    # Python
    ".pylintrc",
    ".flake8",
    "pyrightconfig.json",
    ".mypy.ini",
    "mypy.ini",
    ".ruff.toml",
    "ruff.toml",
    # Editor configs
    ".editorconfig",
    # Docker development
    "docker-compose.dev.yml",
    "docker-compose.override.yml",
    "Dockerfile.dev",
    # Debug configs
    "launch.json",
    ".vscode/launch.json",
]

# Test files and directories
TEST_EXCLUSIONS: list[str] = [
    # Test directories
    "tests/",
    "test/",
    "__tests__/",
    "spec/",
    "specs/",
    # Test files
    "*_test.py",
    "test_*.py",
    "*_spec.py",
    "spec_*.py",
    "*.test.js",
    "*.test.ts",
    "*.spec.js",
    "*.spec.ts",
    # Test configs
    "pytest.ini",
    "conftest.py",
    "jest.config.*",
    "vitest.config.*",
    ".coveragerc",
    "coverage.xml",
    "htmlcov/",
    ".coverage",
    ".pytest_cache/",
    # Mocks and fixtures
    "mocks/",
    "__mocks__/",
    "fixtures/",
    "__fixtures__/",
]

# Build artifacts (for deep clean only)
DEEP_CLEAN_EXCLUSIONS: list[str] = [
    # Python build artifacts
    "dist/",
    "build/",
    "*.egg-info/",
    "*.egg",
    "*.whl",
    "MANIFEST",
    # Python cache
    "__pycache__/",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".Python",
    # Virtual environments
    "venv/",
    ".venv/",
    "env/",
    ".env/",
    "ENV/",
    # Node.js
    "node_modules/",
    ".npm/",
    # IDE/Editor
    ".idea/",
    "*.swp",
    "*.swo",
    "*~",
    # Logs
    "*.log",
    "logs/",
    # Temporary files
    "tmp/",
    "temp/",
    ".tmp/",
    ".temp/",
]

# Combined default exclusions (without deep clean)
DEFAULT_EXCLUSIONS: list[str] = (
    SECURITY_EXCLUSIONS + OS_ARTIFACT_EXCLUSIONS + DEV_TOOLING_EXCLUSIONS + TEST_EXCLUSIONS
)

# All exclusions including deep clean
ALL_EXCLUSIONS: list[str] = DEFAULT_EXCLUSIONS + DEEP_CLEAN_EXCLUSIONS


def get_exclusions(deep: bool = False, custom: list[str] | None = None) -> list[str]:
    """Get exclusion patterns for PACKAGE BUILDING (PyPI).

    WARNING: These patterns are for EXCLUDING files from packages,
    NOT for deleting files. Use get_cleanup_patterns() for cleanup.

    Args:
        deep: Include deep clean patterns (build artifacts, caches)
        custom: Additional custom patterns to include

    Returns:
        Combined list of exclusion patterns for package building
    """
    patterns = list(DEFAULT_EXCLUSIONS)
    if deep:
        patterns.extend(DEEP_CLEAN_EXCLUSIONS)
    if custom:
        patterns.extend(custom)
    return patterns


# =============================================================================
# CLEANUP PATTERNS - Files that are SAFE to DELETE
# =============================================================================
# These patterns define files/directories that can be safely deleted
# because they are temporary, cached, or can be regenerated.
#
# NEVER include in cleanup patterns:
# - .git/ (version control history)
# - .env (secrets and configuration)
# - tests/, specs/ (source code)
# - src/, lib/ (source code)
# - Any user data or configuration
# =============================================================================

# OS-generated temporary files (safe to delete)
CLEANUP_OS_ARTIFACTS: list[str] = [
    # macOS
    ".DS_Store",
    ".AppleDouble",
    ".LSOverride",
    "._*",
    # Windows
    "Thumbs.db",
    "Thumbs.db:encryptable",
    "ehthumbs.db",
    "ehthumbs_vista.db",
    "desktop.ini",
    # Linux
    "*~",
    ".directory",
    ".Trash-*",
]

# Python cache files (safe to delete - regenerated on import)
CLEANUP_PYTHON_CACHE: list[str] = [
    "__pycache__/",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".Python",
    ".pytest_cache/",
    ".mypy_cache/",
    ".ruff_cache/",
    ".coverage",
    "htmlcov/",
    "coverage.xml",
    ".tox/",
    ".nox/",
]

# Editor/IDE temporary files (safe to delete)
CLEANUP_EDITOR_TEMP: list[str] = [
    "*.swp",
    "*.swo",
    "*.bak",
    "*.tmp",
    "*~",
]

# Build artifacts for deep cleanup (safe to delete - regenerated by build)
CLEANUP_BUILD_ARTIFACTS: list[str] = [
    # Python build
    "dist/",
    "build/",
    "*.egg-info/",
    "*.egg",
    "*.whl",
    "MANIFEST",
    # TypeScript/JavaScript build info
    "*.tsbuildinfo",
    "tsconfig.tsbuildinfo",
]

# Log files (safe to delete)
CLEANUP_LOGS: list[str] = [
    "*.log",
    "logs/",
    "*.log.*",
]

# Temporary directories (safe to delete)
CLEANUP_TEMP_DIRS: list[str] = [
    "tmp/",
    "temp/",
    ".tmp/",
    ".temp/",
    ".cache/",
]

# Default cleanup patterns (safe for regular cleanup)
DEFAULT_CLEANUP_PATTERNS: list[str] = (
    CLEANUP_OS_ARTIFACTS + CLEANUP_PYTHON_CACHE + CLEANUP_EDITOR_TEMP + CLEANUP_LOGS
)

# Deep cleanup patterns (includes build artifacts)
DEEP_CLEANUP_PATTERNS: list[str] = (
    DEFAULT_CLEANUP_PATTERNS + CLEANUP_BUILD_ARTIFACTS + CLEANUP_TEMP_DIRS
)


def get_cleanup_patterns(deep: bool = False, custom: list[str] | None = None) -> list[str]:
    """Get patterns for files that are SAFE TO DELETE.

    This function returns patterns for temporary/cache files that can be
    safely deleted because they are regenerated automatically.

    IMPORTANT: This is different from get_exclusions() which returns
    patterns for files to exclude from packages (not delete).

    Args:
        deep: Include build artifacts (dist/, build/, *.egg-info/)
        custom: Additional custom patterns to include

    Returns:
        List of patterns for files safe to delete
    """
    patterns = list(DEFAULT_CLEANUP_PATTERNS)
    if deep:
        patterns.extend(CLEANUP_BUILD_ARTIFACTS)
        patterns.extend(CLEANUP_TEMP_DIRS)
    if custom:
        patterns.extend(custom)
    return patterns
