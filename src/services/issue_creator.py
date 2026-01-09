"""
GitHub Issue Creator Service

Creates GitHub issues from Aetheris analysis reports using the `gh` CLI tool.
Supports dry-run mode, custom labels, assignees, deduplication, and progress feedback.
"""

import json
import os
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Set, Tuple

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


# =============================================================================
# Rate Limiting Constants (T038)
# =============================================================================

MAX_RETRIES = 3
BASE_DELAY_SECONDS = 2.0


# =============================================================================
# Data Classes (T003)
# =============================================================================


@dataclass
class ExtractedBug:
    """Bug information extracted from an analysis report."""

    source_file: str
    report_file: str
    bug_type: str  # 'security', 'risk', 'inconsistency', 'suggestion'
    severity: str  # 'critical', 'high', 'medium', 'low'
    title: str
    description: str
    recommendation: str = ""
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None


@dataclass
class IssueOptions:
    """Configuration options for the issues command."""

    dry_run: bool = False
    labels: List[str] = field(default_factory=list)
    assignee: Optional[str] = None
    repo: Optional[str] = None
    from_report: Optional[str] = None


@dataclass
class IssueToCreate:
    """Issue prepared for GitHub creation."""

    title: str
    body: str
    labels: List[str]
    assignee: Optional[str]
    bug: ExtractedBug


@dataclass
class IssueResult:
    """Result of a single issue creation attempt."""

    status: str  # 'created', 'skipped', 'failed'
    title: str
    url: Optional[str] = None
    error: Optional[str] = None
    bug: Optional[ExtractedBug] = None


@dataclass
class IssuesSummary:
    """Final summary of the issues command execution."""

    total_bugs: int
    created: int
    skipped: int
    failed: int
    results: List[IssueResult] = field(default_factory=list)
    duration_seconds: float = 0.0


# =============================================================================
# Issue Creator Service
# =============================================================================


