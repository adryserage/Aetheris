"""
File Skills for Aetheris (v3.0)

Provides file operation skills:
- read_file: Read file contents
- write_file: Write/append to files
- search_files: Search for files by pattern
"""

import fnmatch
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.skills.base_skill import (
    SandboxValidator,
    Skill,
    SkillParameter,
    SkillResult,
    SkillResultStatus,
)


@dataclass
class ReadFileSkill(Skill):
    """Skill to read file contents"""

    name: str = "read_file"
    description: str = "Read the contents of a file"
    parameters: List[SkillParameter] = field(
        default_factory=lambda: [
            SkillParameter(
                name="path",
                description="Path to the file to read",
                param_type="string",
                required=True,
            ),
            SkillParameter(
                name="start_line",
                description="Starting line number (1-based)",
                param_type="integer",
                required=False,
                default=1,
            ),
            SkillParameter(
                name="end_line",
                description="Ending line number (inclusive)",
                param_type="integer",
                required=False,
            ),
        ]
    )
    requires_confirmation: bool = False
    sandbox: Optional[SandboxValidator] = None

    def __post_init__(self) -> None:
        if self.sandbox is None:
            self.sandbox = SandboxValidator()

    async def execute(self, arguments: Dict[str, Any]) -> SkillResult:
        """Read file contents"""
        # Validate arguments
        error = self.validate_arguments(arguments)
        if error:
            return SkillResult(status=SkillResultStatus.ERROR, error=error)

        path_str = arguments["path"]
        start_line = arguments.get("start_line", 1)
        end_line = arguments.get("end_line")

        # Validate path against sandbox
        if self.sandbox:
            sandbox_error = self.sandbox.validate_path(path_str)
            if sandbox_error:
                return SkillResult(status=SkillResultStatus.DENIED, error=sandbox_error)

        path = Path(path_str)

        if not path.exists():
            return SkillResult(
                status=SkillResultStatus.ERROR,
                error=f"File not found: {path_str}",
            )

        if not path.is_file():
            return SkillResult(
                status=SkillResultStatus.ERROR,
                error=f"Not a file: {path_str}",
            )

        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()

            # Apply line range
            if end_line:
                lines = lines[start_line - 1 : end_line]
            elif start_line > 1:
                lines = lines[start_line - 1 :]

            content = "".join(lines)

            return SkillResult(
                status=SkillResultStatus.SUCCESS,
                output=content,
                data={
                    "path": str(path),
                    "lines_read": len(lines),
                    "start_line": start_line,
                    "end_line": end_line or (start_line + len(lines) - 1),
                },
            )
        except PermissionError:
            return SkillResult(
                status=SkillResultStatus.DENIED,
                error=f"Permission denied: {path_str}",
            )
        except Exception as e:
            return SkillResult(
                status=SkillResultStatus.ERROR,
                error=f"Failed to read file: {e}",
            )


@dataclass
class WriteFileSkill(Skill):
    """Skill to write file contents"""

    name: str = "write_file"
    description: str = "Write content to a file (creates or overwrites)"
    parameters: List[SkillParameter] = field(
        default_factory=lambda: [
            SkillParameter(
                name="path",
                description="Path to the file to write",
                param_type="string",
                required=True,
            ),
            SkillParameter(
                name="content",
                description="Content to write to the file",
                param_type="string",
                required=True,
            ),
            SkillParameter(
                name="mode",
                description="Write mode: 'overwrite' or 'append'",
                param_type="string",
                required=False,
                default="overwrite",
                enum=["overwrite", "append"],
            ),
        ]
    )
    requires_confirmation: bool = True  # Writing requires confirmation
    sandbox: Optional[SandboxValidator] = None

    def __post_init__(self) -> None:
        if self.sandbox is None:
            self.sandbox = SandboxValidator()

    async def execute(self, arguments: Dict[str, Any]) -> SkillResult:
        """Write content to file"""
        # Validate arguments
        error = self.validate_arguments(arguments)
        if error:
            return SkillResult(status=SkillResultStatus.ERROR, error=error)

        path_str = arguments["path"]
        content = arguments["content"]
        mode = arguments.get("mode", "overwrite")

        # Validate path against sandbox
        if self.sandbox:
            sandbox_error = self.sandbox.validate_path(path_str)
            if sandbox_error:
                return SkillResult(status=SkillResultStatus.DENIED, error=sandbox_error)

        path = Path(path_str)

        try:
            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)

            write_mode = "a" if mode == "append" else "w"
            with open(path, write_mode, encoding="utf-8") as f:
                f.write(content)

            return SkillResult(
                status=SkillResultStatus.SUCCESS,
                output=f"Successfully wrote {len(content)} bytes to {path_str}",
                data={
                    "path": str(path),
                    "bytes_written": len(content),
                    "mode": mode,
                },
            )
        except PermissionError:
            return SkillResult(
                status=SkillResultStatus.DENIED,
                error=f"Permission denied: {path_str}",
            )
        except Exception as e:
            return SkillResult(
                status=SkillResultStatus.ERROR,
                error=f"Failed to write file: {e}",
            )


