"""
Task File Parser and Validator

Parses JSON/YAML task files and validates against schema.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import jsonschema
import yaml

from src.schemas import get_task_file_schema_path

# Maximum task file size (1MB)
MAX_TASK_FILE_SIZE = 1024 * 1024


class TaskFileValidationError(Exception):
    """Raised when task file validation fails."""

    def __init__(
        self,
        message: str,
        error_type: str = "validation_error",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.error_type = error_type
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON output."""
        return {
            "type": self.error_type,
            "message": str(self),
            "details": self.details,
        }


@dataclass
class TaskTarget:
    """Target configuration for task execution."""

    files: List[str] = field(default_factory=list)
    changed_only: bool = False
    exclude: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "TaskTarget":
        """Create from dictionary."""
        if not data:
            return cls()

        files = data.get("files", [])
        if isinstance(files, str):
            files = [files]

        return cls(
            files=files,
            changed_only=data.get("changed_only", False),
            exclude=data.get("exclude", []),
        )


@dataclass
class TaskOptions:
    """Options for task execution."""

    timeout: Optional[Union[int, str]] = None
    profile: str = "safe"
    agents: List[str] = field(default_factory=list)
    provider: Optional[str] = None
    verbose: bool = False
    dry_run: bool = False
    extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "TaskOptions":
        """Create from dictionary."""
        if not data:
            return cls()

        known_keys = {"timeout", "profile", "agents", "provider", "verbose", "dry_run"}
        extra = {k: v for k, v in data.items() if k not in known_keys}

        return cls(
            timeout=data.get("timeout"),
            profile=data.get("profile", "safe"),
            agents=data.get("agents", []),
            provider=data.get("provider"),
            verbose=data.get("verbose", False),
            dry_run=data.get("dry_run", False),
            extra=extra,
        )


@dataclass
class TaskOutput:
    """Output configuration for task execution."""

    format: str = "json"
    include_diff: bool = True
    include_logs: bool = True
    file: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "TaskOutput":
        """Create from dictionary."""
        if not data:
            return cls()

        return cls(
            format=data.get("format", "json"),
            include_diff=data.get("include_diff", True),
            include_logs=data.get("include_logs", True),
            file=data.get("file"),
        )


@dataclass
class TaskDefinition:
    """Task definition from task file."""

    type: str
    target: TaskTarget = field(default_factory=TaskTarget)
    options: TaskOptions = field(default_factory=TaskOptions)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskDefinition":
        """Create from dictionary."""
        return cls(
            type=data["type"],
            target=TaskTarget.from_dict(data.get("target")),
            options=TaskOptions.from_dict(data.get("options")),
        )


@dataclass
class TaskFile:
    """Parsed and validated task file."""

    version: str
    task: TaskDefinition
    output: TaskOutput = field(default_factory=TaskOutput)
    metadata: Dict[str, Any] = field(default_factory=dict)
    source_path: Optional[Path] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any], source_path: Optional[Path] = None) -> "TaskFile":
        """Create from dictionary."""
        return cls(
            version=data["version"],
            task=TaskDefinition.from_dict(data["task"]),
            output=TaskOutput.from_dict(data.get("output")),
            metadata=data.get("metadata", {}),
            source_path=source_path,
        )

    @classmethod
    def from_file(cls, path: Union[str, Path]) -> "TaskFile":
        """Load and validate task file from path."""
        parser = TaskFileParser()
        return parser.parse(path)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "version": self.version,
            "task": {
                "type": self.task.type,
                "target": {
                    "files": self.task.target.files,
                    "changed_only": self.task.target.changed_only,
                    "exclude": self.task.target.exclude,
                },
                "options": {
                    "timeout": self.task.options.timeout,
                    "profile": self.task.options.profile,
                    "agents": self.task.options.agents,
                    "provider": self.task.options.provider,
                    "verbose": self.task.options.verbose,
                    "dry_run": self.task.options.dry_run,
                    **self.task.options.extra,
                },
            },
            "output": {
                "format": self.output.format,
                "include_diff": self.output.include_diff,
                "include_logs": self.output.include_logs,
                "file": self.output.file,
            },
            "metadata": self.metadata,
        }


