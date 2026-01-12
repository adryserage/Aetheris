"""
Task Runner for Headless Execution

Provides non-interactive, programmatic execution of Aetheris tasks.
"""

import asyncio
import io
import random
import signal
import time
import traceback
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

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
from src.runner.task_parser import TaskFile, TaskFileParser, TaskFileValidationError


@dataclass
class SecurityProfile:
    """Security profile for headless execution."""

    name: str
    allow_file_write: bool = True
    allow_file_delete: bool = False
    allow_network: bool = True
    allow_auto_fix: bool = False
    require_confirmation: List[str] = field(default_factory=list)

    @classmethod
    def get_profile(cls, name: str) -> "SecurityProfile":
        """Get predefined security profile by name."""
        profiles = {
            "safe": cls(
                name="safe",
                allow_file_write=True,
                allow_file_delete=False,
                allow_network=True,
                allow_auto_fix=False,
                require_confirmation=["delete", "overwrite", "external_api"],
            ),
            "ci": cls(
                name="ci",
                allow_file_write=True,
                allow_file_delete=False,
                allow_network=True,
                allow_auto_fix=True,
                require_confirmation=[],
            ),
            "dev": cls(
                name="dev",
                allow_file_write=True,
                allow_file_delete=True,
                allow_network=True,
                allow_auto_fix=True,
                require_confirmation=[],
            ),
            "unrestricted": cls(
                name="unrestricted",
                allow_file_write=True,
                allow_file_delete=True,
                allow_network=True,
                allow_auto_fix=True,
                require_confirmation=[],
            ),
        }
        return profiles.get(name, profiles["safe"])


@dataclass
class ExecutionContext:
    """Context for task execution."""

    task_file: TaskFile
    profile: SecurityProfile
    headless: bool = True
    dry_run: bool = False
    seed: Optional[int] = None
    no_timestamps: bool = False
    verbose: bool = False
    timeout_seconds: Optional[float] = None
    logs: List[str] = field(default_factory=list)
    blocked_operations: List[BlockedOperation] = field(default_factory=list)
    _interrupted: bool = False
    _start_time: float = 0.0

    def log(self, message: str, level: str = "INFO") -> None:
        """Add log message."""
        if self.verbose or level in ("ERROR", "WARNING"):
            self.logs.append(f"{level}: {message}")

    def block_operation(self, operation: str, reason: str) -> None:
        """Record a blocked operation."""
        self.blocked_operations.append(
            BlockedOperation(
                operation=operation,
                reason=reason,
                profile=self.profile.name,
            )
        )
        self.log(f"Blocked: {operation} - {reason}", "WARNING")

    @property
    def elapsed_ms(self) -> int:
        """Get elapsed time in milliseconds."""
        if self._start_time == 0:
            return 0
        return int((time.time() - self._start_time) * 1000)


