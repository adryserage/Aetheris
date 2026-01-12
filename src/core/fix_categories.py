"""
Fix category definitions for targeted fixing (v2.11)
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class FixCategory:
    """Defines a category for targeted fixing"""

    name: str
    agent_source: str
    issue_types: List[str]
    description: str = ""


@dataclass
class CategoryProgress:
    """Tracks progress of fixes per category"""

    category: str
    total: int = 0
    fixed: int = 0
    skipped: int = 0
    failed: int = 0

    @property
    def pending(self) -> int:
        return self.total - self.fixed - self.skipped - self.failed

    @property
    def progress_percent(self) -> float:
        if self.total == 0:
            return 100.0
        return (self.fixed + self.skipped + self.failed) / self.total * 100


# Default category mappings
CATEGORY_MAPPINGS: Dict[str, FixCategory] = {
    "security": FixCategory(
        name="security",
        agent_source="SecurityAnalysisAgent",
        issue_types=["SecurityIssue", "Vulnerability", "injection", "xss", "hardcoded_secret"],
        description="Security vulnerabilities and risks",
    ),
    "performance": FixCategory(
        name="performance",
        agent_source="PerformanceAnalysisAgent",
        issue_types=["PerformanceIssue", "n_squared", "n_plus_one", "memory_leak", "blocking_async"],
        description="Performance issues and anti-patterns",
    ),
    "compliance": FixCategory(
        name="compliance",
        agent_source="DataPrivacyAgent",
        issue_types=["PrivacyViolation", "pii_logging", "missing_encryption", "gdpr", "hipaa"],
        description="Privacy and compliance violations",
    ),
    "code_quality": FixCategory(
        name="code_quality",
        agent_source="CodeAnalysisExpert",
        issue_types=["QualityIssue", "maintainability", "complexity", "duplication"],
        description="Code quality and maintainability issues",
    ),
    "architecture": FixCategory(
        name="architecture",
        agent_source="ArchitectAnalysisAgent",
        issue_types=["ArchitectureIssue", "circular_dependency", "coupling", "cohesion"],
        description="Architecture and design issues",
    ),
    "type_safety": FixCategory(
        name="type_safety",
        agent_source="TypeSafetyAgent",
        issue_types=["TypeSafetyIssue", "any_usage", "unsafe_cast", "type_ignore"],
        description="Type safety issues",
    ),
    "api_contract": FixCategory(
        name="api_contract",
        agent_source="APIContractAgent",
        issue_types=["APIContractViolation", "rest_violation", "breaking_change"],
        description="API contract violations",
    ),
    "vulnerability": FixCategory(
        name="vulnerability",
        agent_source="DependencyVulnerabilityAgent",
        issue_types=["DependencyVulnerability", "CVE", "outdated_package"],
        description="Dependency vulnerabilities",
    ),
}


class CategoryFilter:
    """Filters issues by category for targeted fixing"""

    def __init__(self, categories: Optional[List[str]] = None):
        """
        Initialize category filter

        Args:
            categories: List of category names to include. None = all categories.
        """
        self.categories = categories
        self._mappings = CATEGORY_MAPPINGS

    def get_category_for_issue(self, issue: Any) -> Optional[str]:
        """
        Determine the category for an issue based on its type/attributes

        Args:
            issue: Issue object (dict or dataclass)

        Returns:
            Category name or None if not categorizable
        """
        # Get issue type from various formats
        issue_type = None
        if isinstance(issue, dict):
            issue_type = issue.get("type") or issue.get("issue_type") or issue.get("__class__")
        elif hasattr(issue, "__class__"):
            issue_type = issue.__class__.__name__
        elif hasattr(issue, "issue_type"):
            issue_type = issue.issue_type

        if not issue_type:
            return None

        # Find matching category
        for cat_name, cat_def in self._mappings.items():
            if issue_type in cat_def.issue_types:
                return cat_name
            # Also check agent source
            if hasattr(issue, "source_agent") and issue.source_agent == cat_def.agent_source:
                return cat_name

        return None

    def should_include(self, issue: Any) -> bool:
        """
        Check if an issue should be included based on category filter

        Args:
            issue: Issue object

        Returns:
            True if issue should be included
        """
        if self.categories is None:
            return True

        category = self.get_category_for_issue(issue)
        if category is None:
            # Include uncategorized issues if "other" is in filter
            return "other" in self.categories
        return category in self.categories

    def filter_issues(self, issues: List[Any]) -> tuple:
        """
        Filter issues by category

        Args:
            issues: List of issues to filter

        Returns:
            Tuple of (included_issues, excluded_issues)
        """
        included = []
        excluded = []
        for issue in issues:
            if self.should_include(issue):
                included.append(issue)
            else:
                excluded.append(issue)
        return included, excluded


def get_categories_for_compliance(framework: str) -> List[str]:
    """Get relevant categories for a compliance framework"""
    compliance_mappings = {
        "gdpr": ["compliance", "security", "type_safety"],
        "hipaa": ["compliance", "security", "type_safety"],
        "pci_dss": ["compliance", "security", "vulnerability"],
        "ccpa": ["compliance", "security"],
    }
    return compliance_mappings.get(framework.lower(), ["compliance"])


def list_categories() -> List[FixCategory]:
    """List all available fix categories"""
    return list(CATEGORY_MAPPINGS.values())


def get_category_descriptions() -> str:
    """Get formatted category descriptions for CLI help"""
    lines = ["Available fix categories:"]
    for cat in CATEGORY_MAPPINGS.values():
        lines.append(f"  {cat.name}: {cat.description}")
    return "\n".join(lines)
