"""Unit tests for output formatter."""

import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest

from src.runner.output_formatter import (
    BlockedOperation,
    ErrorInfo,
    ExecutionResult,
    ExecutionStatus,
    ExitCode,
    OutputFormatter,
    ResultsSummary,
    TaskInfo,
)


class TestExecutionStatus:
    """Tests for ExecutionStatus enum."""

    def test_status_values(self):
        """Test all status values exist."""
        assert ExecutionStatus.SUCCESS == "success"
        assert ExecutionStatus.ERROR == "error"
        assert ExecutionStatus.TIMEOUT == "timeout"
        assert ExecutionStatus.INTERRUPTED == "interrupted"
        assert ExecutionStatus.BLOCKED == "blocked"


class TestExitCode:
    """Tests for ExitCode enum."""

    def test_exit_code_values(self):
        """Test exit code values."""
        assert ExitCode.SUCCESS.value == 0
        assert ExitCode.ERROR.value == 1
        assert ExitCode.WARNING.value == 2


class TestErrorInfo:
    """Tests for ErrorInfo class."""

    def test_to_dict(self):
        """Test conversion to dict."""
        error = ErrorInfo(
            type="file_not_found",
            message="File not found: test.json",
            details={"path": "test.json"},
        )

        result = error.to_dict()

        assert result["type"] == "file_not_found"
        assert result["message"] == "File not found: test.json"
        assert result["details"] == {"path": "test.json"}

    def test_to_dict_without_details(self):
        """Test conversion without details."""
        error = ErrorInfo(type="unknown", message="Unknown error")

        result = error.to_dict()

        assert result["type"] == "unknown"
        assert result["message"] == "Unknown error"
        assert "details" not in result


class TestBlockedOperation:
    """Tests for BlockedOperation class."""

    def test_to_dict(self):
        """Test conversion to dict."""
        blocked = BlockedOperation(
            operation="file_delete",
            reason="Blocked by safe profile",
            profile="safe",
        )

        result = blocked.to_dict()

        assert result["operation"] == "file_delete"
        assert result["reason"] == "Blocked by safe profile"
        assert result["profile"] == "safe"


class TestTaskInfo:
    """Tests for TaskInfo class."""

    def test_to_dict(self):
        """Test conversion to dict."""
        task_info = TaskInfo(
            type="analysis",
            files_processed=42,
            source_file="task.json",
        )

        result = task_info.to_dict()

        assert result["type"] == "analysis"
        assert result["files_processed"] == 42
        assert result["source_file"] == "task.json"


class TestResultsSummary:
    """Tests for ResultsSummary class."""

    def test_to_dict(self):
        """Test conversion to dict."""
        summary = ResultsSummary(
            issues_found=5,
            critical=0,
            high=2,
            medium=3,
            low=0,
            reports=["report1.md", "report2.md"],
        )

        result = summary.to_dict()

        assert result["issues_found"] == 5
        assert result["critical"] == 0
        assert result["high"] == 2
        assert result["medium"] == 3
        assert result["low"] == 0
        assert result["reports"] == ["report1.md", "report2.md"]


