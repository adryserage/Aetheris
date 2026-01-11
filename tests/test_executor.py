"""Unit tests for task executor."""

import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.runner.executor import (
    ExecutionContext,
    SecurityProfile,
    TaskRunner,
    run_task,
)
from src.runner.output_formatter import ExecutionStatus
from src.runner.task_parser import TaskFile


class TestSecurityProfile:
    """Tests for SecurityProfile class."""

    def test_safe_profile(self):
        """Test safe profile restrictions."""
        profile = SecurityProfile.SAFE

        assert profile.allows_auto_fix is False
        assert profile.allows_file_delete is False
        assert profile.allows_shell_commands is False
        assert profile.allows_git_operations is True

    def test_ci_profile(self):
        """Test CI profile permissions."""
        profile = SecurityProfile.CI

        assert profile.allows_auto_fix is True
        assert profile.allows_file_delete is False
        assert profile.allows_shell_commands is False
        assert profile.allows_git_operations is True

    def test_dev_profile(self):
        """Test dev profile permissions."""
        profile = SecurityProfile.DEV

        assert profile.allows_auto_fix is True
        assert profile.allows_file_delete is True
        assert profile.allows_shell_commands is True
        assert profile.allows_git_operations is True

    def test_unrestricted_profile(self):
        """Test unrestricted profile permissions."""
        profile = SecurityProfile.UNRESTRICTED

        assert profile.allows_auto_fix is True
        assert profile.allows_file_delete is True
        assert profile.allows_shell_commands is True
        assert profile.allows_git_operations is True

    def test_from_string(self):
        """Test creating profile from string."""
        assert SecurityProfile.from_string("safe") == SecurityProfile.SAFE
        assert SecurityProfile.from_string("ci") == SecurityProfile.CI
        assert SecurityProfile.from_string("dev") == SecurityProfile.DEV
        assert SecurityProfile.from_string("unrestricted") == SecurityProfile.UNRESTRICTED

    def test_from_string_case_insensitive(self):
        """Test case insensitivity."""
        assert SecurityProfile.from_string("SAFE") == SecurityProfile.SAFE
        assert SecurityProfile.from_string("Ci") == SecurityProfile.CI

    def test_from_string_invalid(self):
        """Test invalid profile name defaults to SAFE."""
        assert SecurityProfile.from_string("invalid") == SecurityProfile.SAFE
        assert SecurityProfile.from_string("") == SecurityProfile.SAFE


class TestExecutionContext:
    """Tests for ExecutionContext class."""

    def test_initialization(self):
        """Test context initialization."""
        context = ExecutionContext(
            profile=SecurityProfile.CI,
            dry_run=True,
            verbose=True,
        )

        assert context.profile == SecurityProfile.CI
        assert context.dry_run is True
        assert context.verbose is True
        assert context.logs == []
        assert context.blocked_operations == []

    def test_log_message(self):
        """Test logging messages."""
        context = ExecutionContext(profile=SecurityProfile.SAFE)

        context.log("INFO", "Test message")

        assert len(context.logs) == 1
        assert "INFO" in context.logs[0]
        assert "Test message" in context.logs[0]

    def test_log_info(self):
        """Test info logging."""
        context = ExecutionContext(profile=SecurityProfile.SAFE)

        context.log_info("Info message")

        assert "INFO" in context.logs[0]
        assert "Info message" in context.logs[0]

    def test_log_error(self):
        """Test error logging."""
        context = ExecutionContext(profile=SecurityProfile.SAFE)

        context.log_error("Error message")

        assert "ERROR" in context.logs[0]
        assert "Error message" in context.logs[0]

    def test_log_warning(self):
        """Test warning logging."""
        context = ExecutionContext(profile=SecurityProfile.SAFE)

        context.log_warning("Warning message")

        assert "WARNING" in context.logs[0]
        assert "Warning message" in context.logs[0]

    def test_add_blocked_operation(self):
        """Test adding blocked operation."""
        context = ExecutionContext(profile=SecurityProfile.SAFE)

        context.add_blocked_operation("file_delete", "Not allowed in safe mode")

        assert len(context.blocked_operations) == 1
        op = context.blocked_operations[0]
        assert op.operation == "file_delete"
        assert op.reason == "Not allowed in safe mode"
        assert op.profile == "safe"


