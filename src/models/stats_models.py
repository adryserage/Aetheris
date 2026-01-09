"""
Statistics and ROI models for Aetheris analysis tracking.

This module provides dataclasses for storing analysis results,
calculating ROI metrics, and generating statistics reports.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class ROIParameters:
    """Configurable ROI calculation parameters."""

    hourly_rate: float = 75.0  # Developer hourly rate (USD)
    time_per_critical: float = 4.0  # Hours to fix critical issue manually
    time_per_high: float = 2.0  # Hours for high severity
    time_per_medium: float = 1.0  # Hours for medium severity
    time_per_low: float = 0.5  # Hours for low severity
    incident_cost: float = 5000.0  # Cost per production incident


@dataclass
class AnalysisRecord:
    """A single analysis run record."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    project_path: str = ""
    duration_seconds: float = 0.0
    files_scanned: int = 0
    issues_by_severity: dict[str, int] = field(
        default_factory=lambda: {"critical": 0, "high": 0, "medium": 0, "low": 0}
    )
    issues_by_category: dict[str, int] = field(
        default_factory=lambda: {"security": 0, "performance": 0, "quality": 0, "debt": 0}
    )
    agents_used: list[str] = field(default_factory=list)
    ai_provider: str = ""
    version: str = ""

    @property
    def total_issues(self) -> int:
        """Calculate total issues from severity breakdown."""
        return sum(self.issues_by_severity.values())

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "project_path": self.project_path,
            "duration_seconds": self.duration_seconds,
            "files_scanned": self.files_scanned,
            "issues_by_severity": self.issues_by_severity,
            "issues_by_category": self.issues_by_category,
            "agents_used": self.agents_used,
            "ai_provider": self.ai_provider,
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AnalysisRecord":
        """Create from dictionary."""
        timestamp = data.get("timestamp", "")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            timestamp=timestamp,
            project_path=data.get("project_path", ""),
            duration_seconds=data.get("duration_seconds", 0.0),
            files_scanned=data.get("files_scanned", 0),
            issues_by_severity=data.get(
                "issues_by_severity", {"critical": 0, "high": 0, "medium": 0, "low": 0}
            ),
            issues_by_category=data.get(
                "issues_by_category", {"security": 0, "performance": 0, "quality": 0, "debt": 0}
            ),
            agents_used=data.get("agents_used", []),
            ai_provider=data.get("ai_provider", ""),
            version=data.get("version", ""),
        )


@dataclass
class StatisticsAggregate:
    """Aggregated statistics from multiple analysis runs."""

    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    total_analyses: int = 0
    total_files_scanned: int = 0
    total_issues_detected: int = 0
    issues_by_severity: dict[str, int] = field(
        default_factory=lambda: {"critical": 0, "high": 0, "medium": 0, "low": 0}
    )
    issues_by_category: dict[str, int] = field(
        default_factory=lambda: {"security": 0, "performance": 0, "quality": 0, "debt": 0}
    )
    average_duration: float = 0.0
    average_issues_per_analysis: float = 0.0

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        return {
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "total_analyses": self.total_analyses,
            "total_files_scanned": self.total_files_scanned,
            "total_issues_detected": self.total_issues_detected,
            "issues_by_severity": self.issues_by_severity,
            "issues_by_category": self.issues_by_category,
            "average_duration": self.average_duration,
            "average_issues_per_analysis": self.average_issues_per_analysis,
        }


@dataclass
class ROICalculation:
    """ROI metrics based on detected issues."""

    hours_saved: float = 0.0
    cost_saved: float = 0.0
    currency: str = "USD"
    incidents_avoided: int = 0
    incident_cost_avoided: float = 0.0
    parameters: ROIParameters = field(default_factory=ROIParameters)

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        return {
            "hours_saved": round(self.hours_saved, 2),
            "cost_saved": round(self.cost_saved, 2),
            "currency": self.currency,
            "incidents_avoided": self.incidents_avoided,
            "incident_cost_avoided": round(self.incident_cost_avoided, 2),
        }


@dataclass
class CategoryMetrics:
    """Metrics for a specific issue category."""

    category: str = ""
    total_issues: int = 0
    severity_breakdown: dict[str, int] = field(
        default_factory=lambda: {"critical": 0, "high": 0, "medium": 0, "low": 0}
    )
    trend: str = "stable"  # "improving", "stable", "regressing"
    change_from_previous: int = 0

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        return {
            "category": self.category,
            "total_issues": self.total_issues,
            "severity_breakdown": self.severity_breakdown,
            "trend": self.trend,
            "change_from_previous": self.change_from_previous,
        }


@dataclass
class ExportReport:
    """Formatted statistics export."""

    generated_at: datetime = field(default_factory=datetime.now)
    period: str = "all"
    format: str = "json"
    summary: Optional[StatisticsAggregate] = None
    roi: Optional[ROICalculation] = None
    by_category: list[CategoryMetrics] = field(default_factory=list)
    records: list[AnalysisRecord] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        return {
            "generated_at": self.generated_at.isoformat(),
            "period": self.period,
            "summary": self.summary.to_dict() if self.summary else None,
            "roi": self.roi.to_dict() if self.roi else None,
            "by_category": [c.to_dict() for c in self.by_category],
            "records": [r.to_dict() for r in self.records],
        }


@dataclass
class StatisticsStorage:
    """Root structure for statistics storage file."""

    version: str = "1.0"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    records: list[AnalysisRecord] = field(default_factory=list)
    roi_parameters: ROIParameters = field(default_factory=ROIParameters)

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dictionary."""
        return {
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "records": [r.to_dict() for r in self.records],
            "roi_parameters": {
                "hourly_rate": self.roi_parameters.hourly_rate,
                "time_per_critical": self.roi_parameters.time_per_critical,
                "time_per_high": self.roi_parameters.time_per_high,
                "time_per_medium": self.roi_parameters.time_per_medium,
                "time_per_low": self.roi_parameters.time_per_low,
                "incident_cost": self.roi_parameters.incident_cost,
            },
        }

    @classmethod
    def from_dict(cls, data: dict) -> "StatisticsStorage":
        """Create from dictionary."""
        roi_params_data = data.get("roi_parameters", {})
        roi_params = ROIParameters(
            hourly_rate=roi_params_data.get("hourly_rate", 75.0),
            time_per_critical=roi_params_data.get("time_per_critical", 4.0),
            time_per_high=roi_params_data.get("time_per_high", 2.0),
            time_per_medium=roi_params_data.get("time_per_medium", 1.0),
            time_per_low=roi_params_data.get("time_per_low", 0.5),
            incident_cost=roi_params_data.get("incident_cost", 5000.0),
        )

        created_at = data.get("created_at", "")
        if isinstance(created_at, str) and created_at:
            created_at = datetime.fromisoformat(created_at)
        else:
            created_at = datetime.now()

        updated_at = data.get("updated_at", "")
        if isinstance(updated_at, str) and updated_at:
            updated_at = datetime.fromisoformat(updated_at)
        else:
            updated_at = datetime.now()

        records = [AnalysisRecord.from_dict(r) for r in data.get("records", [])]

        return cls(
            version=data.get("version", "1.0"),
            created_at=created_at,
            updated_at=updated_at,
            records=records,
            roi_parameters=roi_params,
        )
