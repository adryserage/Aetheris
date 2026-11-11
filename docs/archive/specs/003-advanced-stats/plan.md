# Implementation Plan: Advanced Statistics Command

**Branch**: `003-advanced-stats` | **Date**: 2025-01-07 | **Spec**: [spec.md](./spec.md)
**Target Version**: v2.7

## Summary

Add `aetheris stats` command to display project metrics, performance data, and ROI calculations. Provides value justification for users and stakeholders.

## Technical Context

**Language/Version**: Python 3.9+
**Primary Dependencies**: Rich (tables), locale (region detection)
**Storage**: JSON file for persistent stats (`~/.aetheris/stats.json`)
**Testing**: Unit tests for calculations, integration tests for CLI
**Constraints**: Stats collection must not impact analysis performance

## Project Structure

### Files to Create/Modify

```text
src/cli.py                      # ADD: stats command
src/core/stats.py               # NEW: ProjectStats, PerformanceMetrics, ROIMetrics
src/core/stats_collector.py     # NEW: StatsCollector class
src/core/heuristics.py          # NEW: HeuristicConfig, time/cost calculations
src/core/orchestrator.py        # MODIFY: Integrate stats collection
```

## Data Model

### ProjectStats
```python
@dataclass
class ProjectStats:
    total_files_analyzed: int
    total_lines_of_code: int
    last_updated: datetime
```

### PerformanceMetrics
```python
@dataclass
class PerformanceMetrics:
    bugs_detected: int
    bugs_resolved: int
    total_analysis_time_seconds: float
    total_fix_generation_time_seconds: float
```

### ROIMetrics
```python
@dataclass
class ROIMetrics:
    human_time_saved_minutes: float
    money_saved: float
    currency: str
    hourly_rate: float
```

### HeuristicConfig
```python
@dataclass
class HeuristicConfig:
    simple_bug_minutes: float = 37.5
    moderate_bug_minutes: float = 90.0
    complex_bug_minutes: float = 240.0

    @classmethod
    def get_regional_rate(cls) -> tuple[float, str]:
        """Returns (rate, currency) based on system locale"""
```

## Regional Rate Detection

```python
def get_regional_rate() -> tuple[float, str]:
    locale_str = locale.getdefaultlocale()[0] or "en_US"
    if locale_str.startswith("fr_CA") or locale_str.startswith("en_CA"):
        return (120.0, "CAD")
    elif locale_str.startswith("en_US"):
        return (95.0, "USD")
    else:  # Europe and default
        return (85.0, "EUR")
```

## Next Steps

1. Generate tasks.md
2. Implement data models
3. Implement stats collector
4. Add CLI command
5. Integrate with orchestrator