class TestTaskRunner:
    """Tests for TaskRunner class."""

    def create_task_file(self, content: dict) -> Path:
        """Helper to create a temporary task file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(content, f)
            f.flush()
            return Path(f.name)

    def test_initialization(self):
        """Test runner initialization."""
        runner = TaskRunner(profile=SecurityProfile.CI, verbose=True)

        assert runner.profile == SecurityProfile.CI
        assert runner.verbose is True
        assert runner.dry_run is False

    def test_initialization_defaults(self):
        """Test runner default values."""
        runner = TaskRunner()

        assert runner.profile == SecurityProfile.SAFE
        assert runner.verbose is False
        assert runner.dry_run is False
        assert runner.timeout is None
        assert runner.seed is None

    @pytest.mark.asyncio
    async def test_run_dry_run(self):
        """Test dry run mode."""
        content = {
            "version": "1.0",
            "task": {"type": "analysis", "target": {"files": ["*.py"]}},
        }
        path = self.create_task_file(content)

        try:
            runner = TaskRunner(dry_run=True)
            result = await runner.run(path)

            # Dry run should succeed without actually running
            assert result.status == ExecutionStatus.SUCCESS
        finally:
            path.unlink()

    @pytest.mark.asyncio
    async def test_run_file_not_found(self):
        """Test running with non-existent file."""
        runner = TaskRunner()
        result = await runner.run(Path("/nonexistent/task.json"))

        assert result.status == ExecutionStatus.ERROR
        assert result.error.type == "file_not_found"

    @pytest.mark.asyncio
    async def test_run_invalid_task_file(self):
        """Test running with invalid task file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("invalid json")
            f.flush()
            path = Path(f.name)

        try:
            runner = TaskRunner()
            result = await runner.run(path)

            assert result.status == ExecutionStatus.ERROR
            assert result.error.type == "parse_error"
        finally:
            path.unlink()

    @pytest.mark.asyncio
    async def test_run_includes_version(self):
        """Test that result includes version."""
        content = {
            "version": "1.0",
            "task": {"type": "analysis", "target": {"files": ["*.py"]}},
        }
        path = self.create_task_file(content)

        try:
            runner = TaskRunner(dry_run=True)
            result = await runner.run(path)

            assert result.version is not None
        finally:
            path.unlink()

    @pytest.mark.asyncio
    async def test_run_with_seed(self):
        """Test running with random seed."""
        content = {
            "version": "1.0",
            "task": {"type": "analysis", "target": {"files": ["*.py"]}},
        }
        path = self.create_task_file(content)

        try:
            runner = TaskRunner(dry_run=True, seed=42)
            result = await runner.run(path)

            # Should complete successfully with seed
            assert result.status == ExecutionStatus.SUCCESS
        finally:
            path.unlink()


class TestRunTask:
    """Tests for run_task convenience function."""

    def test_run_task_dry_run(self):
        """Test run_task in dry run mode."""
        content = {
            "version": "1.0",
            "task": {"type": "analysis", "target": {"files": ["*.py"]}},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(content, f)
            f.flush()
            path = Path(f.name)

        try:
            result = run_task(path, dry_run=True)

            assert result.status == ExecutionStatus.SUCCESS
        finally:
            path.unlink()

    def test_run_task_with_profile(self):
        """Test run_task with specific profile."""
        content = {
            "version": "1.0",
            "task": {"type": "analysis", "target": {"files": ["*.py"]}},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(content, f)
            f.flush()
            path = Path(f.name)

        try:
            result = run_task(path, profile="ci", dry_run=True)

            assert result.status == ExecutionStatus.SUCCESS
        finally:
            path.unlink()

    def test_run_task_file_not_found(self):
        """Test run_task with non-existent file."""
        result = run_task(Path("/nonexistent/task.json"))

        assert result.status == ExecutionStatus.ERROR
        assert result.error.type == "file_not_found"
