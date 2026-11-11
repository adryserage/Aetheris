# Quickstart: Advanced Statistics & ROI

**Feature**: 018-advanced-stats-roi
**Date**: 2026-01-09

## CLI Usage

### View Statistics Dashboard

```bash
# Show statistics for all time (default)
aetheris stats

# Show last 7 days only
aetheris stats --period week

# Show last 30 days
aetheris stats --period month

# Show all historical data
aetheris stats --period all
```

### Export Statistics

```bash
# Export to JSON (for programmatic use)
aetheris stats --export json
# Output: aetheris-stats-2026-01-09.json

# Export to CSV (for spreadsheets)
aetheris stats --export csv
# Output: aetheris-stats-2026-01-09.csv

# Export to Markdown (for documentation)
aetheris stats --export md
# Output: aetheris-stats-2026-01-09.md

# Combine with period filter
aetheris stats --period month --export json
```

### Configure ROI Parameters

```bash
# Set custom hourly rate
aetheris config set stats.hourly_rate 100

# Set custom incident cost
aetheris config set stats.incident_cost 10000

# View current configuration
aetheris config get stats
```

## Example Output

### Dashboard View

```
┌─────────────────────────────────────────────────────────────┐
│                   📊 Aetheris Statistics                     │
│                      Last 30 days                           │
├─────────────────────────────────────────────────────────────┤
│  Analyses: 42    Files: 1,250    Issues: 156               │
├─────────────────────────────────────────────────────────────┤
│ Category Breakdown                                          │
│ ┌──────────────┬──────────┬───────────────────────────────┐│
│ │ Category     │ Issues   │ Distribution                  ││
│ ├──────────────┼──────────┼───────────────────────────────┤│
│ │ Security     │ 23       │ ████████░░░░░░░░░░░░  15%    ││
│ │ Performance  │ 45       │ ██████████████░░░░░░  29%    ││
│ │ Quality      │ 52       │ ████████████████░░░░  33%    ││
│ │ Tech Debt    │ 36       │ ████████████░░░░░░░░  23%    ││
│ └──────────────┴──────────┴───────────────────────────────┘│
├─────────────────────────────────────────────────────────────┤
│ 💰 ROI Estimate                                             │
│    Hours Saved: 72.5 hrs    Cost Avoided: $5,437.50        │
└─────────────────────────────────────────────────────────────┘
```

### JSON Export

```json
{
  "generated_at": "2026-01-09T12:00:00Z",
  "period": "month",
  "summary": {
    "total_analyses": 42,
    "files_scanned": 1250,
    "issues_detected": 156,
    "issues_by_severity": {
      "critical": 3,
      "high": 12,
      "medium": 45,
      "low": 96
    }
  },
  "roi": {
    "hours_saved": 72.5,
    "cost_saved": 5437.50,
    "currency": "USD"
  },
  "by_category": {
    "security": {"total": 23, "critical": 2, "high": 5, "medium": 8, "low": 8},
    "performance": {"total": 45, "critical": 0, "high": 3, "medium": 15, "low": 27},
    "quality": {"total": 52, "critical": 1, "high": 2, "medium": 12, "low": 37},
    "debt": {"total": 36, "critical": 0, "high": 2, "medium": 10, "low": 24}
  }
}
```

### No Data Available

```
┌─────────────────────────────────────────────────────────────┐
│                   📊 Aetheris Statistics                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  No analysis data available yet.                           │
│                                                             │
│  Run your first analysis:                                   │
│    aetheris analysis                                        │
│                                                             │
│  Or analyze specific files:                                 │
│    aetheris analysis --files src/main.py                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Programmatic Usage

### Record Analysis (automatic)

Statistics are automatically recorded after each analysis run:

```python
from src.core.analyzer import CodeAnalyzer

analyzer = CodeAnalyzer(config)
results = await analyzer.analyze(files)
# Statistics automatically recorded
```

### Query Statistics (service)

```python
from src.services.statistics_service import StatisticsService

stats_service = StatisticsService()

# Get aggregate for last month
aggregate = stats_service.get_aggregate(period="month")
print(f"Total analyses: {aggregate.total_analyses}")

# Calculate ROI
roi = stats_service.calculate_roi(aggregate)
print(f"Hours saved: {roi.hours_saved}")

# Export to JSON
stats_service.export(format="json", period="month", output_path="stats.json")
```

## Storage Locations

| Location | Purpose |
|----------|---------|
| `~/.aetheris/statistics.json` | Global user statistics |
| `./aetheris-stats.json` | Project-specific statistics |
| `~/.aetheris/config.json` | ROI parameters configuration |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AETHERIS_STATS_DIR` | `~/.aetheris` | Statistics storage directory |
| `AETHERIS_HOURLY_RATE` | `75.0` | Developer hourly rate for ROI |
| `AETHERIS_INCIDENT_COST` | `5000.0` | Cost per production incident |
