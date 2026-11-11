# Research: Advanced Statistics & ROI

**Feature**: 018-advanced-stats-roi
**Date**: 2026-01-09

## Research Topics

### 1. Statistics Storage Format

**Decision**: JSON file with atomic writes

**Rationale**:
- Human-readable and debuggable
- Native Python support (no additional dependencies)
- Consistent with existing Aetheris patterns (config files, cache)
- Supports incremental updates

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| SQLite | Overkill for simple append-only records; adds complexity |
| CSV | No nested structure support for category breakdowns |
| YAML | Slower parsing, no significant benefit over JSON |

**Implementation Notes**:
- Use `fcntl` (Unix) / `msvcrt` (Windows) for file locking
- Implement backup rotation (keep last 3 backups)
- Storage location: `~/.aetheris/statistics.json` (global) + `./aetheris-stats.json` (project)

---

### 2. ROI Calculation Formula

**Decision**: Severity-weighted time savings model

**Rationale**:
- Industry-standard approach for defect prevention ROI
- Configurable parameters for different team contexts
- Conservative estimates to maintain credibility

**Formula**:
```
Time Saved = Σ (issues_by_severity × time_factor)
Cost Saved = Time Saved × hourly_rate

Where time_factor:
  - Critical: 4 hours (production incident investigation)
  - High: 2 hours (complex debugging)
  - Medium: 1 hour (standard fix)
  - Low: 0.5 hours (quick fix)

Security Bonus:
  - Security issues add potential_incident_cost to avoided costs
  - Default: $5,000 per security issue (configurable)
```

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Fixed cost per issue | Doesn't reflect severity differences |
| LOC-based | Inaccurate proxy for effort |
| Historical data fitting | No baseline data available |

---

### 3. Period Filtering Strategy

**Decision**: Timestamp-based filtering with predefined ranges

**Rationale**:
- Simple implementation using datetime comparisons
- Covers common reporting needs (weekly, monthly, all-time)
- Extensible to custom date ranges if needed

**Period Definitions**:
| Period | Range |
|--------|-------|
| `week` | Last 7 days |
| `month` | Last 30 days |
| `all` | All recorded history |

**Alternatives Considered**:
| Alternative | Rejected Because |
|-------------|------------------|
| Calendar weeks/months | More complex, less intuitive |
| Custom date ranges only | Verbose for common cases |
| Sliding windows | Overcomplicated for MVP |

---

### 4. Export Format Specifications

**Decision**: Three formats with consistent structure

**Rationale**:
- JSON: Machine-readable, API integration
- CSV: Spreadsheet compatibility, reporting
- Markdown: Documentation, README badges

---

### 5. Dashboard Display Design

**Decision**: Rich terminal UI with panels and tables

**Rationale**:
- Consistent with existing Aetheris CLI output
- Rich library already installed
- Supports colors, tables, progress indicators

---

### 6. Integration with Analysis Pipeline

**Decision**: Post-analysis hook in CodeAnalyzer

**Rationale**:
- Non-invasive integration point
- Access to complete analysis results
- Can be disabled without affecting core analysis

---

## Research Conclusions

All technical decisions made. No unresolved NEEDS CLARIFICATION items.

**Ready for Phase 1**: Data model and contract generation.
