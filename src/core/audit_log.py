"""
Audit Logging for CI Mode (v2.12)

Provides structured logging for CI/CD environments with JSON Lines format.
Records analysis events, profile constraints, and execution details.
"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.core.profiles import ProfileType


@dataclass
class AuditLogEntry:
    """Structured audit log record for CI mode"""

    timestamp: str  # ISO 8601 format
    level: str  # INFO, WARN, ERROR
    event: str  # Event type identifier
    profile: str  # Active profile name
    session_id: str  # Unique analysis session ID
    details: Dict[str, Any] = field(default_factory=dict)

    def to_jsonl(self) -> str:
        """Serialize to JSON Lines format"""
        data = {
            "timestamp": self.timestamp,
            "level": self.level,
            "event": self.event,
            "profile": self.profile,
            "session_id": self.session_id,
            "details": self.details,
        }
        return json.dumps(data, ensure_ascii=False, default=str)

    @classmethod
    def from_jsonl(cls, line: str) -> "AuditLogEntry":
        """Deserialize from JSON Lines format"""
        data = json.loads(line)
        return cls(
            timestamp=data["timestamp"],
            level=data["level"],
            event=data["event"],
            profile=data["profile"],
            session_id=data["session_id"],
            details=data.get("details", {}),
        )


# Event types for audit logging
class AuditEvent:
    """Event type constants for audit logging"""

    ANALYSIS_STARTED = "analysis_started"
    PROFILE_APPLIED = "profile_applied"
    FILE_ANALYZED = "file_analyzed"
    CONSTRAINT_ENFORCED = "constraint_enforced"
    REPAIR_LOOP = "repair_loop"
    COMMAND_EXECUTED = "command_executed"
    COMMAND_BLOCKED = "command_blocked"
    NETWORK_BLOCKED = "network_blocked"
    DIFF_EXCEEDED = "diff_exceeded"
    TEST_REQUIRED = "test_required"
    TEST_PASSED = "test_passed"
    TEST_FAILED = "test_failed"
    ANALYSIS_COMPLETED = "analysis_completed"
    ANALYSIS_FAILED = "analysis_failed"


class AuditLogger:
    """Audit logger for CI mode"""

    def __init__(
        self,
        enabled: bool = True,
        log_path: Optional[str] = None,
        profile: ProfileType = ProfileType.CI,
        session_id: Optional[str] = None,
    ):
        """
        Initialize audit logger

        Args:
            enabled: Whether audit logging is enabled
            log_path: Path to audit log file (default: aetheris-audit.jsonl)
            profile: Active safety profile
            session_id: Unique session ID (auto-generated if not provided)
        """
        self.enabled = enabled
        self.log_path = Path(log_path or "aetheris-audit.jsonl")
        self.profile = profile
        self.session_id = session_id or str(uuid.uuid4())[:8]
        self._buffer: List[AuditLogEntry] = []
        self._file_handle = None

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO 8601 format"""
        return datetime.utcnow().isoformat() + "Z"

    def _create_entry(
        self,
        level: str,
        event: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> AuditLogEntry:
        """Create a new audit log entry"""
        return AuditLogEntry(
            timestamp=self._get_timestamp(),
            level=level,
            event=event,
            profile=self.profile.value,
            session_id=self.session_id,
            details=details or {},
        )

    def log_event(
        self,
        event: str,
        level: str = "INFO",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log an event

        Args:
            event: Event type (use AuditEvent constants)
            level: Log level (INFO, WARN, ERROR)
            details: Event-specific data
        """
        if not self.enabled:
            return

        entry = self._create_entry(level, event, details)
        self._buffer.append(entry)

        # Write immediately for important events
        if level in ("WARN", "ERROR") or event in (
            AuditEvent.ANALYSIS_STARTED,
            AuditEvent.ANALYSIS_COMPLETED,
            AuditEvent.ANALYSIS_FAILED,
        ):
            self.flush()

    def log_info(self, event: str, **details) -> None:
        """Log an INFO level event"""
        self.log_event(event, "INFO", details)

    def log_warn(self, event: str, **details) -> None:
        """Log a WARN level event"""
        self.log_event(event, "WARN", details)

    def log_error(self, event: str, **details) -> None:
        """Log an ERROR level event"""
        self.log_event(event, "ERROR", details)

    def log_analysis_started(
        self,
        root_dir: str,
        files_count: int,
        agents: List[str],
    ) -> None:
        """Log analysis start event"""
        self.log_info(
            AuditEvent.ANALYSIS_STARTED,
            root_dir=root_dir,
            files_count=files_count,
            agents=agents,
        )

    def log_profile_applied(
        self,
        profile_name: str,
        constraints: Dict[str, Any],
    ) -> None:
        """Log profile constraints applied"""
        self.log_info(
            AuditEvent.PROFILE_APPLIED,
            profile_name=profile_name,
            constraints=constraints,
        )

    def log_file_analyzed(
        self,
        file_path: str,
        issues_count: int,
        duration_ms: int,
    ) -> None:
        """Log individual file analysis"""
        self.log_info(
            AuditEvent.FILE_ANALYZED,
            file_path=file_path,
            issues_count=issues_count,
            duration_ms=duration_ms,
        )

    def log_constraint_enforced(
        self,
        constraint_type: str,
        message: str,
    ) -> None:
        """Log profile constraint enforcement"""
        self.log_warn(
            AuditEvent.CONSTRAINT_ENFORCED,
            constraint_type=constraint_type,
            message=message,
        )

    def log_command_blocked(self, command: str, reason: str) -> None:
        """Log blocked command in safe mode"""
        self.log_warn(
            AuditEvent.COMMAND_BLOCKED,
            command=command,
            reason=reason,
        )

    def log_analysis_completed(
        self,
        total_files: int,
        total_issues: int,
        duration_seconds: float,
    ) -> None:
        """Log analysis completion"""
        self.log_info(
            AuditEvent.ANALYSIS_COMPLETED,
            total_files=total_files,
            total_issues=total_issues,
            duration_seconds=round(duration_seconds, 2),
        )

    def log_analysis_failed(
        self,
        error: str,
        files_processed: int,
    ) -> None:
        """Log analysis failure"""
        self.log_error(
            AuditEvent.ANALYSIS_FAILED,
            error=error,
            files_processed=files_processed,
        )

    def flush(self) -> None:
        """Flush buffered entries to file"""
        if not self.enabled or not self._buffer:
            return

        try:
            # Ensure parent directory exists
            self.log_path.parent.mkdir(parents=True, exist_ok=True)

            # Append entries to file
            with open(self.log_path, "a", encoding="utf-8") as f:
                for entry in self._buffer:
                    f.write(entry.to_jsonl() + "\n")

            self._buffer.clear()
        except IOError as e:
            # Don't fail the analysis if audit logging fails
            print(f"⚠️  Warning: Could not write audit log: {e}")

    def get_log_path(self) -> Path:
        """Get the audit log file path"""
        return self.log_path

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Log failure if exception occurred
        if exc_type is not None:
            self.log_analysis_failed(
                error=str(exc_val),
                files_processed=0,
            )
        self.flush()


def create_audit_logger(
    profile: ProfileType,
    log_path: Optional[str] = None,
) -> AuditLogger:
    """
    Create an audit logger based on profile settings

    Args:
        profile: Active safety profile
        log_path: Optional custom log path

    Returns:
        AuditLogger instance (may be disabled for non-CI profiles)
    """
    from src.core.profiles import get_profile_config

    config = get_profile_config(profile)
    return AuditLogger(
        enabled=config.audit_logging,
        log_path=log_path,
        profile=profile,
    )