class TaskRunner:
    """Non-interactive task runner for headless execution."""

    def __init__(
        self,
        task_file: Optional[TaskFile] = None,
        task_file_path: Optional[str] = None,
        profile: Optional[str] = None,
        headless: bool = True,
        dry_run: bool = False,
        seed: Optional[int] = None,
        no_timestamps: bool = False,
        verbose: bool = False,
        timeout: Optional[str] = None,
        output_file: Optional[str] = None,
    ):
        """Initialize task runner.

        Args:
            task_file: Pre-parsed TaskFile object
            task_file_path: Path to task file (alternative to task_file)
            profile: Security profile name (overrides task file)
            headless: Run in headless mode (no TTY required)
            dry_run: Validate without executing
            seed: Random seed for reproducibility
            no_timestamps: Disable timestamps in output
            verbose: Enable verbose logging
            timeout: Execution timeout (overrides task file)
            output_file: Write output to file (overrides task file)
        """
        self._task_file = task_file
        self._task_file_path = task_file_path
        self._profile_override = profile
        self._headless = headless
        self._dry_run = dry_run
        self._seed = seed
        self._no_timestamps = no_timestamps
        self._verbose = verbose
        self._timeout_override = timeout
        self._output_file = output_file

        self._context: Optional[ExecutionContext] = None
        self._original_handlers: Dict[int, Any] = {}
        self._stdout_capture = io.StringIO()
        self._stderr_capture = io.StringIO()

    def _parse_timeout(self, timeout_value: Optional[Any]) -> Optional[float]:
        """Parse timeout value to seconds."""
        if timeout_value is None:
            return None

        if isinstance(timeout_value, (int, float)):
            return float(timeout_value) if timeout_value > 0 else None

        if isinstance(timeout_value, str):
            timeout_str = timeout_value.lower().strip()
            if timeout_str in ("0", "no-limit", "unlimited"):
                return None

            # Parse duration strings like "30m", "2h"
            if timeout_str.endswith("s"):
                return float(timeout_str[:-1])
            elif timeout_str.endswith("m"):
                return float(timeout_str[:-1]) * 60
            elif timeout_str.endswith("h"):
                return float(timeout_str[:-1]) * 3600
            else:
                return float(timeout_str)

        return None

    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        if not self._headless:
            return

        def handler(signum: int, frame: Any) -> None:
            if self._context:
                self._context._interrupted = True
                self._context.log(f"Received signal {signum}, shutting down...", "WARNING")

        # Only setup handlers if we're the main process
        if hasattr(signal, "SIGINT"):
            self._original_handlers[signal.SIGINT] = signal.signal(signal.SIGINT, handler)
        if hasattr(signal, "SIGTERM"):
            self._original_handlers[signal.SIGTERM] = signal.signal(signal.SIGTERM, handler)

    def _restore_signal_handlers(self) -> None:
        """Restore original signal handlers."""
        for sig, handler in self._original_handlers.items():
            try:
                signal.signal(sig, handler)
            except (ValueError, OSError):
                pass
        self._original_handlers.clear()

    @contextmanager
    def _capture_output(self):
        """Context manager to capture stdout/stderr."""
        self._stdout_capture = io.StringIO()
        self._stderr_capture = io.StringIO()

        with redirect_stdout(self._stdout_capture), redirect_stderr(self._stderr_capture):
            yield

    def _get_version(self) -> str:
        """Get Aetheris version."""
        try:
            from src import __version__

            return __version__
        except ImportError:
            try:
                import tomllib

                pyproject = Path(__file__).parent.parent.parent / "pyproject.toml"
                if pyproject.exists():
                    with open(pyproject, "rb") as f:
                        data = tomllib.load(f)
                        return data.get("project", {}).get("version", "unknown")
            except Exception:
                pass
        return "unknown"

    async def execute(self) -> ExecutionResult:
        """Execute the task.

        Returns:
            ExecutionResult with status, exit code, and results
        """
        start_time = time.time()

        try:
            # Parse task file if needed
            if self._task_file is None:
                if self._task_file_path is None:
                    return ExecutionResult.create_error(
                        duration_ms=0,
                        error_info=ErrorInfo(
                            type="configuration_error",
                            message="No task file provided",
                        ),
                    )
                try:
                    parser = TaskFileParser()
                    self._task_file = parser.parse(self._task_file_path)
                except TaskFileValidationError as e:
                    return ExecutionResult.create_error(
                        duration_ms=int((time.time() - start_time) * 1000),
                        error_info=ErrorInfo(
                            type=e.error_type,
                            message=str(e),
                            details=e.details,
                        ),
                    )

            # Setup execution context
            profile_name = self._profile_override or self._task_file.task.options.profile
            profile = SecurityProfile.get_profile(profile_name)

            timeout = self._parse_timeout(
                self._timeout_override or self._task_file.task.options.timeout
            )

            self._context = ExecutionContext(
                task_file=self._task_file,
                profile=profile,
                headless=self._headless,
                dry_run=self._dry_run or self._task_file.task.options.dry_run,
                seed=self._seed,
                no_timestamps=self._no_timestamps,
                verbose=self._verbose or self._task_file.task.options.verbose,
                timeout_seconds=timeout,
            )
            self._context._start_time = start_time

            # Setup random seed for reproducibility
            if self._context.seed is not None:
                random.seed(self._context.seed)

            # Setup signal handlers
            self._setup_signal_handlers()

            self._context.log(f"Starting task: {self._task_file.task.type}")
            self._context.log(f"Security profile: {profile.name}")

            # Dry run - just validate
            if self._context.dry_run:
                self._context.log("Dry run mode - validation only")
                return ExecutionResult.success(
                    duration_ms=self._context.elapsed_ms,
                    task=TaskInfo(
                        type=self._task_file.task.type,
                        source_file=(
                            str(self._task_file.source_path)
                            if self._task_file.source_path
                            else None
                        ),
                    ),
                    logs=self._context.logs,
                    version=self._get_version(),
                    metadata=self._task_file.metadata,
                )

            # Execute with timeout
            try:
                if timeout:
                    result = await asyncio.wait_for(
                        self._execute_task(),
                        timeout=timeout,
                    )
                else:
                    result = await self._execute_task()

                # Check for interruption
                if self._context._interrupted:
                    return ExecutionResult.interrupted(
                        duration_ms=self._context.elapsed_ms,
                        task=TaskInfo(
                            type=self._task_file.task.type,
                            source_file=(
                                str(self._task_file.source_path)
                                if self._task_file.source_path
                                else None
                            ),
                        ),
                        results=result.results if hasattr(result, "results") else None,
                        logs=self._context.logs,
                        version=self._get_version(),
                        metadata=self._task_file.metadata,
                    )

                # Check for blocked operations
                if self._context.blocked_operations:
                    return ExecutionResult.blocked(
                        duration_ms=self._context.elapsed_ms,
                        blocked_operations=self._context.blocked_operations,
                        task=TaskInfo(
                            type=self._task_file.task.type,
                            source_file=(
                                str(self._task_file.source_path)
                                if self._task_file.source_path
                                else None
                            ),
                        ),
                        logs=self._context.logs,
                        version=self._get_version(),
                        metadata=self._task_file.metadata,
                    )

                return result

            except asyncio.TimeoutError:
                self._context.log("Execution timed out", "ERROR")
                return ExecutionResult.timeout(
                    duration_ms=self._context.elapsed_ms,
                    task=TaskInfo(
                        type=self._task_file.task.type,
                        source_file=(
                            str(self._task_file.source_path)
                            if self._task_file.source_path
                            else None
                        ),
                    ),
                    logs=self._context.logs,
                    version=self._get_version(),
                    metadata=self._task_file.metadata,
                )

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            return ExecutionResult.create_error(
                duration_ms=duration_ms,
                error_info=ErrorInfo(
                    type=type(e).__name__,
                    message=str(e),
                    traceback=traceback.format_exc() if self._verbose else None,
                ),
                task=(
                    TaskInfo(
                        type=self._task_file.task.type if self._task_file else "unknown",
                        source_file=(
                            str(self._task_file.source_path)
                            if self._task_file and self._task_file.source_path
                            else None
                        ),
                    )
                    if self._task_file
                    else None
                ),
                logs=self._context.logs if self._context else [],
                version=self._get_version(),
            )

        finally:
            self._restore_signal_handlers()

    async def _execute_task(self) -> ExecutionResult:
        """Execute the actual task.

        This is where we dispatch to the appropriate Aetheris command.
        """
        assert self._task_file is not None
        assert self._context is not None

        task_type = self._task_file.task.type
        self._context.log(f"Executing task type: {task_type}")

        # Import here to avoid circular imports
        from src.core.config import load_env_file

        # Load environment
        load_env_file()

        if task_type == "analysis":
            return await self._execute_analysis()
        elif task_type == "fix":
            return await self._execute_fix()
        elif task_type == "stats":
            return await self._execute_stats()
        elif task_type == "cleanup":
            return await self._execute_cleanup()
        elif task_type == "validate-package":
            return await self._execute_validate_package()
        else:
            return ExecutionResult.create_error(
                duration_ms=self._context.elapsed_ms,
                error_info=ErrorInfo(
                    type="unsupported_task",
                    message=f"Unsupported task type: {task_type}",
                    details={
                        "supported": ["analysis", "fix", "stats", "cleanup", "validate-package"]
                    },
                ),
                task=TaskInfo(type=task_type),
                logs=self._context.logs,
                version=self._get_version(),
            )

    async def _execute_analysis(self) -> ExecutionResult:
        """Execute analysis task."""
        from src.core.analyzer import CodeAnalyzer
        from src.core.config import AnalysisConfig, TimeoutConfig

        assert self._task_file is not None
        assert self._context is not None

        self._context.log("Initializing CodeAnalyzer...")

        # Build config from task target
        target = self._task_file.task.target

        # Parse timeout - TimeoutConfig expects (value, enabled)
        timeout_config = None
        if self._context.timeout_seconds:
            timeout_config = TimeoutConfig(
                value=int(self._context.timeout_seconds),
                enabled=True,
            )

        config = AnalysisConfig(
            analyze_changed_files_only=target.changed_only,
            changed_files=target.files if target.files else [],
            pr_number=None,
            timeout_config=timeout_config,
        )

        try:
            analyzer = CodeAnalyzer(config=config)
            self._context.log("Starting analysis...")

            # Run analysis
            await analyzer.run()

            self._context.log("Analysis completed successfully")

            # Build results summary
            results = ResultsSummary(
                issues_found=getattr(analyzer, "total_issues", 0),
                critical=getattr(analyzer, "critical_count", 0),
                high=getattr(analyzer, "high_count", 0),
                medium=getattr(analyzer, "medium_count", 0),
                low=getattr(analyzer, "low_count", 0),
                reports=["docs/analyses/quality_assurance_report.md"],
            )

            return ExecutionResult.success(
                duration_ms=self._context.elapsed_ms,
                task=TaskInfo(
                    type="analysis",
                    files_processed=getattr(analyzer, "files_analyzed", 0),
                    source_file=(
                        str(self._task_file.source_path) if self._task_file.source_path else None
                    ),
                ),
                results=results,
                logs=self._context.logs,
                version=self._get_version(),
                metadata=self._task_file.metadata,
            )

        except Exception as e:
            self._context.log(f"Analysis failed: {e}", "ERROR")
            return ExecutionResult.create_error(
                duration_ms=self._context.elapsed_ms,
                error_info=ErrorInfo(
                    type="analysis_error",
                    message=str(e),
                    traceback=traceback.format_exc() if self._context.verbose else None,
                ),
                task=TaskInfo(type="analysis"),
                logs=self._context.logs,
                version=self._get_version(),
            )

    async def _execute_fix(self) -> ExecutionResult:
        """Execute fix task."""
        assert self._task_file is not None
        assert self._context is not None

        # Check if auto-fix is allowed
        if not self._context.profile.allow_auto_fix:
            self._context.block_operation(
                "auto_fix",
                f"Auto-fix not allowed by '{self._context.profile.name}' profile",
            )
            return ExecutionResult.blocked(
                duration_ms=self._context.elapsed_ms,
                blocked_operations=self._context.blocked_operations,
                task=TaskInfo(type="fix"),
                logs=self._context.logs,
                version=self._get_version(),
            )

        self._context.log("Fix task not fully implemented in headless mode")
        return ExecutionResult.success(
            duration_ms=self._context.elapsed_ms,
            task=TaskInfo(type="fix"),
            logs=self._context.logs,
            version=self._get_version(),
            metadata=self._task_file.metadata,
        )

    async def _execute_stats(self) -> ExecutionResult:
        """Execute stats task."""
        from src.services.statistics_service import StatisticsService

        assert self._task_file is not None
        assert self._context is not None

        self._context.log("Generating statistics...")

        try:
            stats_service = StatisticsService()
            # aggregate_statistics returns (ProjectAggregation | None, ProjectAggregation | None, dict)
            stats = stats_service.aggregate_statistics()

            return ExecutionResult.success(
                duration_ms=self._context.elapsed_ms,
                task=TaskInfo(type="stats"),
                results=ResultsSummary(
                    extra={"statistics": stats[0].__dict__ if stats[0] else {}} if stats else {},
                ),
                logs=self._context.logs,
                version=self._get_version(),
                metadata=self._task_file.metadata,
            )
        except Exception as e:
            self._context.log(f"Stats failed: {e}", "ERROR")
            return ExecutionResult.create_error(
                duration_ms=self._context.elapsed_ms,
                error_info=ErrorInfo(
                    type="stats_error",
                    message=str(e),
                ),
                task=TaskInfo(type="stats"),
                logs=self._context.logs,
                version=self._get_version(),
            )

    async def _execute_cleanup(self) -> ExecutionResult:
        """Execute cleanup task."""
        from src.models.cleanup_models import CleanupConfig
        from src.services.cleanup_service import CleanupService

        assert self._task_file is not None
        assert self._context is not None

        self._context.log("Running cleanup...")

        try:
            # Create cleanup config with dry_run setting
            cleanup_config = CleanupConfig(dry_run=self._context.dry_run)
            cleanup_service = CleanupService(config=cleanup_config)

            # Get target directory from task file or use current directory
            target_dir = "."
            if self._task_file.task.target and self._task_file.task.target.files:
                target_dir = self._task_file.task.target.files[0]

            result = cleanup_service.cleanup(target_dir)

            return ExecutionResult.success(
                duration_ms=self._context.elapsed_ms,
                task=TaskInfo(type="cleanup"),
                results=ResultsSummary(
                    extra=(
                        {"cleaned": result.__dict__ if hasattr(result, "__dict__") else {}}
                        if result
                        else {}
                    ),
                ),
                logs=self._context.logs,
                version=self._get_version(),
                metadata=self._task_file.metadata,
            )
        except Exception as e:
            self._context.log(f"Cleanup failed: {e}", "ERROR")
            return ExecutionResult.create_error(
                duration_ms=self._context.elapsed_ms,
                error_info=ErrorInfo(
                    type="cleanup_error",
                    message=str(e),
                ),
                task=TaskInfo(type="cleanup"),
                logs=self._context.logs,
                version=self._get_version(),
            )

    async def _execute_validate_package(self) -> ExecutionResult:
        """Execute validate-package task."""
        from src.services.secret_scanner import SecretScanner

        assert self._task_file is not None
        assert self._context is not None

        self._context.log("Validating package...")

        try:
            scanner = SecretScanner()
            # scan_directory requires a directory path
            target_dir = "."
            if self._task_file.task.target and self._task_file.task.target.files:
                target_dir = self._task_file.task.target.files[0]

            findings = scanner.scan_directory(target_dir)

            has_issues = len(findings) > 0

            return ExecutionResult(
                status=ExecutionStatus.ERROR if has_issues else ExecutionStatus.SUCCESS,
                exit_code=ExitCode.ERROR if has_issues else ExitCode.SUCCESS,
                duration_ms=self._context.elapsed_ms,
                task=TaskInfo(type="validate-package"),
                results=ResultsSummary(
                    issues_found=len(findings),
                    extra={
                        "findings": [
                            f.to_dict() if hasattr(f, "to_dict") else str(f) for f in findings
                        ]
                    },
                ),
                logs=self._context.logs,
                version=self._get_version(),
                metadata=self._task_file.metadata,
            )
        except Exception as e:
            self._context.log(f"Validation failed: {e}", "ERROR")
            return ExecutionResult.create_error(
                duration_ms=self._context.elapsed_ms,
                error_info=ErrorInfo(
                    type="validation_error",
                    message=str(e),
                ),
                task=TaskInfo(type="validate-package"),
                logs=self._context.logs,
                version=self._get_version(),
            )


