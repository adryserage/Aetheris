# Data Model: Safety Profiles

**Feature**: 010-safety-profiles
**Date**: 2026-01-07

## Entities

### ProfileType (Enum)

Represents the available safety profile types.

| Value | Description |
|-------|-------------|
| `SAFE` | Conservative mode with maximum guardrails |
| `CI` | Strict CI/CD mode, non-interactive |
| `YOLO` | Full autonomy, extended capabilities |

```python
class ProfileType(str, Enum):
    SAFE = "safe"
    CI = "ci"
    YOLO = "yolo"
```

---

### ProfileConfig (Dataclass)

Configuration values for a specific profile.

| Field | Type | SAFE | CI | YOLO |
|-------|------|------|----|----- |
| `network_allowed` | bool | False | True | True |
| `ai_network_allowed` | bool | True | True | True |
| `max_diff_lines` | int | 500 | 500 | None |
| `max_repair_loops` | int | 3 | 3 | 10 |
| `require_tests` | bool | True | True | False |
| `interactive_prompts` | bool | True | False | True |
| `fail_fast` | bool | False | True | False |
| `audit_logging` | bool | False | True | True |
| `require_acknowledgment` | bool | False | False | True |
| `allowlist_enabled` | bool | True | False | False |

```python
@dataclass
class ProfileConfig:
    profile_type: ProfileType
    network_allowed: bool
    ai_network_allowed: bool
    max_diff_lines: Optional[int]
    max_repair_loops: int
    require_tests: bool
    interactive_prompts: bool
    fail_fast: bool
    audit_logging: bool
    require_acknowledgment: bool
    allowlist_enabled: bool
```

---

### AllowlistConfig (Dataclass)

Command allowlist configuration for safe mode.

| Field | Type | Description |
|-------|------|-------------|
| `version` | str | Schema version |
| `patterns` | List[str] | Glob patterns for allowed commands |
| `exact` | List[str] | Exact command matches |
| `user_additions` | List[str] | User-added patterns |

```python
@dataclass
class AllowlistConfig:
    version: str
    patterns: List[str]
    exact: List[str]
    user_additions: List[str] = field(default_factory=list)

    def is_allowed(self, command: str) -> bool:
        """Check if command matches allowlist"""
        ...
```

**Default Allowlist**:
- `git *` - Git operations
- `pytest *`, `python -m pytest *` - Testing
- `black *`, `ruff *`, `mypy *` - Linting/formatting
- `pip list`, `pip show *` - Package inspection (read-only)

---

### AuditLogEntry (Dataclass)

Structured audit log record for CI mode.

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | datetime | ISO 8601 timestamp |
| `level` | str | Log level (INFO, WARN, ERROR) |
| `event` | str | Event type identifier |
| `profile` | ProfileType | Active profile |
| `details` | dict | Event-specific data |
| `session_id` | str | Unique analysis session ID |

```python
@dataclass
class AuditLogEntry:
    timestamp: datetime
    level: str
    event: str
    profile: ProfileType
    details: Dict[str, Any]
    session_id: str

    def to_jsonl(self) -> str:
        """Serialize to JSON Lines format"""
        ...
```

**Event Types**:
- `analysis_started` - Analysis run initiated
- `profile_applied` - Profile constraints activated
- `file_analyzed` - Individual file analysis complete
- `constraint_enforced` - Profile constraint blocked an action
- `repair_loop` - Repair iteration executed
- `analysis_completed` - Analysis finished
- `analysis_failed` - Analysis encountered error

---

### DiffBoundary (Dataclass)

Configuration for diff size limits.

| Field | Type | Description |
|-------|------|-------------|
| `max_lines_changed` | Optional[int] | Maximum total lines changed |
| `max_files_changed` | Optional[int] | Maximum files modified |
| `max_lines_per_file` | Optional[int] | Maximum lines per file |

```python
@dataclass
class DiffBoundary:
    max_lines_changed: Optional[int] = 500
    max_files_changed: Optional[int] = None
    max_lines_per_file: Optional[int] = None

    def exceeds(self, lines: int, files: int = 1) -> bool:
        """Check if proposed changes exceed boundaries"""
        ...
```

---

## Relationships

```
AnalysisConfig
    └── profile: ProfileType
            └── get_config() -> ProfileConfig
                    ├── DiffBoundary
                    ├── AllowlistConfig (if allowlist_enabled)
                    └── AuditLogEntry (if audit_logging)
```

## State Transitions

### Profile Lifecycle

```
┌─────────────────┐
│  Profile None   │
│ (CLI not run)   │
└────────┬────────┘
         │ --profile flag or default
         ▼
┌─────────────────┐
│ Profile Applied │
│ (constraints    │
│  active)        │
└────────┬────────┘
         │ analysis complete
         ▼
┌─────────────────┐
│ Profile Ended   │
│ (cleanup done)  │
└─────────────────┘
```

### Repair Loop States (Safe Mode)

```
┌──────────────────┐
│ Iteration 0      │
└────────┬─────────┘
         │ issue found
         ▼
┌──────────────────┐     max_repair_loops
│ Iteration 1-N    │────────────────────►  STOP
└────────┬─────────┘     reached
         │ success
         ▼
┌──────────────────┐
│ Complete         │
└──────────────────┘
```
