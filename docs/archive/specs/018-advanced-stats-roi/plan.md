# Implementation Plan: Advanced Statistics & ROI

**Branch**: `018-advanced-stats-roi` | **Date**: 2026-01-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/018-advanced-stats-roi/spec.md`
**Version Target**: v2.6.5

## Summary

Implement a comprehensive statistics and ROI tracking system for Aetheris that:
- Stores analysis results locally with timestamps after each analysis run
- Calculates aggregated metrics (total analyses, files scanned, issues detected)
- Estimates developer time and cost savings based on issue severity
- Provides CLI commands for viewing stats, filtering by period, and exporting to JSON/CSV/Markdown

## Technical Context

**Language/Version**: Python 3.9+ (compatible with existing codebase)
**Primary Dependencies**: Pydantic (data validation), Rich (terminal UI), pathlib (file I/O)
**Storage**: Local JSON files (~/.aetheris/statistics.json and ./aetheris-stats.json)
**Testing**: pytest, pytest-asyncio
**Target Platform**: Cross-platform CLI (Linux, macOS, Windows)
**Project Type**: Single project extending existing CLI
**Performance Goals**: Dashboard display < 2 seconds, handle 1000+ analysis records
**Constraints**: No external services, local storage only, backward compatible CLI
**Scale/Scope**: Per-project statistics with optional global aggregation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Since the project constitution is a template, applying general principles:

| Principle | Status | Notes |
|-----------|--------|-------|
| Extend existing CLI | ✅ Pass | Adding `stats` subcommand to existing CLI |
| Local storage | ✅ Pass | JSON files, no cloud dependency |
| Cross-platform | ✅ Pass | Using pathlib, standard Python |
| Backward compatible | ✅ Pass | New command, no breaking changes |
| Test coverage | ⚠️ Pending | Will add unit tests for new service |

## Project Structure

### Documentation (this feature)

```text
specs/018-advanced-stats-roi/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (CLI interface spec)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── models/
│   └── stats_models.py      # NEW: AnalysisRecord, ROICalculation, StatisticsAggregate
├── services/
│   └── statistics_service.py # NEW: StatisticsService class
├── cli.py                    # MODIFY: Add stats subcommand
└── config/
    └── stats_config.py       # NEW: Default ROI parameters

tests/
├── unit/
│   └── test_statistics_service.py  # NEW
└── integration/
    └── test_stats_cli.py           # NEW
```

**Structure Decision**: Single project extension - adding new models and service module following existing patterns (cleanup_service.py, cleanup_models.py as reference).

## Dependencies

### Existing (No Changes)
- `pydantic>=2.0.0` - Data validation for stats models
- `rich>=13.0.0` - Terminal UI for dashboard display
- `pyyaml>=6.0` - Config file support

### New (Optional)
- None required - using existing dependencies

## Integration Points

1. **CodeAnalyzer** (`src/core/analyzer.py`)
   - Hook after analysis completion to record statistics
   - Pass analysis results to StatisticsService

2. **CLI** (`src/cli.py`)
   - New `stats` command with subcommands
   - Export flags: `--export json|csv|md`
   - Period filter: `--period week|month|all`

3. **Config** (`src/config/`)
   - ROI calculation parameters (hourly rate, incident costs)
   - Storage paths configuration

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Storage file corruption | Low | Medium | Implement backup and recovery |
| Large file performance | Low | Low | Use pagination, lazy loading |
| Concurrent writes | Low | Medium | File locking mechanism |
| Config migration | Low | Low | Default values if missing |

## Complexity Tracking

No constitution violations requiring justification. Implementation follows existing patterns.