async def run_task(
    task_file_path: str,
    profile: Optional[str] = None,
    dry_run: bool = False,
    seed: Optional[int] = None,
    no_timestamps: bool = False,
    verbose: bool = False,
    timeout: Optional[str] = None,
    output_file: Optional[str] = None,
    output_format: str = "json",
) -> Tuple[ExecutionResult, int]:
    """Run a task file and return result.

    Convenience function for CLI integration.

    Args:
        task_file_path: Path to task file
        profile: Security profile override
        dry_run: Validate without executing
        seed: Random seed for reproducibility
        no_timestamps: Disable timestamps
        verbose: Enable verbose logging
        timeout: Execution timeout override
        output_file: Write output to file
        output_format: Output format (json/yaml)

    Returns:
        Tuple of (ExecutionResult, exit_code)
    """
    runner = TaskRunner(
        task_file_path=task_file_path,
        profile=profile,
        dry_run=dry_run,
        seed=seed,
        no_timestamps=no_timestamps,
        verbose=verbose,
        timeout=timeout,
        output_file=output_file,
    )

    result = await runner.execute()

    # Format and output
    formatter = OutputFormatter(
        format=output_format,
        include_timestamps=not no_timestamps,
        output_file=output_file,
    )
    formatter.output(result)

    return result, result.exit_code.value
