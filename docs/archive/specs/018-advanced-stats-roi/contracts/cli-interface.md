# CLI Contract: Statistics Commands

**Feature**: 018-advanced-stats-roi
**Date**: 2026-01-09

## Command: `aetheris stats`

### Synopsis

```
aetheris stats [OPTIONS]
```

### Description

Display analysis statistics dashboard with aggregated metrics and ROI estimates.

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--period` | enum | `all` | Time period filter: `week`, `month`, `all` |
| `--export` | enum | None | Export format: `json`, `csv`, `md` |
| `--output` | path | auto | Output file path (default: `aetheris-stats-{date}.{ext}`) |
| `--project` | path | `.` | Project directory to read stats from |
| `--global` | flag | false | Show global stats instead of project |

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | No statistics data available |
| 3 | Invalid period or export format |
| 4 | Cannot write export file |

### Examples

```bash
# Basic dashboard
aetheris stats

# Last week only
aetheris stats --period week

# Export to JSON
aetheris stats --export json

# Export monthly stats to specific file
aetheris stats --period month --export csv --output report.csv

# Global user statistics
aetheris stats --global
```

---

## Command: `aetheris config get stats`

### Synopsis

```
aetheris config get stats
```

### Description

Display current ROI configuration parameters.

### Output

```json
{
  "hourly_rate": 75.0,
  "incident_cost": 5000.0,
  "time_per_critical": 4.0,
  "time_per_high": 2.0,
  "time_per_medium": 1.0,
  "time_per_low": 0.5
}
```

---

## Command: `aetheris config set stats.<key> <value>`

### Synopsis

```
aetheris config set stats.<key> <value>
```

### Description

Update ROI configuration parameter.

### Parameters

| Key | Type | Range | Description |
|-----|------|-------|-------------|
| `hourly_rate` | float | 0-1000 | Developer hourly rate (USD) |
| `incident_cost` | float | 0-100000 | Production incident cost |
| `time_per_critical` | float | 0-24 | Hours per critical issue |
| `time_per_high` | float | 0-24 | Hours per high severity issue |
| `time_per_medium` | float | 0-24 | Hours per medium severity issue |
| `time_per_low` | float | 0-24 | Hours per low severity issue |

### Examples

```bash
aetheris config set stats.hourly_rate 100
aetheris config set stats.incident_cost 10000
```

---

## Output Formats

### Terminal Dashboard (default)

Rich-formatted terminal output with:
- Header panel with title and period
- Summary metrics (analyses, files, issues)
- Category breakdown table with bar charts
- ROI estimate panel

### JSON Export

```json
{
  "generated_at": "ISO8601",
  "period": "week|month|all",
  "summary": {
    "total_analyses": "int",
    "files_scanned": "int",
    "issues_detected": "int",
    "issues_by_severity": {"critical": "int", "high": "int", "medium": "int", "low": "int"}
  },
  "roi": {
    "hours_saved": "float",
    "cost_saved": "float",
    "currency": "string"
  },
  "by_category": {
    "<category>": {
      "total": "int",
      "critical": "int",
      "high": "int",
      "medium": "int",
      "low": "int"
    }
  },
  "records": [
    {
      "id": "uuid",
      "timestamp": "ISO8601",
      "files_scanned": "int",
      "issues_detected": "int"
    }
  ]
}
```

### CSV Export

```csv
date,files_scanned,critical,high,medium,low,hours_saved,cost_saved
2026-01-09,123,0,2,8,15,12.5,937.50
2026-01-08,98,1,0,5,12,10.0,750.00
```

### Markdown Export

```markdown
# Aetheris Analysis Statistics

**Period**: Last 30 days | **Generated**: 2026-01-09

## Summary
| Metric | Value |
|--------|-------|
| Total Analyses | 42 |
| Files Scanned | 1,250 |
| Issues Detected | 156 |

## ROI Metrics
- **Hours Saved**: 72.5
- **Cost Saved**: $5,437.50

## Category Breakdown
| Category | Issues | Critical | High | Medium | Low |
|----------|--------|----------|------|--------|-----|
| Security | 23 | 2 | 5 | 8 | 8 |
| Performance | 45 | 0 | 3 | 15 | 27 |
| Quality | 52 | 1 | 2 | 12 | 37 |
| Tech Debt | 36 | 0 | 2 | 10 | 24 |
```

---

## Error Messages

| Scenario | Message |
|----------|---------|
| No data | "No analysis data available. Run `aetheris analysis` first." |
| Invalid period | "Invalid period '{value}'. Use: week, month, or all" |
| Invalid export | "Invalid export format '{value}'. Use: json, csv, or md" |
| Write error | "Cannot write to '{path}': {error}" |
| Corrupt storage | "Statistics file corrupted. Creating new storage." |
