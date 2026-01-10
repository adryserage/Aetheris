"""
Statistics configuration for Aetheris.

Defines default paths and ROI calculation parameters.
"""

from pathlib import Path

# Storage paths
GLOBAL_STATS_DIR = Path.home() / ".aetheris"
GLOBAL_STATS_FILE = GLOBAL_STATS_DIR / "statistics.json"
LOCAL_STATS_FILE = "aetheris-stats.json"

# Default ROI parameters
DEFAULT_HOURLY_RATE = 75.0  # USD
DEFAULT_INCIDENT_COST = 5000.0  # USD per production incident

# Time estimates per severity (hours to fix manually)
TIME_PER_SEVERITY = {
    "critical": 4.0,
    "high": 2.0,
    "medium": 1.0,
    "low": 0.5,
}

# Issue categories
ISSUE_CATEGORIES = ["security", "performance", "quality", "debt"]

# Period options
PERIOD_DAYS = {
    "week": 7,
    "month": 30,
    "all": None,  # No filter
}

# Export formats
EXPORT_FORMATS = ["json", "csv", "md"]
