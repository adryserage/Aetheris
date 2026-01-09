# Statistics & ROI Command

Track analysis statistics and calculate return on investment from Aetheris usage.

## Quick Start

```bash
# View dashboard
aetheris stats

# Filter by time period
aetheris stats --period week

# Export to JSON
aetheris stats --export json
```

## Synopsis

```
aetheris stats [OPTIONS]
```

## Description

The `stats` command displays a comprehensive dashboard showing:

- **Analysis metrics**: Total analyses, files scanned, issues detected
- **Issue breakdown**: By severity (critical, high, medium, low) and category (security, performance, quality, debt)
- **ROI metrics**: Estimated developer hours saved, cost savings, incidents avoided

Statistics are automatically recorded after each `aetheris analysis` run.

## Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--period` | `-p` | `all` | Time period filter: `week`, `month`, or `all` |
| `--export` | `-e` | None | Export format: `json`, `csv`, or `md` |
| `--output` | `-o` | Auto | Output file path for export |
| `--global` | | false | Show global stats instead of project-local |
| `--project` | | `.` | Project directory to read stats from |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | No statistics data available |
| 3 | Invalid period or export format |
| 4 | Cannot write export file |

## Examples

### View Dashboard

```bash
# Basic dashboard (all time)
aetheris stats

# Last 7 days
aetheris stats --period week

# Last 30 days
aetheris stats --period month
```

### Export Statistics

```bash
# Export to JSON
aetheris stats --export json

# Export to CSV with custom filename
aetheris stats --export csv --output monthly-report.csv

# Export monthly Markdown report
aetheris stats --period month --export md --output docs/stats-report.md
```

### Global vs Project Statistics

```bash
# Project-local stats (default)
aetheris stats

# Global user statistics (all projects)
aetheris stats --global

# Stats from specific project
aetheris stats --project /path/to/other/project
```

## Output Formats

### Terminal Dashboard (default)

Rich-formatted terminal output with:
- Summary metrics panel
- Severity breakdown table with bar chart
- Category breakdown table with trends
- ROI estimate panel

### JSON Export

```json
{
  "generated_at": "2026-01-09T12:00:00",
  "period": "week",
  "summary": {
    "total_analyses": 42,
    "files_scanned": 1250,
    "issues_detected": 156,
    "issues_by_severity": {"critical": 2, "high": 15, "medium": 45, "low": 94}
  },
  "roi": {
    "hours_saved": 72.5,
    "cost_saved": 5437.50,
    "currency": "USD",
    "incidents_avoided": 3
  },
  "by_category": {...},
  "records": [...]
}
```

### CSV Export

```csv
date,files_scanned,critical,high,medium,low,security,performance,quality,debt,duration_seconds
2026-01-09,123,0,2,8,15,3,5,12,5,45.20
2026-01-08,98,1,0,5,12,4,3,8,2,32.15
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
...
```

## ROI Calculation

ROI is calculated using configurable parameters:

| Severity | Default Hours Saved | Description |
|----------|---------------------|-------------|
| Critical | 4.0 hours | Major issues caught before production |
| High | 2.0 hours | Significant bugs avoided |
| Medium | 1.0 hours | Code quality improvements |
| Low | 0.5 hours | Minor suggestions |

**Default rates:**
- Developer hourly rate: $75/hour
- Cost per production incident avoided: $5,000

## Storage

Statistics are stored in JSON format:

| Location | Scope | File |
|----------|-------|------|
| Project-local | Single project | `./aetheris-stats.json` |
| Global | All projects | `~/.aetheris/statistics.json` |

## Related Commands

- `aetheris analysis` - Run analysis (auto-records statistics)
- `aetheris config get stats` - View ROI configuration
- `aetheris config set stats.<key> <value>` - Update ROI parameters

## Version

Added in **v2.6.5**
