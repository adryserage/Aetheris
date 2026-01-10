# Feature Specification: Advanced Statistics & ROI

**Feature Branch**: `018-advanced-stats-roi`
**Created**: 2026-01-09
**Status**: Draft
**Version Target**: v2.6.5
**Input**: User description: "Statistiques Avancées & ROI (v2.6.5) - Système complet de métriques et statistiques pour mesurer l'impact des analyses Aetheris."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Analysis Statistics Dashboard (Priority: P1)

As a developer, I want to view a comprehensive dashboard of my analysis statistics so that I can understand the impact of Aetheris on my codebase quality.

**Why this priority**: Core feature - without a dashboard to display statistics, other features have no value. This is the foundation that all other features build upon.

**Independent Test**: Can be tested by running `aetheris stats` after performing at least one analysis and verifying that aggregate metrics are displayed correctly.

**Acceptance Scenarios**:

1. **Given** I have run at least one analysis, **When** I execute `aetheris stats`, **Then** I see a formatted dashboard showing total analyses, files scanned, and issues detected
2. **Given** I have never run an analysis, **When** I execute `aetheris stats`, **Then** I see a friendly message indicating no data available with guidance to run first analysis
3. **Given** I have run multiple analyses, **When** I view the dashboard, **Then** I see aggregated totals and averages across all analyses

---

### User Story 2 - Calculate and Display ROI Metrics (Priority: P2)

As a team lead, I want to see the estimated time and cost savings from using Aetheris so that I can justify the tool's value to stakeholders.

**Why this priority**: ROI metrics are the key differentiator that demonstrates business value. Depends on P1 for data collection.

**Independent Test**: Can be tested by viewing ROI section of the stats output and verifying calculations match expected formulas based on detected issues.

**Acceptance Scenarios**:

1. **Given** I have detected issues in analyses, **When** I view stats, **Then** I see estimated developer hours saved based on issue complexity
2. **Given** I have security issues detected, **When** I view ROI metrics, **Then** I see estimated cost of potential security incidents avoided
3. **Given** I want to customize ROI calculations, **When** I provide custom hourly rates, **Then** the ROI is calculated using my custom values

---

### User Story 3 - Export Statistics to Various Formats (Priority: P2)

As a manager, I want to export analysis statistics to different formats so that I can include them in reports and presentations.

**Why this priority**: Essential for reporting and sharing metrics with stakeholders who don't use CLI tools directly.

**Independent Test**: Can be tested by running export commands and verifying output files are valid and contain expected data.

**Acceptance Scenarios**:

1. **Given** I have statistics data, **When** I run `aetheris stats --export json`, **Then** I receive a valid JSON file with all metrics
2. **Given** I have statistics data, **When** I run `aetheris stats --export csv`, **Then** I receive a CSV file importable into spreadsheet applications
3. **Given** I have statistics data, **When** I run `aetheris stats --export md`, **Then** I receive a Markdown report suitable for documentation

---

### User Story 4 - Filter Statistics by Time Period (Priority: P3)

As a developer, I want to filter statistics by time period so that I can track trends and improvements over time.

**Why this priority**: Adds analytical depth but not essential for basic functionality.

**Independent Test**: Can be tested by running stats with period filters and verifying only data from specified period is included.

**Acceptance Scenarios**:

1. **Given** I have analyses from multiple weeks, **When** I run `aetheris stats --period week`, **Then** I see only statistics from the last 7 days
2. **Given** I have analyses from multiple months, **When** I run `aetheris stats --period month`, **Then** I see only statistics from the last 30 days
3. **Given** I want all historical data, **When** I run `aetheris stats --period all`, **Then** I see statistics from all recorded analyses

---

### User Story 5 - View Metrics by Category Breakdown (Priority: P3)

As a developer, I want to see metrics broken down by category so that I can identify which areas of my codebase need the most attention.

**Why this priority**: Provides deeper insights but requires P1 and P2 to be meaningful.

**Independent Test**: Can be tested by running stats with category breakdown flag and verifying each category shows separate metrics.

**Acceptance Scenarios**:

