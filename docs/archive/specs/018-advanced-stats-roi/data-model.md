# Data Model: Advanced Statistics & ROI

**Feature**: 018-advanced-stats-roi
**Date**: 2026-01-09

## Entities

### 1. AnalysisRecord

Represents a single analysis run with all relevant metrics.

```python
@dataclass
class AnalysisRecord:
    """A single analysis run record."""
    id: str                          # UUID for unique identification
    timestamp: datetime              # When analysis was run
    project_path: str                # Absolute path to analyzed project
    duration_seconds: float          # How long the analysis took
    files_scanned: int               # Number of files analyzed
    issues_by_severity: dict[str, int]  # {"critical": 0, "high": 2, "medium": 5, "low": 10}
    issues_by_category: dict[str, int]  # {"security": 3, "performance": 5, "quality": 7, "debt": 2}
    agents_used: list[str]           # ["security", "performance", "quality"]
    ai_provider: str                 # "gemini", "openai", "claude"
    version: str                     # Aetheris version used
```

**Validation Rules**:
- `timestamp` must be valid ISO 8601 format
- `files_scanned` must be >= 0
- `issues_by_severity` keys must be in ["critical", "high", "medium", "low"]
- `issues_by_category` keys must be in ["security", "performance", "quality", "debt"]

---

### 2. StatisticsAggregate

Computed totals and averages from multiple AnalysisRecords.

```python
@dataclass
class StatisticsAggregate:
    """Aggregated statistics from multiple analysis runs."""
    period_start: datetime           # Start of the aggregation period
    period_end: datetime             # End of the aggregation period
    total_analyses: int              # Number of analysis runs
    total_files_scanned: int         # Sum of all files scanned
    total_issues_detected: int       # Sum of all issues
    issues_by_severity: dict[str, int]  # Aggregated by severity
    issues_by_category: dict[str, int]  # Aggregated by category
    average_duration: float          # Average analysis duration
    average_issues_per_analysis: float  # Average issues per run
```

**Computed Properties**:
- `total_issues_detected` = sum of all `issues_by_severity` values
- `average_issues_per_analysis` = `total_issues_detected` / `total_analyses`

---

### 3. ROICalculation

Derived metrics for return on investment estimates.

```python
@dataclass
class ROICalculation:
    """ROI metrics based on detected issues."""
    hours_saved: float               # Estimated developer hours saved
    cost_saved: float                # Estimated cost in currency
    currency: str                    # "USD" by default
    incidents_avoided: int           # Number of potential production incidents
    incident_cost_avoided: float     # Cost of avoided incidents
    calculation_parameters: ROIParameters  # Parameters used for calculation
```

**ROIParameters**:
```python
@dataclass
class ROIParameters:
    """Configurable ROI calculation parameters."""
    hourly_rate: float = 75.0        # Developer hourly rate
    time_per_critical: float = 4.0   # Hours to fix critical issue manually
    time_per_high: float = 2.0       # Hours for high severity
    time_per_medium: float = 1.0     # Hours for medium severity
    time_per_low: float = 0.5        # Hours for low severity
    incident_cost: float = 5000.0    # Cost per production incident
```

---

### 4. CategoryMetrics

Issue counts and severity breakdown for a specific category.

```python
@dataclass
class CategoryMetrics:
    """Metrics for a specific issue category."""
    category: str                    # "security", "performance", "quality", "debt"
    total_issues: int                # Total issues in this category
    severity_breakdown: dict[str, int]  # {"critical": 1, "high": 3, ...}
    trend: str                       # "improving", "stable", "regressing"
    change_from_previous: int        # Delta from previous period
```

---

### 5. ExportReport

Container for formatted export data.

```python
@dataclass
class ExportReport:
    """Formatted statistics export."""
    generated_at: datetime           # When export was created
    period: str                      # "week", "month", "all"
    format: str                      # "json", "csv", "markdown"
    summary: StatisticsAggregate     # Aggregate data
    roi: ROICalculation              # ROI metrics
    by_category: list[CategoryMetrics]  # Per-category breakdown
    records: list[AnalysisRecord]    # Raw records (for detailed exports)
```

---

### 6. StatisticsStorage

The root storage structure for the JSON file.

```python
@dataclass
class StatisticsStorage:
    """Root structure for statistics storage file."""
    version: str = "1.0"             # Schema version for migrations
    created_at: datetime             # When storage was created
    updated_at: datetime             # Last update timestamp
    records: list[AnalysisRecord]    # All analysis records
    roi_parameters: ROIParameters    # Current ROI configuration
```

---

## Relationships

```
StatisticsStorage
    └── records: list[AnalysisRecord]
    └── roi_parameters: ROIParameters

StatisticsAggregate (computed from records with period filter)
    └── period_start, period_end
    └── aggregated metrics

ROICalculation (computed from StatisticsAggregate)
    └── uses ROIParameters
    └── produces hours_saved, cost_saved

ExportReport (combines all for output)
    └── StatisticsAggregate
    └── ROICalculation
    └── list[CategoryMetrics]
```

---

## State Transitions

### AnalysisRecord Lifecycle

```
[Analysis Starts] → [Analysis Completes] → [Record Created] → [Stored]
                                              ↓
                                        [StatisticsStorage.records.append()]
```

### Statistics Query Flow

```
[User: aetheris stats] → [Load Storage] → [Filter by Period] → [Aggregate] → [Calculate ROI] → [Display/Export]
```

---

## Storage Schema (JSON)

```json
{
  "version": "1.0",
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-01-09T12:00:00Z",
  "roi_parameters": {
    "hourly_rate": 75.0,
    "time_per_critical": 4.0,
    "time_per_high": 2.0,
    "time_per_medium": 1.0,
    "time_per_low": 0.5,
    "incident_cost": 5000.0
  },
  "records": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "timestamp": "2026-01-09T10:30:00Z",
      "project_path": "/home/user/myproject",
      "duration_seconds": 45.2,
      "files_scanned": 123,
      "issues_by_severity": {"critical": 0, "high": 2, "medium": 8, "low": 15},
      "issues_by_category": {"security": 3, "performance": 5, "quality": 12, "debt": 5},
      "agents_used": ["security", "performance", "quality", "architecture", "dependency", "metrics"],
      "ai_provider": "gemini",
      "version": "2.6.5"
    }
  ]
}
```