@dataclass
class SearchFilesSkill(Skill):
    """Skill to search for files"""

    name: str = "search_files"
    description: str = "Search for files by glob pattern and optionally by content"
    parameters: List[SkillParameter] = field(
        default_factory=lambda: [
            SkillParameter(
                name="pattern",
                description="Glob pattern to match files (e.g., '**/*.py')",
                param_type="string",
                required=True,
            ),
            SkillParameter(
                name="content_pattern",
                description="Regex pattern to search in file contents",
                param_type="string",
                required=False,
            ),
            SkillParameter(
                name="directory",
                description="Directory to search in (default: current directory)",
                param_type="string",
                required=False,
            ),
            SkillParameter(
                name="max_results",
                description="Maximum number of results to return",
                param_type="integer",
                required=False,
                default=100,
            ),
        ]
    )
    requires_confirmation: bool = False
    sandbox: Optional[SandboxValidator] = None

    def __post_init__(self) -> None:
        if self.sandbox is None:
            self.sandbox = SandboxValidator()

    async def execute(self, arguments: Dict[str, Any]) -> SkillResult:
        """Search for files matching pattern"""
        # Validate arguments
        error = self.validate_arguments(arguments)
        if error:
            return SkillResult(status=SkillResultStatus.ERROR, error=error)

        pattern = arguments["pattern"]
        content_pattern = arguments.get("content_pattern")
        directory = arguments.get("directory", ".")
        max_results = arguments.get("max_results", 100)

        # Validate directory against sandbox
        if self.sandbox:
            sandbox_error = self.sandbox.validate_path(directory)
            if sandbox_error:
                return SkillResult(status=SkillResultStatus.DENIED, error=sandbox_error)

        search_dir = Path(directory)
        if not search_dir.exists():
            return SkillResult(
                status=SkillResultStatus.ERROR,
                error=f"Directory not found: {directory}",
            )

        try:
            # Compile content regex if provided
            content_regex = None
            if content_pattern:
                try:
                    content_regex = re.compile(content_pattern)
                except re.error as e:
                    return SkillResult(
                        status=SkillResultStatus.ERROR,
                        error=f"Invalid regex pattern: {e}",
                    )

            # Find files matching glob pattern
            matches: List[Dict[str, Any]] = []
            for path in search_dir.glob(pattern):
                if len(matches) >= max_results:
                    break

                if not path.is_file():
                    continue

                # Apply sandbox validation
                if self.sandbox and not self.sandbox.is_path_allowed(path):
                    continue

                match_info: Dict[str, Any] = {"path": str(path)}

                # Search content if pattern provided
                if content_regex:
                    try:
                        with open(path, "r", encoding="utf-8", errors="replace") as f:
                            content = f.read()
                            content_matches = list(content_regex.finditer(content))
                            if content_matches:
                                match_info["content_matches"] = len(content_matches)
                                # Include first few matches
                                match_info["match_previews"] = [
                                    m.group(0)[:100] for m in content_matches[:3]
                                ]
                            else:
                                continue  # Skip files without content match
                    except Exception:
                        continue  # Skip unreadable files

                matches.append(match_info)

            return SkillResult(
                status=SkillResultStatus.SUCCESS,
                output=f"Found {len(matches)} matching files",
                data={
                    "matches": matches,
                    "pattern": pattern,
                    "content_pattern": content_pattern,
                    "total_matches": len(matches),
                },
            )
        except Exception as e:
            return SkillResult(
                status=SkillResultStatus.ERROR,
                error=f"Search failed: {e}",
            )