class TaskFileParser:
    """Parser and validator for task files."""

    def __init__(self):
        self._schema: Optional[Dict[str, Any]] = None

    @property
    def schema(self) -> Dict[str, Any]:
        """Lazy-load JSON schema."""
        if self._schema is None:
            schema_path = get_task_file_schema_path()
            with open(schema_path, encoding="utf-8") as f:
                self._schema = json.load(f)
        return self._schema

    def parse(self, path: Union[str, Path]) -> TaskFile:
        """Parse and validate task file.

        Args:
            path: Path to task file (JSON or YAML)

        Returns:
            Validated TaskFile object

        Raises:
            TaskFileValidationError: If file is invalid
        """
        path = Path(path)

        # Check file exists
        if not path.exists():
            raise TaskFileValidationError(
                f"Task file not found: {path}",
                error_type="file_not_found",
                details={"path": str(path)},
            )

        # Check file size
        file_size = path.stat().st_size
        if file_size > MAX_TASK_FILE_SIZE:
            raise TaskFileValidationError(
                f"Task file too large: {file_size} bytes (max: {MAX_TASK_FILE_SIZE})",
                error_type="file_too_large",
                details={"size": file_size, "max_size": MAX_TASK_FILE_SIZE},
            )

        # Read and decode file
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as e:
            raise TaskFileValidationError(
                f"Invalid encoding (UTF-8 required): {e}",
                error_type="encoding_error",
                details={"encoding": "utf-8", "error": str(e)},
            )

        # Parse content based on extension
        data = self._parse_content(content, path)

        # Validate against schema
        self._validate_schema(data, path)

        # Check for circular dependencies (if applicable)
        self._check_circular_dependencies(data)

        return TaskFile.from_dict(data, source_path=path)

    def _parse_content(self, content: str, path: Path) -> Dict[str, Any]:
        """Parse content as JSON or YAML."""
        suffix = path.suffix.lower()

        if suffix in (".json",):
            try:
                return json.loads(content)
            except json.JSONDecodeError as e:
                raise TaskFileValidationError(
                    f"Invalid JSON syntax: {e.msg}",
                    error_type="parse_error",
                    details={
                        "format": "json",
                        "line": e.lineno,
                        "column": e.colno,
                        "message": e.msg,
                    },
                )

        elif suffix in (".yaml", ".yml"):
            try:
                return yaml.safe_load(content)
            except yaml.YAMLError as e:
                raise TaskFileValidationError(
                    f"Invalid YAML syntax: {e}",
                    error_type="parse_error",
                    details={"format": "yaml", "message": str(e)},
                )

        else:
            # Try JSON first, then YAML
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                try:
                    return yaml.safe_load(content)
                except yaml.YAMLError:
                    raise TaskFileValidationError(
                        f"Unable to parse file as JSON or YAML: {path}",
                        error_type="parse_error",
                        details={"path": str(path), "format": "unknown"},
                    )

    def _validate_schema(self, data: Dict[str, Any], path: Path) -> None:
        """Validate data against JSON schema."""
        try:
            jsonschema.validate(instance=data, schema=self.schema)
        except jsonschema.ValidationError as e:
            raise TaskFileValidationError(
                f"Schema validation failed: {e.message}",
                error_type="schema_validation_error",
                details={
                    "path": str(path),
                    "schema_path": list(e.absolute_schema_path),
                    "instance_path": list(e.absolute_path),
                    "message": e.message,
                },
            )

    def _check_circular_dependencies(self, data: Dict[str, Any]) -> None:
        """Check for circular dependencies in task configuration.

        Currently a placeholder - can be extended for complex task graphs.
        """
        # For single-task files, no circular dependencies possible
        # This is reserved for future multi-task/pipeline support
        pass

    def validate_only(self, path: Union[str, Path]) -> bool:
        """Validate task file without parsing.

        Args:
            path: Path to task file

        Returns:
            True if valid

        Raises:
            TaskFileValidationError: If file is invalid
        """
        self.parse(path)
        return True
