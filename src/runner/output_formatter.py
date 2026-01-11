"""
Output Formatter for Headless Execution

Produces structured JSON output for all execution results.
"""

import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class ExecutionStatus(str, Enum):
    """Execution status values."""

    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    INTERRUPTED = "interrupted"
    BLOCKED = "blocked"


class ExitCode(int, Enum):
    """Exit codes for headless execution."""

    SUCCESS = 0
    ERROR = 1
    WARNING = 2


@dataclass
class ErrorInfo:
    """Structured error information."""

    type: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    traceback: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "type": self.type,
            "message": self.message,
        }
        if self.details:
            result["details"] = self.details
        if self.traceback:
            result["traceback"] = self.traceback
        return result


@dataclass
class BlockedOperation:
    """Record of an operation blocked by security profile."""

    operation: str
    reason: str
    profile: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "operation": self.operation,
            "reason": self.reason,
            "profile": self.profile,
        }


@dataclass
class TaskInfo:
    """Information about the executed task."""

    type: str
    files_processed: int = 0
    source_file: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "type": self.type,
            "files_processed": self.files_processed,
        }
        if self.source_file:
            result["source_file"] = self.source_file
        result.update(self.extra)
        return result


@dataclass
class ResultsSummary:
    """Summary of analysis/fix results."""

    issues_found: int = 0
    issues_fixed: int = 0
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    reports: List[str] = field(default_factory=list)
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "issues_found": self.issues_found,
            "issues_fixed": self.issues_fixed,
            "critical": self.critical,
            "high": self.high,
            "medium": self.medium,
            "low": self.low,
        }
        if self.reports:
            result["reports"] = self.reports
        result.update(self.extra)
        return result