class TestExecutionResult:
    """Tests for ExecutionResult class."""

    def test_success_factory(self):
        """Test creating success result."""
        task_info = TaskInfo(type="analysis", files_processed=10, source_file="task.json")
        results = ResultsSummary(issues_found=2, critical=0, high=1, medium=1, low=0, reports=[])

        result = ExecutionResult.success(
            duration_ms=5000,
            task=task_info,
            results=results,
        )

        assert result.status == ExecutionStatus.SUCCESS
        assert result.exit_code == ExitCode.SUCCESS
        assert result.duration_ms == 5000
        assert result.task == task_info
        assert result.results == results

    def test_error_factory(self):
        """Test creating error result."""
        error = ErrorInfo(type="parse_error", message="Invalid JSON")

        result = ExecutionResult.error(duration_ms=100, error=error)

        assert result.status == ExecutionStatus.ERROR
        assert result.exit_code == ExitCode.ERROR
        assert result.error == error

    def test_timeout_factory(self):
        """Test creating timeout result."""
        result = ExecutionResult.timeout(duration_ms=60000, timeout_seconds=60)

        assert result.status == ExecutionStatus.TIMEOUT
        assert result.exit_code == ExitCode.ERROR
        assert result.error.type == "timeout"
        assert "60" in result.error.message

    def test_interrupted_factory(self):
        """Test creating interrupted result."""
        result = ExecutionResult.interrupted(duration_ms=30000, signal_name="SIGINT")

        assert result.status == ExecutionStatus.INTERRUPTED
        assert result.exit_code == ExitCode.ERROR
        assert result.error.type == "interrupted"
        assert "SIGINT" in result.error.message

    def test_blocked_factory(self):
        """Test creating blocked result."""
        blocked_ops = [
            BlockedOperation(operation="file_delete", reason="Not allowed", profile="safe")
        ]

        result = ExecutionResult.blocked(duration_ms=500, blocked_operations=blocked_ops)

        assert result.status == ExecutionStatus.BLOCKED
        assert result.exit_code == ExitCode.ERROR
        assert result.blocked_operations == blocked_ops

    def test_to_dict_success(self):
        """Test conversion to dict for success."""
        task_info = TaskInfo(type="analysis", files_processed=5, source_file="task.json")
        results = ResultsSummary(issues_found=0, critical=0, high=0, medium=0, low=0, reports=[])

        result = ExecutionResult.success(
            duration_ms=1000,
            task=task_info,
            results=results,
            version="2.8.0",
        )

        data = result.to_dict()

        assert data["status"] == "success"
        assert data["exit_code"] == 0
        assert data["duration_ms"] == 1000
        assert data["version"] == "2.8.0"
        assert data["task"]["type"] == "analysis"
        assert data["results"]["issues_found"] == 0

    def test_to_dict_with_logs(self):
        """Test conversion with logs."""
        result = ExecutionResult.success(
            duration_ms=1000,
            logs=["Log line 1", "Log line 2"],
        )

        data = result.to_dict()

        assert data["logs"] == ["Log line 1", "Log line 2"]

    def test_to_dict_with_diff(self):
        """Test conversion with diff."""
        result = ExecutionResult.success(
            duration_ms=1000,
            diff="--- a/file.py\n+++ b/file.py",
        )

        data = result.to_dict()

        assert data["diff"] == "--- a/file.py\n+++ b/file.py"


class TestOutputFormatter:
    """Tests for OutputFormatter class."""

    def test_format_json(self):
        """Test JSON formatting."""
        result = ExecutionResult.success(duration_ms=1000)

        output = OutputFormatter.format(result, format_type="json")

        # Should be valid JSON
        data = json.loads(output)
        assert data["status"] == "success"

    def test_format_yaml(self):
        """Test YAML formatting."""
        result = ExecutionResult.success(duration_ms=1000)

        output = OutputFormatter.format(result, format_type="yaml")

        # Should contain YAML structure
        assert "status: success" in output or "status: 'success'" in output

    def test_output_to_stdout(self, capsys):
        """Test output to stdout."""
        result = ExecutionResult.success(duration_ms=1000)

        OutputFormatter.output(result)

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["status"] == "success"

    def test_output_to_file(self):
        """Test output to file."""
        result = ExecutionResult.success(duration_ms=1000)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            path = Path(f.name)

        try:
            OutputFormatter.output(result, output_file=path)

            content = path.read_text()
            data = json.loads(content)
            assert data["status"] == "success"
        finally:
            path.unlink()

    def test_no_timestamps_option(self):
        """Test that no_timestamps removes timestamp."""
        result = ExecutionResult.success(duration_ms=1000)

        output_with = OutputFormatter.format(result, no_timestamps=False)
        output_without = OutputFormatter.format(result, no_timestamps=True)

        data_with = json.loads(output_with)
        data_without = json.loads(output_without)

        assert "timestamp" in data_with
        assert "timestamp" not in data_without
