"""Unit tests for task file parser."""

import json
import tempfile
from pathlib import Path

import pytest
import yaml

from src.runner.task_parser import TaskFile, TaskFileParser, TaskFileValidationError


class TestTaskFileParser:
    """Tests for TaskFileParser class."""

    def test_parse_valid_json(self):
        """Test parsing a valid JSON task file."""
        content = {
            "version": "1.0",
            "task": {
                "type": "analysis",
                "target": {"files": ["src/**/*.py"]},
                "options": {"timeout": "30m", "profile": "ci"},
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(content, f)
            f.flush()
            path = Path(f.name)

        try:
            parser = TaskFileParser()
            task_file = parser.parse(path)

            assert task_file.version == "1.0"
            assert task_file.task.type == "analysis"
            assert task_file.task.target.files == ["src/**/*.py"]
            assert task_file.task.options.timeout == "30m"
            assert task_file.task.options.profile == "ci"
        finally:
            path.unlink()

    def test_parse_valid_yaml(self):
        """Test parsing a valid YAML task file."""
        content = {
            "version": "1.0",
            "task": {
                "type": "analysis",
                "target": {"changed_only": True},
                "options": {"timeout": "15m", "agents": ["security", "quality"]},
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(content, f)
            f.flush()
            path = Path(f.name)

        try:
            parser = TaskFileParser()
            task_file = parser.parse(path)

            assert task_file.version == "1.0"
            assert task_file.task.type == "analysis"
            assert task_file.task.target.changed_only is True
            assert task_file.task.options.agents == ["security", "quality"]
        finally:
            path.unlink()

    def test_parse_file_not_found(self):
        """Test parsing a non-existent file."""
        parser = TaskFileParser()

        with pytest.raises(TaskFileValidationError) as exc_info:
            parser.parse(Path("/nonexistent/file.json"))

        assert exc_info.value.error_type == "file_not_found"

    def test_parse_invalid_extension(self):
        """Test parsing a file with invalid extension."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("some content")
            f.flush()
            path = Path(f.name)

        try:
            parser = TaskFileParser()

            with pytest.raises(TaskFileValidationError) as exc_info:
                parser.parse(path)

            assert exc_info.value.error_type == "invalid_format"
        finally:
            path.unlink()

    def test_parse_invalid_json_syntax(self):
        """Test parsing invalid JSON syntax."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{invalid json")
            f.flush()
            path = Path(f.name)

        try:
            parser = TaskFileParser()

            with pytest.raises(TaskFileValidationError) as exc_info:
                parser.parse(path)

            assert exc_info.value.error_type == "parse_error"
        finally:
            path.unlink()

    def test_parse_missing_required_field(self):
        """Test parsing file missing required fields."""
        content = {"version": "1.0"}  # Missing 'task' field

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(content, f)
            f.flush()
            path = Path(f.name)

        try:
            parser = TaskFileParser()

            with pytest.raises(TaskFileValidationError) as exc_info:
                parser.parse(path)

            assert exc_info.value.error_type == "validation_error"
        finally:
            path.unlink()

    def test_parse_invalid_task_type(self):
        """Test parsing file with invalid task type."""
        content = {
            "version": "1.0",
            "task": {"type": "invalid_type", "target": {"files": ["*.py"]}},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(content, f)
            f.flush()
            path = Path(f.name)

        try:
            parser = TaskFileParser()

            with pytest.raises(TaskFileValidationError) as exc_info:
                parser.parse(path)

            assert exc_info.value.error_type == "validation_error"
        finally:
            path.unlink()

    def test_parse_all_task_types(self):
        """Test that all valid task types are accepted."""
        valid_types = ["analysis", "fix", "stats", "cleanup", "validate-package"]

        for task_type in valid_types:
            content = {
                "version": "1.0",
                "task": {"type": task_type, "target": {"files": ["*.py"]}},
            }

            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
                json.dump(content, f)
                f.flush()
                path = Path(f.name)

            try:
                parser = TaskFileParser()
                task_file = parser.parse(path)
                assert task_file.task.type == task_type
            finally:
                path.unlink()


class TestTaskFile:
    """Tests for TaskFile class."""

    def test_from_file_json(self):
        """Test creating TaskFile from JSON file."""
        content = {
            "version": "1.0",
            "task": {
                "type": "analysis",
                "target": {"files": ["src/**/*.py"]},
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(content, f)
            f.flush()
            path = Path(f.name)

        try:
            task_file = TaskFile.from_file(path)
            assert task_file.version == "1.0"
            assert task_file.task.type == "analysis"
        finally:
            path.unlink()

    def test_from_file_yaml(self):
        """Test creating TaskFile from YAML file."""
        content = {
            "version": "1.0",
            "task": {
                "type": "stats",
                "target": {"files": ["*.py"]},
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(content, f)
            f.flush()
            path = Path(f.name)

        try:
            task_file = TaskFile.from_file(path)
            assert task_file.version == "1.0"
            assert task_file.task.type == "stats"
        finally:
            path.unlink()

    def test_metadata_preserved(self):
        """Test that metadata is preserved in parsed file."""
        content = {
            "version": "1.0",
            "task": {"type": "analysis", "target": {"files": ["*.py"]}},
            "metadata": {"run_id": "build-123", "triggered_by": "github-actions"},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(content, f)
            f.flush()
            path = Path(f.name)

        try:
            task_file = TaskFile.from_file(path)
            assert task_file.metadata == {"run_id": "build-123", "triggered_by": "github-actions"}
        finally:
            path.unlink()

    def test_output_options(self):
        """Test parsing output options."""
        content = {
            "version": "1.0",
            "task": {"type": "analysis", "target": {"files": ["*.py"]}},
            "output": {"format": "json", "include_diff": True, "include_logs": True},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(content, f)
            f.flush()
            path = Path(f.name)

        try:
            task_file = TaskFile.from_file(path)
            assert task_file.output.format == "json"
            assert task_file.output.include_diff is True
            assert task_file.output.include_logs is True
        finally:
            path.unlink()


class TestTaskFileValidationError:
    """Tests for TaskFileValidationError class."""

    def test_error_attributes(self):
        """Test error has correct attributes."""
        error = TaskFileValidationError(
            message="Test error",
            error_type="test_type",
            details={"key": "value"},
        )

        assert str(error) == "Test error"
        assert error.error_type == "test_type"
        assert error.details == {"key": "value"}

    def test_error_without_details(self):
        """Test error without details."""
        error = TaskFileValidationError(
            message="Test error",
            error_type="test_type",
        )

        assert error.details is None