class IssueCreator:
    """Service for creating GitHub issues from Aetheris analysis reports."""

    def __init__(self, repo: Optional[str] = None, output_dir: str = "docs/analyses"):
        self.repo = repo
        self.output_dir = output_dir
        self.existing_titles: Set[str] = set()

    # -------------------------------------------------------------------------
    # T004: Validate gh CLI
    # -------------------------------------------------------------------------

    async def validate_gh_cli(self) -> Tuple[bool, str]:
        """Check if gh CLI is installed and authenticated."""
        try:
            # Check if gh is installed
            result = subprocess.run(
                ["gh", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                return False, "gh CLI is not installed. Install from https://cli.github.com/"

            # Check authentication
            result = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                return False, "gh CLI is not authenticated. Run 'gh auth login' first."

            return True, "gh CLI is ready"

        except FileNotFoundError:
            return False, "gh CLI is not installed. Install from https://cli.github.com/"
        except subprocess.TimeoutExpired:
            return False, "gh CLI check timed out"
        except Exception as e:
            return False, f"Error checking gh CLI: {e}"

    # -------------------------------------------------------------------------
    # T005: Run gh command helper
    # -------------------------------------------------------------------------

    def _run_gh_command(
        self,
        args: List[str],
        repo: Optional[str] = None,
    ) -> Tuple[bool, str, str]:
        """
        Execute a gh CLI command with error handling.

        Returns:
            Tuple of (success, stdout, stderr)
        """
        cmd = ["gh"] + args

        # Add repo flag if specified
        target_repo = repo or self.repo
        if target_repo:
            cmd.extend(["--repo", target_repo])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
            )

            return (
                result.returncode == 0,
                result.stdout.strip(),
                result.stderr.strip(),
            )

        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)

    # -------------------------------------------------------------------------
    # T023: Get existing issues for deduplication
    # -------------------------------------------------------------------------

    def get_existing_issues(self) -> Set[str]:
        """Fetch existing issue titles from GitHub for deduplication."""
        success, stdout, stderr = self._run_gh_command(
            ["issue", "list", "--json", "title", "--limit", "1000", "--state", "all"]
        )

        if not success:
            console.print(f"[yellow]Warning: Could not fetch existing issues: {stderr}[/yellow]")
            return set()

        try:
            issues = json.loads(stdout) if stdout else []
            return {issue.get("title", "").lower() for issue in issues}
        except json.JSONDecodeError:
            console.print("[yellow]Warning: Could not parse existing issues[/yellow]")
            return set()

    # -------------------------------------------------------------------------
    # T024: Check if issue is duplicate
    # -------------------------------------------------------------------------

    def is_duplicate(self, title: str) -> bool:
        """Check if an issue with this title already exists."""
        return title.lower() in self.existing_titles

    # -------------------------------------------------------------------------
    # T021: Format dry-run preview
    # -------------------------------------------------------------------------

    def _print_dry_run_preview(self, bug: ExtractedBug, labels: List[str]) -> None:
        """Print formatted preview for a single issue in dry-run mode."""
        title = self.format_issue_title(bug)
        labels_str = ", ".join(labels)

        console.print(f"\n[bold cyan]{title}[/bold cyan]")
        console.print(f"  [dim]Labels:[/dim] {labels_str}")
        console.print(f"  [dim]File:[/dim] {bug.source_file}")
        console.print(
            f"  [dim]Type:[/dim] {bug.bug_type.title()} | [dim]Severity:[/dim] {bug.severity.title()}"
        )
        if bug.line_number:
            console.print(f"  [dim]Line:[/dim] {bug.line_number}")

    # -------------------------------------------------------------------------
    # T038: Exponential backoff for rate limiting
    # -------------------------------------------------------------------------

    def _create_issue_with_retry(
        self,
        bug: ExtractedBug,
        labels: List[str],
        assignee: Optional[str] = None,
    ) -> IssueResult:
        """Create issue with exponential backoff for rate limiting."""
        import time

        for attempt in range(MAX_RETRIES):
            result = self.create_issue(bug, labels, assignee)

            if result.status == "created":
                return result

            # Check for rate limiting
            if result.error and ("rate limit" in result.error.lower() or "403" in result.error):
                delay = BASE_DELAY_SECONDS * (2**attempt)
                console.print(
                    f"[yellow]Rate limited. Waiting {delay:.1f}s before retry...[/yellow]"
                )
                time.sleep(delay)
                continue

            # Non-rate-limit error, don't retry
            return result

        return result

    # -------------------------------------------------------------------------
    # T008-T009: Parse single report and extract bugs
    # -------------------------------------------------------------------------

    def parse_single_report(self, report_path: str) -> List[ExtractedBug]:
        """Extract bugs from a single markdown analysis report."""
        bugs = []

        try:
            with open(report_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception as e:
            console.print(f"[yellow]Warning: Could not read {report_path}: {e}[/yellow]")
            return bugs

        # Extract source file from report header
        # Format: # Analyse: path/to/file.py
        source_file_match = re.search(r"^#\s*Analyse:\s*(.+)$", content, re.MULTILINE)
        source_file = source_file_match.group(1).strip() if source_file_match else "unknown"

        # Find the Risques section
        risques_pattern = r"##\s*Risques.*?(?=\n##|\Z)"
        risques_match = re.search(risques_pattern, content, re.DOTALL | re.IGNORECASE)

        if not risques_match:
            return bugs

        risques_section = risques_match.group(0)

        # Extract individual bugs from bullet points
        # Pattern: - **Type:** Description or - **Description:** ...
        bug_pattern = r"-\s*\*\*([^:*]+)\*\*\s*:?\s*(.+?)(?=\n-\s*\*\*|\n##|\Z)"
        bug_matches = re.findall(bug_pattern, risques_section, re.DOTALL)

        for bug_type_raw, description_raw in bug_matches:
            bug_type = self._classify_bug_type(bug_type_raw.strip())
            severity = self._extract_severity(description_raw)
            description = description_raw.strip()

            # Extract first line as title (max 100 chars)
            first_line = description.split("\n")[0].strip()
            title = first_line[:97] + "..." if len(first_line) > 100 else first_line

            # Try to extract line number
            line_match = re.search(r"ligne\s*(\d+)|line\s*(\d+)", description, re.IGNORECASE)
            line_number = None
            if line_match:
                line_number = int(line_match.group(1) or line_match.group(2))

            bugs.append(
                ExtractedBug(
                    source_file=source_file,
                    report_file=report_path,
                    bug_type=bug_type,
                    severity=severity,
                    title=title,
                    description=description,
                    recommendation="",
                    line_number=line_number,
                )
            )

        return bugs

    def _classify_bug_type(self, raw_type: str) -> str:
        """Classify bug type from raw text."""
        raw_lower = raw_type.lower()

        if any(kw in raw_lower for kw in ["sécurité", "security", "vulnérab", "injection", "xss"]):
            return "security"
        elif any(kw in raw_lower for kw in ["risque", "risk", "dette", "debt", "obsolète"]):
            return "risk"
        elif any(kw in raw_lower for kw in ["incohérence", "inconsist", "conflit"]):
            return "inconsistency"
        else:
            return "suggestion"

    def _extract_severity(self, description: str) -> str:
        """Extract severity from description text."""
        desc_lower = description.lower()

        if any(kw in desc_lower for kw in ["critique", "critical", "urgent"]):
            return "critical"
        elif any(kw in desc_lower for kw in ["élevé", "high", "important"]):
            return "high"
        elif any(kw in desc_lower for kw in ["moyen", "medium", "modéré"]):
            return "medium"
        else:
            return "low"

    # -------------------------------------------------------------------------
    # T010: Parse all reports from directory
    # -------------------------------------------------------------------------

    def parse_reports(self, from_report: Optional[str] = None) -> List[ExtractedBug]:
        """Scan docs/analyses/ directory and extract all bugs."""
        all_bugs = []

        if from_report:
            # Single file mode
            if os.path.exists(from_report):
                return self.parse_single_report(from_report)
            else:
                console.print(f"[red]Error: Report file not found: {from_report}[/red]")
                return []

        # Scan directory
        if not os.path.exists(self.output_dir):
            console.print(
                "[yellow]No analysis reports found. Run 'aetheris analysis' first.[/yellow]"
            )
            return []

        report_files = list(Path(self.output_dir).glob("*.md"))

        if not report_files:
            console.print(f"[yellow]No analysis reports found in {self.output_dir}[/yellow]")
            return []

        for report_file in report_files:
            bugs = self.parse_single_report(str(report_file))
            all_bugs.extend(bugs)

        return all_bugs

    # -------------------------------------------------------------------------
    # T011: Format issue body
    # -------------------------------------------------------------------------

    def format_issue_body(self, bug: ExtractedBug) -> str:
        """Format the issue body with markdown template."""
        body = f"""## File

`{bug.source_file}`

## Bug Description

{bug.description}

## Issue Details

- **Type**: {bug.bug_type.title()}
- **Severity**: {bug.severity.title()}
- **Line**: {bug.line_number or "N/A"}

## Recommended Solution

{bug.recommendation or "See description for context and recommended fixes."}

---
*Generated by [Aetheris](https://github.com/adryserage/aetheris) code analysis*
"""
        return body

    # -------------------------------------------------------------------------
    # T012: Format issue title
    # -------------------------------------------------------------------------

    def format_issue_title(self, bug: ExtractedBug) -> str:
        """Format issue title as [Type] in filename - description."""
        filename = os.path.basename(bug.source_file)
        bug_type_label = bug.bug_type.title()

        # Truncate title if needed (GitHub limit is 256, but we keep it readable)
        max_desc_len = 50
        title_desc = bug.title[:max_desc_len]
        if len(bug.title) > max_desc_len:
            title_desc += "..."

        return f"[{bug_type_label}] in {filename} - {title_desc}"

    # -------------------------------------------------------------------------
    # T013: Get labels for bug
    # -------------------------------------------------------------------------

    def get_labels_for_bug(
        self, bug: ExtractedBug, custom_labels: Optional[List[str]] = None
    ) -> List[str]:
        """Get labels based on bug type and severity."""
        labels = ["aetheris-analysis"]

        # Bug type labels
        if bug.bug_type == "security":
            labels.extend(["bug", "security"])
        elif bug.bug_type == "risk":
            labels.extend(["bug", "tech-debt"])
        elif bug.bug_type == "inconsistency":
            labels.append("bug")
        else:  # suggestion
            labels.append("enhancement")

        # Severity labels
        labels.append(f"priority-{bug.severity}")

        # Add custom labels
        if custom_labels:
            labels.extend(custom_labels)

        return list(set(labels))  # Remove duplicates

    # -------------------------------------------------------------------------
    # T014: Create single issue
    # -------------------------------------------------------------------------

    def create_issue(
        self,
        bug: ExtractedBug,
        labels: List[str],
        assignee: Optional[str] = None,
    ) -> IssueResult:
        """Create a single GitHub issue using gh CLI."""
        title = self.format_issue_title(bug)
        body = self.format_issue_body(bug)

        # Build command
        args = [
            "issue",
            "create",
            "--title",
            title,
            "--body",
            body,
        ]

        # Add labels
        if labels:
            args.extend(["--label", ",".join(labels)])

        # Add assignee
        if assignee:
            args.extend(["--assignee", assignee])

        success, stdout, stderr = self._run_gh_command(args)

        if success:
            # Extract URL from output
            url = stdout.strip() if stdout else None
            return IssueResult(
                status="created",
                title=title,
                url=url,
                bug=bug,
            )
        else:
            return IssueResult(
                status="failed",
                title=title,
                error=stderr or "Unknown error",
                bug=bug,
            )

    # -------------------------------------------------------------------------
    # T015: Main run orchestration
    # -------------------------------------------------------------------------

    async def run(self, options: IssueOptions) -> IssuesSummary:
        """Main orchestration method for issue creation."""
        import time

        start_time = time.time()

        summary = IssuesSummary(
            total_bugs=0,
            created=0,
            skipped=0,
            failed=0,
        )

        # Validate gh CLI (unless dry-run)
        if not options.dry_run:
            valid, message = await self.validate_gh_cli()
            if not valid:
                console.print(f"[red]Error: {message}[/red]")
                return summary

        # Parse reports
        console.print("[blue]Scanning analysis reports...[/blue]")
        bugs = self.parse_reports(options.from_report)
        summary.total_bugs = len(bugs)

        if not bugs:
            console.print("[yellow]No bugs found in analysis reports.[/yellow]")
            return summary

        console.print(f"[green]Found {len(bugs)} bugs in analysis reports[/green]")

        # T023-T025: Fetch existing issues for deduplication (unless dry-run)
        if not options.dry_run:
            console.print("[blue]Fetching existing issues for deduplication...[/blue]")
            self.existing_titles = self.get_existing_issues()
            console.print(f"[dim]Found {len(self.existing_titles)} existing issues[/dim]")

        # T021: Dry-run header
        if options.dry_run:
            console.print()
            console.print("[yellow]🔍 DRY-RUN MODE - No issues will be created[/yellow]")
            console.print("[dim]The following issues would be created:[/dim]")

        # Process each bug with progress bar (T017)
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            disable=options.dry_run,  # Disable spinner in dry-run for cleaner preview
        ) as progress:
            task_desc = "Previewing issues..." if options.dry_run else "Creating issues..."
            task = progress.add_task(task_desc, total=len(bugs))

            for bug in bugs:
                labels = self.get_labels_for_bug(bug, options.labels)
                title = self.format_issue_title(bug)

                if options.dry_run:
                    # T021: Formatted preview output
                    self._print_dry_run_preview(bug, labels)
                    result = IssueResult(
                        status="created",  # Would be created
                        title=title,
                        bug=bug,
                    )
                    summary.created += 1
                else:
                    # T024-T026: Check for duplicates
                    if self.is_duplicate(title):
                        result = IssueResult(
                            status="skipped",
                            title=title,
                            error="Already exists",
                            bug=bug,
                        )
                        summary.skipped += 1
                        console.print(f"  [yellow]○[/yellow] {title} [dim](already exists)[/dim]")
                    else:
                        # T038: Create with retry for rate limiting
                        result = self._create_issue_with_retry(bug, labels, options.assignee)

                        if result.status == "created":
                            summary.created += 1
                            # Add to existing titles to prevent duplicates in same run
                            self.existing_titles.add(title.lower())
                            console.print(f"  [green]✓[/green] {title}")
                            if result.url:
                                console.print(f"    [dim]{result.url}[/dim]")
                        else:
                            summary.failed += 1
                            console.print(f"  [red]✗[/red] {title}: {result.error}")

                summary.results.append(result)
                progress.advance(task)

        summary.duration_seconds = time.time() - start_time

        # Print summary (T018, T022)
        self._print_summary(summary, options.dry_run)

        return summary

    # -------------------------------------------------------------------------
    # T018: Print summary report
    # -------------------------------------------------------------------------

    def _print_summary(self, summary: IssuesSummary, dry_run: bool = False):
        """Print final summary report."""
        console.print()
        console.rule("[bold]Summary")
        console.print()

        if dry_run:
            # T022: Dry-run summary with "would be created" wording
            console.print("[yellow]🔍 DRY-RUN MODE - No issues were actually created[/yellow]")
            console.print()
            console.print(f"Total bugs found:      [bold]{summary.total_bugs}[/bold]")
            console.print(f"Issues would create:   [green]{summary.created}[/green]")
            console.print()
            console.print("[dim]Run without --dry-run to create these issues.[/dim]")
        else:
            console.print(f"Total bugs found: [bold]{summary.total_bugs}[/bold]")
            console.print(f"Issues created:   [green]{summary.created}[/green]")
            console.print(
                f"Issues skipped:   [yellow]{summary.skipped}[/yellow] [dim](already exist)[/dim]"
            )
            console.print(f"Issues failed:    [red]{summary.failed}[/red]")

        console.print()
        console.print(f"Duration: {summary.duration_seconds:.1f}s")
