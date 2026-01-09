"""Default exclusion patterns for artifact cleanup and package building.

These patterns define which files/directories should be excluded from:
- Package distributions (PyPI)
- Cleanup operations
- Build artifacts

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
    SECURITY_EXCLUSIONS
    + OS_ARTIFACT_EXCLUSIONS
    + DEV_TOOLING_EXCLUSIONS
    + TEST_EXCLUSIONS
)

# All exclusions including deep clean
ALL_EXCLUSIONS: list[str] = DEFAULT_EXCLUSIONS + DEEP_CLEAN_EXCLUSIONS


def get_exclusions(deep: bool = False, custom: list[str] | None = None) -> list[str]:
    """Get exclusion patterns based on configuration.

    Args:
        deep: Include deep clean patterns (build artifacts, caches)
        custom: Additional custom patterns to include

    Returns:
        Combined list of exclusion patterns
    """
    patterns = list(DEFAULT_EXCLUSIONS)
    if deep:
        patterns.extend(DEEP_CLEAN_EXCLUSIONS)
    if custom:
        patterns.extend(custom)
    return patterns
