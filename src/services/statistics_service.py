"""
Statistics service for Aetheris analysis tracking and ROI calculation.

Provides functionality for:
- Recording analysis results
- Aggregating statistics across analyses
- Calculating ROI metrics
- Exporting to JSON, CSV, and Markdown
- Filtering by time period
- Category breakdown analysis
"""

import csv
import json
import logging
from datetime import datetime, timedelta
from io import StringIO
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.config.stats_config import (
    EXPORT_FORMATS,
    GLOBAL_STATS_DIR,
    GLOBAL_STATS_FILE,
    ISSUE_CATEGORIES,
    LOCAL_STATS_FILE,
    PERIOD_DAYS,
)
from src.models.stats_models import (
    AnalysisRecord,
    CategoryMetrics,
    ExportReport,
    ROICalculation,
    ROIParameters,
    StatisticsAggregate,
    StatisticsStorage,
)

logger = logging.getLogger(__name__)


class StatisticsService:
    """Service for managing analysis statistics and ROI calculations."""

    def __init__(self, project_path: Optional[Path] = None, use_global: bool = False):
        """
        Initialize statistics service.

        Args:
            project_path: Path to project directory (for local stats)
            use_global: Whether to use global stats instead of project-local
        """
        self.console = Console()
        self.use_global = use_global
        self.project_path = project_path or Path.cwd()
        self._storage: Optional[StatisticsStorage] = None

    @property
    def storage_path(self) -> Path:
        """Get the appropriate storage file path."""
        if self.use_global:
            return GLOBAL_STATS_FILE
        return self.project_path / LOCAL_STATS_FILE

    def _ensure_storage_dir(self) -> None:
        """Ensure storage directory exists."""
        if self.use_global:
            GLOBAL_STATS_DIR.mkdir(parents=True, exist_ok=True)

    def load_storage(self) -> StatisticsStorage:
        """Load statistics storage from file."""
        if self._storage is not None:
            return self._storage

        storage_path = self.storage_path

        if not storage_path.exists():
            logger.info(f"No statistics file found at {storage_path}, creating new storage")
            self._storage = StatisticsStorage()
            return self._storage

        try:
            with open(storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._storage = StatisticsStorage.from_dict(data)
            logger.info(f"Loaded {len(self._storage.records)} records from {storage_path}")
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Statistics file corrupted: {e}. Creating new storage.")
            self._storage = StatisticsStorage()

        return self._storage

    def save_storage(self) -> None:
        """Save statistics storage to file."""
        if self._storage is None:
            return

        self._ensure_storage_dir()
        self._storage.updated_at = datetime.now()

        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(self._storage.to_dict(), f, indent=2)
            logger.info(f"Saved statistics to {self.storage_path}")
        except OSError as e:
            logger.error(f"Failed to save statistics: {e}")
            raise

    def record_analysis(self, record: AnalysisRecord) -> None:
        """
        Record a new analysis result.

        Args:
            record: The analysis record to store
        """
        storage = self.load_storage()
        storage.records.append(record)
        self.save_storage()
        logger.info(f"Recorded analysis {record.id} with {record.total_issues} issues")

    def filter_by_period(
        self, records: list[AnalysisRecord], period: str = "all"
    ) -> list[AnalysisRecord]:
        """
        Filter records by time period.

        Args:
            records: List of records to filter
            period: Period filter (week, month, all)

        Returns:
            Filtered list of records
        """
        days = PERIOD_DAYS.get(period)
        if days is None:
            return records

        cutoff = datetime.now() - timedelta(days=days)
        return [r for r in records if r.timestamp >= cutoff]

    def aggregate_statistics(
        self, period: str = "all"
    ) -> tuple[StatisticsAggregate, list[AnalysisRecord]]:
        """
        Calculate aggregated statistics.

        Args:
            period: Time period filter (week, month, all)

        Returns:
            Tuple of (aggregate stats, filtered records)
        """
        storage = self.load_storage()
        records = self.filter_by_period(storage.records, period)

        if not records:
            return StatisticsAggregate(), []

        # Calculate aggregates
        total_analyses = len(records)
        total_files = sum(r.files_scanned for r in records)
        total_duration = sum(r.duration_seconds for r in records)

        # Aggregate by severity
        issues_by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for r in records:
            for severity, count in r.issues_by_severity.items():
                issues_by_severity[severity] = issues_by_severity.get(severity, 0) + count

        # Aggregate by category
        issues_by_category = {cat: 0 for cat in ISSUE_CATEGORIES}
        for r in records:
            for category, count in r.issues_by_category.items():
                if category in issues_by_category:
                    issues_by_category[category] += count

        total_issues = sum(issues_by_severity.values())

        # Find date range
        timestamps = [r.timestamp for r in records]
        period_start = min(timestamps)
        period_end = max(timestamps)

        aggregate = StatisticsAggregate(
            period_start=period_start,
            period_end=period_end,
            total_analyses=total_analyses,
            total_files_scanned=total_files,
            total_issues_detected=total_issues,
            issues_by_severity=issues_by_severity,
            issues_by_category=issues_by_category,
            average_duration=total_duration / total_analyses if total_analyses > 0 else 0,
            average_issues_per_analysis=total_issues / total_analyses if total_analyses > 0 else 0,
        )

        return aggregate, records

    def calculate_roi(
        self, aggregate: StatisticsAggregate, params: Optional[ROIParameters] = None
    ) -> ROICalculation:
        """
        Calculate ROI metrics from aggregate statistics.

        Args:
            aggregate: Aggregated statistics
            params: ROI calculation parameters (uses defaults if not provided)

        Returns:
            ROI calculation result
        """
        if params is None:
            storage = self.load_storage()
            params = storage.roi_parameters

        # Calculate hours saved
        hours_saved = (
            aggregate.issues_by_severity.get("critical", 0) * params.time_per_critical
            + aggregate.issues_by_severity.get("high", 0) * params.time_per_high
            + aggregate.issues_by_severity.get("medium", 0) * params.time_per_medium
            + aggregate.issues_by_severity.get("low", 0) * params.time_per_low
        )

        # Calculate cost saved
        cost_saved = hours_saved * params.hourly_rate

        # Estimate incidents avoided (critical + high security issues)
        security_critical = min(
            aggregate.issues_by_severity.get("critical", 0),
            aggregate.issues_by_category.get("security", 0),
        )
        incidents_avoided = security_critical + aggregate.issues_by_severity.get("critical", 0) // 2
        incident_cost_avoided = incidents_avoided * params.incident_cost

        return ROICalculation(
            hours_saved=hours_saved,
            cost_saved=cost_saved,
            currency="USD",
            incidents_avoided=incidents_avoided,
            incident_cost_avoided=incident_cost_avoided,
            parameters=params,
        )

    def get_category_breakdown(
        self, records: list[AnalysisRecord], previous_records: Optional[list[AnalysisRecord]] = None
    ) -> list[CategoryMetrics]:
        """
        Get metrics breakdown by category.

        Args:
            records: Current period records
            previous_records: Previous period records for trend calculation

        Returns:
            List of category metrics
        """
        categories = []

        for category in ISSUE_CATEGORIES:
            # Current period totals
            total = sum(r.issues_by_category.get(category, 0) for r in records)

            # Severity breakdown for this category (estimated distribution)
            severity_breakdown = {"critical": 0, "high": 0, "medium": 0, "low": 0}
            for r in records:
                cat_issues = r.issues_by_category.get(category, 0)
                if cat_issues > 0 and r.total_issues > 0:
                    ratio = cat_issues / r.total_issues
                    for sev, count in r.issues_by_severity.items():
                        severity_breakdown[sev] += int(count * ratio)

            # Calculate trend
            trend = "stable"
            change = 0
            if previous_records:
                prev_total = sum(r.issues_by_category.get(category, 0) for r in previous_records)
                change = total - prev_total
                if change < -2:
                    trend = "improving"
                elif change > 2:
                    trend = "regressing"

            categories.append(
                CategoryMetrics(
                    category=category,
                    total_issues=total,
                    severity_breakdown=severity_breakdown,
                    trend=trend,
                    change_from_previous=change,
                )
            )

        return categories

    def compare_periods(
        self, current_period: str = "week", previous_period: str = "month"
    ) -> tuple[StatisticsAggregate, StatisticsAggregate, dict]:
        """
        Compare statistics between two periods.

        Args:
            current_period: Current time period
            previous_period: Previous time period for comparison

        Returns:
            Tuple of (current stats, previous stats, deltas)
        """
        current_agg, _ = self.aggregate_statistics(current_period)
        previous_agg, _ = self.aggregate_statistics(previous_period)

        # Calculate deltas
        deltas = {
            "analyses": current_agg.total_analyses - previous_agg.total_analyses,
            "files": current_agg.total_files_scanned - previous_agg.total_files_scanned,
            "issues": current_agg.total_issues_detected - previous_agg.total_issues_detected,
            "avg_duration": current_agg.average_duration - previous_agg.average_duration,
        }

        # Calculate percentage changes
        if previous_agg.total_issues_detected > 0:
            deltas["issues_pct"] = (
                (current_agg.total_issues_detected - previous_agg.total_issues_detected)
                / previous_agg.total_issues_detected
                * 100
            )
        else:
            deltas["issues_pct"] = 0

        return current_agg, previous_agg, deltas

    def format_dashboard(self, period: str = "all") -> str:
        """
        Format statistics as a Rich dashboard.

        Args:
            period: Time period filter

        Returns:
            Formatted dashboard string (also prints to console)
        """
        aggregate, records = self.aggregate_statistics(period)

        if not records:
            msg = (
                "[yellow]No analysis data available.[/yellow]\n\n"
                "Run [bold]aetheris analysis[/bold] to generate statistics."
            )
            self.console.print(Panel(msg, title="📊 Aetheris Statistics", border_style="yellow"))
            return "No data available"

        roi = self.calculate_roi(aggregate)
        categories = self.get_category_breakdown(records)

        # Header
        period_label = {"week": "Last 7 days", "month": "Last 30 days", "all": "All time"}.get(
            period, period
        )

        # Summary Panel
        summary_text = Text()
        summary_text.append("📈 Total Analyses: ", style="bold")
        summary_text.append(f"{aggregate.total_analyses}\n")
        summary_text.append("📁 Files Scanned: ", style="bold")
        summary_text.append(f"{aggregate.total_files_scanned:,}\n")
        summary_text.append("🔍 Issues Detected: ", style="bold")
        summary_text.append(f"{aggregate.total_issues_detected:,}\n")
        summary_text.append("⏱️  Avg Duration: ", style="bold")
        summary_text.append(f"{aggregate.average_duration:.1f}s\n")
        summary_text.append("📊 Avg Issues/Analysis: ", style="bold")
        summary_text.append(f"{aggregate.average_issues_per_analysis:.1f}")

        self.console.print(
            Panel(summary_text, title=f"📊 Statistics ({period_label})", border_style="blue")
        )

        # Severity Table
        severity_table = Table(title="Issues by Severity", show_header=True, header_style="bold")
        severity_table.add_column("Severity", style="cyan")
        severity_table.add_column("Count", justify="right")
        severity_table.add_column("Bar", justify="left")

        max_count = max(aggregate.issues_by_severity.values()) or 1
        colors = {"critical": "red", "high": "orange1", "medium": "yellow", "low": "green"}

        for severity, count in aggregate.issues_by_severity.items():
            bar_len = int((count / max_count) * 20)
            bar = "█" * bar_len
            severity_table.add_row(
                severity.capitalize(), str(count), f"[{colors.get(severity, 'white')}]{bar}[/]"
            )

        self.console.print(severity_table)

        # Category Table
        cat_table = Table(title="Issues by Category", show_header=True, header_style="bold")
        cat_table.add_column("Category", style="cyan")
        cat_table.add_column("Total", justify="right")
        cat_table.add_column("Critical", justify="right", style="red")
        cat_table.add_column("High", justify="right", style="orange1")
        cat_table.add_column("Medium", justify="right", style="yellow")
        cat_table.add_column("Low", justify="right", style="green")
        cat_table.add_column("Trend")

        trend_icons = {"improving": "📉 ↓", "stable": "➡️", "regressing": "📈 ↑"}

        for cat in categories:
            cat_table.add_row(
                cat.category.capitalize(),
                str(cat.total_issues),
                str(cat.severity_breakdown.get("critical", 0)),
                str(cat.severity_breakdown.get("high", 0)),
                str(cat.severity_breakdown.get("medium", 0)),
                str(cat.severity_breakdown.get("low", 0)),
                trend_icons.get(cat.trend, "➡️"),
            )

        self.console.print(cat_table)

        # ROI Panel
        roi_text = Text()
        roi_text.append("💰 Estimated Savings\n\n", style="bold")
        roi_text.append("⏰ Developer Hours Saved: ", style="bold")
        roi_text.append(f"{roi.hours_saved:.1f} hours\n")
        roi_text.append("💵 Cost Saved: ", style="bold")
        roi_text.append(f"${roi.cost_saved:,.2f} {roi.currency}\n")
        roi_text.append("🛡️  Incidents Avoided: ", style="bold")
        roi_text.append(f"{roi.incidents_avoided}\n")
        roi_text.append("💸 Incident Cost Avoided: ", style="bold")
        roi_text.append(f"${roi.incident_cost_avoided:,.2f}")

        self.console.print(Panel(roi_text, title="📈 ROI Metrics", border_style="green"))

        return "Dashboard displayed"

    def export_json(self, period: str = "all", output_path: Optional[Path] = None) -> Path:
        """
        Export statistics to JSON format.

        Args:
            period: Time period filter
            output_path: Output file path (auto-generated if not provided)

        Returns:
            Path to exported file
        """
        aggregate, records = self.aggregate_statistics(period)
        roi = self.calculate_roi(aggregate)
        categories = self.get_category_breakdown(records)

        report = ExportReport(
            generated_at=datetime.now(),
            period=period,
            format="json",
            summary=aggregate,
            roi=roi,
            by_category=categories,
            records=records,
        )

        if output_path is None:
            output_path = Path(f"aetheris-stats-{datetime.now().strftime('%Y%m%d')}.json")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report.to_dict(), f, indent=2)

        logger.info(f"Exported JSON statistics to {output_path}")
        return output_path

    def export_csv(self, period: str = "all", output_path: Optional[Path] = None) -> Path:
        """
        Export statistics to CSV format.

        Args:
            period: Time period filter
            output_path: Output file path (auto-generated if not provided)

        Returns:
            Path to exported file
        """
        _, records = self.aggregate_statistics(period)

        if output_path is None:
            output_path = Path(f"aetheris-stats-{datetime.now().strftime('%Y%m%d')}.csv")

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "date",
                    "files_scanned",
                    "critical",
                    "high",
                    "medium",
                    "low",
                    "security",
                    "performance",
                    "quality",
                    "debt",
                    "duration_seconds",
                ]
            )

            for record in records:
                writer.writerow(
                    [
                        record.timestamp.strftime("%Y-%m-%d"),
                        record.files_scanned,
                        record.issues_by_severity.get("critical", 0),
                        record.issues_by_severity.get("high", 0),
                        record.issues_by_severity.get("medium", 0),
                        record.issues_by_severity.get("low", 0),
                        record.issues_by_category.get("security", 0),
                        record.issues_by_category.get("performance", 0),
                        record.issues_by_category.get("quality", 0),
                        record.issues_by_category.get("debt", 0),
                        f"{record.duration_seconds:.2f}",
                    ]
                )

        logger.info(f"Exported CSV statistics to {output_path}")
        return output_path

    def export_markdown(self, period: str = "all", output_path: Optional[Path] = None) -> Path:
        """
        Export statistics to Markdown format.

        Args:
            period: Time period filter
            output_path: Output file path (auto-generated if not provided)

        Returns:
            Path to exported file
        """
        aggregate, records = self.aggregate_statistics(period)
        roi = self.calculate_roi(aggregate)
        categories = self.get_category_breakdown(records)

        period_label = {"week": "Last 7 days", "month": "Last 30 days", "all": "All time"}.get(
            period, period
        )

        output = StringIO()
        output.write("# Aetheris Analysis Statistics\n\n")
        output.write(
            f"**Period**: {period_label} | **Generated**: {datetime.now().strftime('%Y-%m-%d')}\n\n"
        )

        # Summary
        output.write("## Summary\n\n")
        output.write("| Metric | Value |\n")
        output.write("|--------|-------|\n")
        output.write(f"| Total Analyses | {aggregate.total_analyses} |\n")
        output.write(f"| Files Scanned | {aggregate.total_files_scanned:,} |\n")
        output.write(f"| Issues Detected | {aggregate.total_issues_detected:,} |\n")
        output.write(f"| Avg Duration | {aggregate.average_duration:.1f}s |\n\n")

        # ROI
        output.write("## ROI Metrics\n\n")
        output.write(f"- **Hours Saved**: {roi.hours_saved:.1f}\n")
        output.write(f"- **Cost Saved**: ${roi.cost_saved:,.2f}\n")
        output.write(f"- **Incidents Avoided**: {roi.incidents_avoided}\n")
        output.write(f"- **Incident Cost Avoided**: ${roi.incident_cost_avoided:,.2f}\n\n")

        # Category Breakdown
        output.write("## Category Breakdown\n\n")
        output.write("| Category | Issues | Critical | High | Medium | Low |\n")
        output.write("|----------|--------|----------|------|--------|-----|\n")
        for cat in categories:
            output.write(
                f"| {cat.category.capitalize()} | {cat.total_issues} | "
                f"{cat.severity_breakdown.get('critical', 0)} | "
                f"{cat.severity_breakdown.get('high', 0)} | "
                f"{cat.severity_breakdown.get('medium', 0)} | "
                f"{cat.severity_breakdown.get('low', 0)} |\n"
            )

        if output_path is None:
            output_path = Path(f"aetheris-stats-{datetime.now().strftime('%Y%m%d')}.md")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output.getvalue())

        logger.info(f"Exported Markdown statistics to {output_path}")
        return output_path

    def export(self, format: str, period: str = "all", output_path: Optional[Path] = None) -> Path:
        """
        Export statistics to specified format.

        Args:
            format: Export format (json, csv, md)
            period: Time period filter
            output_path: Output file path

        Returns:
            Path to exported file

        Raises:
            ValueError: If format is invalid
        """
        if format not in EXPORT_FORMATS:
            raise ValueError(f"Invalid format '{format}'. Use: {', '.join(EXPORT_FORMATS)}")

        if format == "json":
            return self.export_json(period, output_path)
        elif format == "csv":
            return self.export_csv(period, output_path)
        else:  # md
            return self.export_markdown(period, output_path)

    def get_roi_parameters(self) -> ROIParameters:
        """Get current ROI parameters."""
        storage = self.load_storage()
        return storage.roi_parameters

    def set_roi_parameter(self, key: str, value: float) -> None:
        """
        Set a single ROI parameter.

        Args:
            key: Parameter name (hourly_rate, incident_cost, time_per_*)
            value: New value
        """
        storage = self.load_storage()
        params = storage.roi_parameters

        valid_keys = [
            "hourly_rate",
            "incident_cost",
            "time_per_critical",
            "time_per_high",
            "time_per_medium",
            "time_per_low",
        ]

        if key not in valid_keys:
            raise ValueError(f"Invalid parameter '{key}'. Valid keys: {', '.join(valid_keys)}")

        setattr(params, key, value)
        self.save_storage()
        logger.info(f"Updated ROI parameter {key} to {value}")
