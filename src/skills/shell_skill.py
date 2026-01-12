"""
Shell Skill for Aetheris (v3.0)

Provides shell command execution with safety controls.
"""

import asyncio
import shlex
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

# Dangerous commands that should be blocked
BLOCKED_COMMANDS = [
    "rm -rf /",
    "rm -rf ~",
    "rm -rf /*",
    "sudo rm",
    "mkfs",
    "dd if=/dev/",
    ":(){:|:&};:",  # Fork bomb
    "chmod -R 777 /",
    "chown -R",
    "> /dev/sda",
    "wget | sh",
    "curl | bash",
    "curl | sh",
]

# Commands that require extra confirmation
DANGEROUS_PATTERNS = [
    "rm -rf",
    "rm -r",
    "sudo",
    "chmod",
    "chown",
    "kill",
    "pkill",
    "killall",
]


def is_command_safe(command: str) -> tuple[bool, Optional[str]]:
    """Check if a command is safe to execute. Returns (is_safe, reason)."""
    command_lower = command.lower().strip()

    # Check for blocked commands
    for blocked in BLOCKED_COMMANDS:
        if blocked in command_lower:
            return False, f"Blocked command pattern: {blocked}"

    return True, None


def is_command_dangerous(command: str) -> bool:
    """Check if a command requires extra confirmation."""
    command_lower = command.lower().strip()
    return any(pattern in command_lower for pattern in DANGEROUS_PATTERNS)


@dataclass
class ExecuteCommandSkill(Skill):
    """Skill to execute shell commands"""

    name: str = "execute_command"
    description: str = "Execute a shell command and return its output"
    parameters: List[SkillParameter] = field(
        default_factory=lambda: [
            SkillParameter(
                name="command",
                description="The shell command to execute",
                param_type="string",
                required=True,
            ),
            SkillParameter(
                name="working_directory",
                description="Directory to run the command in",
                param_type="string",
                required=False,
            ),
            SkillParameter(
                name="timeout",
                description="Timeout in seconds (default: 60)",
                param_type="integer",
                required=False,
                default=60,
            ),
        ]
    )
    requires_confirmation: bool = True
    sandbox: Optional[SandboxValidator] = None

    def __post_init__(self) -> None:
        if self.sandbox is None:
            self.sandbox = SandboxValidator()

    async def execute(self, arguments: Dict[str, Any]) -> SkillResult:
        """Execute shell command"""
        # Validate arguments
        error = self.validate_arguments(arguments)
        if error:
            return SkillResult(status=SkillResultStatus.ERROR, error=error)

        command = arguments["command"]
        working_dir = arguments.get("working_directory")
        timeout = arguments.get("timeout", 60)

        # Safety check
        is_safe, reason = is_command_safe(command)
        if not is_safe:
            return SkillResult(
                status=SkillResultStatus.DENIED,
                error=f"Command blocked for safety: {reason}",
            )

        # Validate working directory if provided
        if working_dir:
            if self.sandbox:
                sandbox_error = self.sandbox.validate_path(working_dir)
                if sandbox_error:
                    return SkillResult(
                        status=SkillResultStatus.DENIED,
                        error=sandbox_error,
                    )
            cwd = Path(working_dir)
            if not cwd.exists():
                return SkillResult(
                    status=SkillResultStatus.ERROR,
                    error=f"Working directory not found: {working_dir}",
                )
        else:
            cwd = Path.cwd()

        try:
            # Execute command
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(cwd),
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout,
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return SkillResult(
                    status=SkillResultStatus.ERROR,
                    error=f"Command timed out after {timeout} seconds",
                )

            stdout_str = stdout.decode("utf-8", errors="replace")
            stderr_str = stderr.decode("utf-8", errors="replace")

            if process.returncode == 0:
                return SkillResult(
                    status=SkillResultStatus.SUCCESS,
                    output=stdout_str or "Command executed successfully (no output)",
                    data={
                        "command": command,
                        "return_code": process.returncode,
                        "stdout": stdout_str,
                        "stderr": stderr_str,
                    },
                )
            else:
                return SkillResult(
                    status=SkillResultStatus.ERROR,
                    output=stderr_str or stdout_str,
                    error=f"Command failed with exit code {process.returncode}",
                    data={
                        "command": command,
                        "return_code": process.returncode,
                        "stdout": stdout_str,
                        "stderr": stderr_str,
                    },
                )

        except PermissionError:
            return SkillResult(
                status=SkillResultStatus.DENIED,
                error="Permission denied to execute command",
            )
        except Exception as e:
            return SkillResult(
                status=SkillResultStatus.ERROR,
                error=f"Failed to execute command: {e}",
            )

    def is_dangerous(self, command: str) -> bool:
        """Check if command requires extra confirmation"""
        return is_command_dangerous(command)