1. **Given** I have issues in multiple categories, **When** I view detailed stats, **Then** I see separate counts for security, performance, quality, and technical debt issues
2. **Given** I want to focus on one category, **When** I filter by category, **Then** I see only metrics relevant to that category
3. **Given** I view category breakdown, **When** comparing periods, **Then** I can see which categories improved or regressed

---

### User Story 6 - Compare Analysis Results Over Time (Priority: P4)

As a team lead, I want to compare analysis results between different time periods so that I can demonstrate improvement trends.

**Why this priority**: Advanced analytics feature that depends on historical data collection.

**Independent Test**: Can be tested by running comparison command with two date ranges and verifying delta calculations.

**Acceptance Scenarios**:

1. **Given** I have analyses from different periods, **When** I request a comparison, **Then** I see side-by-side metrics with percentage change
2. **Given** metrics have improved, **When** I view the comparison, **Then** improvements are highlighted positively
3. **Given** metrics have regressed, **When** I view the comparison, **Then** regressions are flagged as warnings

---

### Edge Cases

- What happens when statistics storage file is corrupted or missing?
  - System recreates empty storage and logs warning
- How does system handle analyses with zero issues?
  - Include in statistics with zero values, don't skip
- What happens when export file path is not writable?
  - Display clear error message with permission details
- How does system handle very large statistics history (years of data)?
  - Implement pagination for display, full data for exports
- What happens when user specifies invalid period format?
  - Show usage help with valid period options

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST store analysis results locally with timestamps after each analysis run
- **FR-002**: System MUST calculate total analyses, files scanned, and issues detected from stored history
- **FR-003**: System MUST estimate developer time saved using configurable formulas based on issue severity and type
- **FR-004**: System MUST calculate ROI based on estimated time saved and configurable hourly/incident rates
- **FR-005**: System MUST provide `aetheris stats` command to display statistics dashboard in terminal
- **FR-006**: System MUST support export to JSON, CSV, and Markdown formats via `--export` flag
- **FR-007**: System MUST support period filtering via `--period` flag with week, month, and all options
- **FR-008**: System MUST display metrics broken down by category (security, performance, quality, technical debt)
- **FR-009**: System MUST gracefully handle missing or corrupted statistics storage
- **FR-010**: System MUST allow users to configure ROI calculation parameters (hourly rate, incident costs)
- **FR-011**: System MUST display trends showing improvement or regression between periods
- **FR-012**: System MUST persist statistics across system restarts

### Key Entities

- **AnalysisRecord**: Represents a single analysis run with timestamp, files scanned, issues found by category, and duration
- **StatisticsAggregate**: Computed totals and averages from multiple AnalysisRecords
- **ROICalculation**: Derived metrics including time saved, cost avoided, with calculation parameters
- **CategoryMetrics**: Issue counts and severity breakdown for each category (security, performance, quality, debt)
- **ExportReport**: Formatted output for JSON, CSV, or Markdown containing selected statistics

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can view complete statistics dashboard within 2 seconds of command execution
- **SC-002**: Statistics are accurately persisted across 100% of analysis runs without data loss
- **SC-003**: Exported files are valid and parseable by standard tools (JSON validators, spreadsheet apps)
- **SC-004**: ROI estimates are within reasonable range based on industry benchmarks for code review time savings
- **SC-005**: 90% of users can understand and interpret the dashboard without additional documentation
- **SC-006**: Period filtering returns accurate data subsets matching the specified time range
- **SC-007**: System handles 1000+ analysis records without performance degradation

## Assumptions

- Statistics are stored locally per project (not centralized)
- Default ROI parameters use industry-standard estimates (can be overridden)
- Issue severity is already tracked by existing analysis functionality
- Users have write access to project directory for statistics storage
- Default time estimates per issue type:
  - Critical: 4 hours saved
  - High: 2 hours saved
  - Medium: 1 hour saved
  - Low: 0.5 hours saved
- Default hourly developer rate: $75/hour (configurable)
- Default cost per production incident avoided: $5,000 (configurable)

## Out of Scope

- Cloud synchronization of statistics
- Team/organization-wide aggregated statistics
- Real-time dashboard (web UI)
- Integration with external analytics platforms (future feature)
- Automated report scheduling