@dataclass
class ExecutionResult:
    """Complete execution result for headless mode."""

    status: ExecutionStatus
    exit_code: ExitCode
    duration_ms: int
    timestamp: Optional[datetime] = None
    version: Optional[str] = None
    task: Optional[TaskInfo] = None
    results: Optional[ResultsSummary] = None
    diff: Optional[str] = None
    logs: List[str] = field(default_factory=list)
    stdout: str = ""
    stderr: str = ""
    error: Optional[ErrorInfo] = None
    blocked_operations: List[BlockedOperation] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    _include_timestamps: bool = True

    def __post_init__(self):
        """Set default timestamp if not provided."""
        if self.timestamp is None and self._include_timestamps:
            self.timestamp = datetime.utcnow()

    @classmethod
    def success(
        cls,
        duration_ms: int,
        task: Optional[TaskInfo] = None,
        results: Optional[ResultsSummary] = None,
        diff: Optional[str] = None,
        logs: Optional[List[str]] = None,
        **kwargs,
    ) -> "ExecutionResult":
        """Create a success result."""
        return cls(
            status=ExecutionStatus.SUCCESS,
            exit_code=ExitCode.SUCCESS,
            duration_ms=duration_ms,
            task=task,
            results=results,
            diff=diff,
            logs=logs or [],
            **kwargs,
        )

    @classmethod
    def error(
        cls,
        duration_ms: int,
        error: ErrorInfo,
        task: Optional[TaskInfo] = None,
        logs: Optional[List[str]] = None,
        **kwargs,
    ) -> "ExecutionResult":
        """Create an error result."""
        return cls(
            status=ExecutionStatus.ERROR,
            exit_code=ExitCode.ERROR,
            duration_ms=duration_ms,
            error=error,
            task=task,
            logs=logs or [],
            **kwargs,
        )

    @classmethod
    def timeout(
        cls,
        duration_ms: int,
        task: Optional[TaskInfo] = None,
        results: Optional[ResultsSummary] = None,
        logs: Optional[List[str]] = None,
        **kwargs,
    ) -> "ExecutionResult":
        """Create a timeout result."""
        return cls(
            status=ExecutionStatus.TIMEOUT,
            exit_code=ExitCode.ERROR,
            duration_ms=duration_ms,
            task=task,
            results=results,
            logs=logs or [],
            error=ErrorInfo(
                type="timeout",
                message="Execution timed out",
            ),
            **kwargs,
        )

    @classmethod
    def interrupted(
        cls,
        duration_ms: int,
        task: Optional[TaskInfo] = None,
        results: Optional[ResultsSummary] = None,
        logs: Optional[List[str]] = None,
        **kwargs,
    ) -> "ExecutionResult":
        """Create an interrupted result."""
        return cls(
            status=ExecutionStatus.INTERRUPTED,
            exit_code=ExitCode.ERROR,
            duration_ms=duration_ms,
            task=task,
            results=results,
            logs=logs or [],
            error=ErrorInfo(
                type="interrupted",
                message="Execution was interrupted",
            ),
            **kwargs,
        )

    @classmethod
    def blocked(
        cls,
        duration_ms: int,
        blocked_operations: List[BlockedOperation],
        task: Optional[TaskInfo] = None,
        logs: Optional[List[str]] = None,
        **kwargs,
    ) -> "ExecutionResult":
        """Create a blocked result."""
        return cls(
            status=ExecutionStatus.BLOCKED,
            exit_code=ExitCode.ERROR,
            duration_ms=duration_ms,
            task=task,
            blocked_operations=blocked_operations,
            logs=logs or [],
            error=ErrorInfo(
                type="blocked",
                message="Operations blocked by security profile",
            ),
            **kwargs,
        )

    def to_dict(self, include_null: bool = False) -> Dict[str, Any]:
        """Convert to dictionary for JSON output.

        Args:
            include_null: If True, include null values
        """
        result: Dict[str, Any] = {
            "status": self.status.value,
            "exit_code": self.exit_code.value,
            "duration_ms": self.duration_ms,
        }

        if self._include_timestamps and self.timestamp:
            result["timestamp"] = self.timestamp.isoformat() + "Z"

        if self.version:
            result["version"] = self.version

        if self.task:
            result["task"] = self.task.to_dict()
        elif include_null:
            result["task"] = None

        if self.results:
            result["results"] = self.results.to_dict()
        elif include_null:
            result["results"] = None

        if self.diff is not None:
            result["diff"] = self.diff
        elif include_null:
            result["diff"] = None

        if self.logs:
            result["logs"] = self.logs
        elif include_null:
            result["logs"] = []

        if self.stdout:
            result["stdout"] = self.stdout

        if self.stderr:
            result["stderr"] = self.stderr

        if self.error:
            result["error"] = self.error.to_dict()
        elif include_null:
            result["error"] = None

        if self.blocked_operations:
            result["blocked_operations"] = [op.to_dict() for op in self.blocked_operations]

        if self.metadata:
            result["metadata"] = self.metadata

        return result

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def to_yaml(self) -> str:
        """Convert to YAML string."""
        return yaml.dump(
            self.to_dict(),
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )


class OutputFormatter:
    """Formatter for execution output."""

    def __init__(
        self,
        format: str = "json",
        include_diff: bool = True,
        include_logs: bool = True,
        include_timestamps: bool = True,
        output_file: Optional[str] = None,
    ):
        self.format = format
        self.include_diff = include_diff
        self.include_logs = include_logs
        self.include_timestamps = include_timestamps
        self.output_file = output_file

    def format_result(self, result: ExecutionResult) -> str:
        """Format execution result to string.

        Args:
            result: Execution result to format

        Returns:
            Formatted string (JSON or YAML)
        """
        # Apply formatting options
        result._include_timestamps = self.include_timestamps

        if not self.include_diff:
            result.diff = None

        if not self.include_logs:
            result.logs = []

        if self.format == "yaml":
            return result.to_yaml()
        else:
            return result.to_json()

    def output(self, result: ExecutionResult) -> None:
        """Output formatted result to stdout or file.

        Args:
            result: Execution result to output
        """
        formatted = self.format_result(result)

        if self.output_file:
            path = Path(self.output_file)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(formatted, encoding="utf-8")
        else:
            print(formatted, file=sys.stdout)

    @classmethod
    def minimal_error_json(
        cls,
        error_type: str,
        message: str,
        exit_code: int = 1,
    ) -> str:
        """Generate minimal error JSON for crash scenarios.

        Used when full ExecutionResult cannot be created.
        """
        return json.dumps(
            {
                "status": "error",
                "exit_code": exit_code,
                "duration_ms": 0,
                "error": {
                    "type": error_type,
                    "message": message,
                },
            },
            indent=2,
        )
