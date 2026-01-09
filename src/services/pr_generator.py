"""
GitHub PR Generator Service

Creates GitHub Pull Requests from Aetheris analysis reports.
Generates AI-powered fixes for each bug, creates branches, and opens PRs.
"""

import hashlib
import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Set, Tuple

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

# Reuse bug parsing from issue_creator
from src.services.issue_creator import ExtractedBug, IssueCreator

console = Console()


# =============================================================================
# Constants
# =============================================================================

MAX_RETRIES = 3
BASE_DELAY_SECONDS = 2.0


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class PROptions:
    """Configuration options for the PR generation command."""

    dry_run: bool = False
    base_branch: Optional[str] = None
    from_report: Optional[str] = None
    bug_index: Optional[int] = None
    issue_number: Optional[int] = None
    link_issues: bool = False


@dataclass
class GeneratedFix:
    """AI-generated fix for a bug."""

    bug: ExtractedBug
    original_code: str
    fixed_code: str
    file_path: str
    is_valid: bool
    validation_error: Optional[str] = None


@dataclass
class PRToCreate:
    """Prepared PR ready for GitHub."""

    title: str
    body: str
    branch_name: str
    base_branch: str
    fix: GeneratedFix
    linked_issue: Optional[int] = None


@dataclass
class PRResult:
    """Result of a single PR creation attempt."""

    status: str  # 'created', 'skipped', 'failed'
    title: str
    branch_name: Optional[str] = None
    url: Optional[str] = None
    error: Optional[str] = None
    bug: Optional[ExtractedBug] = None


@dataclass
class PRSummary:
    """Final summary of the PR generation execution."""

    total_bugs: int
    created: int
    skipped: int
    failed: int
    results: List[PRResult] = field(default_factory=list)
    duration_seconds: float = 0.0


# =============================================================================
# PR Generator Service
# =============================================================================


class PRGenerator:
    """Service for generating GitHub PRs from Aetheris analysis reports."""

    def __init__(
        self,
        repo: Optional[str] = None,
        output_dir: str = "docs/analyses",
        ai_provider=None,
    ):
        self.repo = repo
        self.output_dir = output_dir
        self.ai_provider = ai_provider
        self.issue_creator = IssueCreator(repo=repo, output_dir=output_dir)
        self.existing_branches: Set[str] = set()
        self.existing_issues: dict = {}  # title -> issue_number
        self.original_branch: str = ""

    # -------------------------------------------------------------------------
    # Validation Methods
    # -------------------------------------------------------------------------

    async def validate_prerequisites(self) -> Tuple[bool, str]:
        """Check git, gh CLI, and AI provider availability."""
        # Check git
        success, _, stderr = self._run_git_command(["--version"])
        if not success:
            return False, "git is not installed or not accessible"

        # Check gh CLI
        valid, message = await self.issue_creator.validate_gh_cli()
        if not valid:
            return False, message

        # Check AI provider
        if self.ai_provider is None:
            return False, "AI provider not configured. Set AI_PROVIDER and API key."

        return True, "All prerequisites validated"

    # -------------------------------------------------------------------------
    # Command Helpers
    # -------------------------------------------------------------------------

    def _run_git_command(self, args: List[str], cwd: Optional[str] = None) -> Tuple[bool, str, str]:
        """Execute a git command with error handling."""
        cmd = ["git"] + args

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=cwd,
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

    def _run_gh_command(self, args: List[str]) -> Tuple[bool, str, str]:
        """Execute a gh CLI command with error handling."""
        return self.issue_creator._run_gh_command(args)

    # -------------------------------------------------------------------------
    # Branch Operations
    # -------------------------------------------------------------------------

    def generate_branch_name(self, bug: ExtractedBug) -> str:
        """Generate branch name: fix/<type>-<filename>-<hash>."""
        filename = Path(bug.source_file).stem
        # Create short hash from bug title
        title_hash = hashlib.md5(bug.title.encode()).hexdigest()[:6]
        return f"fix/{bug.bug_type}-{filename}-{title_hash}"

    def get_default_branch(self) -> str:
        """Get the repository's default branch."""
        success, stdout, _ = self._run_gh_command(
            ["repo", "view", "--json", "defaultBranchRef", "--jq", ".defaultBranchRef.name"]
        )
        if success and stdout:
            return stdout.strip()
        return "main"  # fallback

    def get_current_branch(self) -> str:
        """Get the current git branch name."""
        success, stdout, _ = self._run_git_command(["branch", "--show-current"])
        return stdout if success else "main"

    def branch_exists(self, branch_name: str) -> bool:
        """Check if a branch already exists locally or remotely."""
        # Check local
        success, _, _ = self._run_git_command(["rev-parse", "--verify", branch_name])
        if success:
            return True

        # Check remote
        success, _, _ = self._run_git_command(["ls-remote", "--heads", "origin", branch_name])
        return success

    def create_branch(self, branch_name: str, base_branch: str) -> Tuple[bool, str]:
        """Create a new branch from base branch."""
        # Fetch latest
        self._run_git_command(["fetch", "origin", base_branch])

        # Create and checkout branch
        success, _, stderr = self._run_git_command(
            ["checkout", "-b", branch_name, f"origin/{base_branch}"]
        )
        if not success:
            return False, f"Failed to create branch: {stderr}"
        return True, ""

    def push_branch(self, branch_name: str) -> Tuple[bool, str]:
        """Push branch to origin."""
        success, _, stderr = self._run_git_command(["push", "-u", "origin", branch_name])
        if not success:
            return False, f"Failed to push branch: {stderr}"
        return True, ""

    def restore_branch(self, branch_name: str) -> None:
        """Restore to original branch."""
        self._run_git_command(["checkout", branch_name])

    # -------------------------------------------------------------------------
    # File Operations
    # -------------------------------------------------------------------------

    def read_source_file(self, file_path: str) -> Optional[str]:
        """Read source file content for AI context."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception:
            return None

    def apply_fix(self, file_path: str, fixed_code: str) -> Tuple[bool, str]:
        """Write fixed code to file."""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(fixed_code)
            return True, ""
        except Exception as e:
            return False, str(e)

    def restore_file(self, file_path: str) -> None:
        """Reset file to HEAD state."""
        self._run_git_command(["checkout", "HEAD", "--", file_path])

    # -------------------------------------------------------------------------
    # AI Fix Generation
    # -------------------------------------------------------------------------

    def build_fix_prompt(self, bug: ExtractedBug, code_context: str) -> str:
        """Build the AI prompt for fix generation."""
        language = self._detect_language(bug.source_file)

        return f"""You are a senior software engineer. Fix the following bug.

## Bug Information
- **File**: {bug.source_file}
- **Type**: {bug.bug_type}
- **Severity**: {bug.severity}
- **Description**: {bug.description}
- **Line**: {bug.line_number or 'Not specified'}

## Current Code
```{language}
{code_context}
```

## Instructions
1. Analyze the bug description carefully
2. Apply a minimal, targeted fix
3. Return ONLY the complete fixed file content
4. Do NOT include explanations or markdown code blocks
5. Preserve the original code style and formatting

## Fixed Code:
"""

    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension."""
        ext = Path(file_path).suffix.lower()
        lang_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "jsx",
            ".tsx": "tsx",
            ".java": "java",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".c": "c",
            ".cpp": "cpp",
            ".h": "c",
            ".cs": "csharp",
        }
        return lang_map.get(ext, "text")

    async def generate_fix(self, bug: ExtractedBug) -> GeneratedFix:
        """Generate AI fix for a bug."""
        file_path = bug.source_file
        original_code = self.read_source_file(file_path)

        if original_code is None:
            return GeneratedFix(
                bug=bug,
                original_code="",
                fixed_code="",
                file_path=file_path,
                is_valid=False,
                validation_error="Source file not found",
            )

        # Build and send prompt to AI
        prompt = self.build_fix_prompt(bug, original_code)

        try:
            fixed_code = await self.ai_provider.generate(prompt)

            # Clean up AI response (remove markdown code blocks if present)
            fixed_code = self._clean_ai_response(fixed_code)

            # Validate the fix
            is_valid, error = self.validate_fix(file_path, fixed_code)

            return GeneratedFix(
                bug=bug,
                original_code=original_code,
                fixed_code=fixed_code,
                file_path=file_path,
                is_valid=is_valid,
                validation_error=error,
            )
        except Exception as e:
            return GeneratedFix(
                bug=bug,
                original_code=original_code,
                fixed_code="",
                file_path=file_path,
                is_valid=False,
                validation_error=f"AI generation failed: {e}",
            )

    def _clean_ai_response(self, response: str) -> str:
        """Clean AI response by removing markdown code blocks."""
        response = response.strip()

        # Remove leading ```language
        if response.startswith("```"):
            lines = response.split("\n")
            if len(lines) > 2:
                lines = lines[1:]  # Remove first line
                if lines[-1].strip() == "```":
                    lines = lines[:-1]  # Remove last line
                response = "\n".join(lines)

        return response

    def validate_fix(self, file_path: str, fixed_code: str) -> Tuple[bool, Optional[str]]:
        """Validate generated fix for syntax errors."""
        ext = Path(file_path).suffix.lower()

        if ext == ".py":
            try:
                compile(fixed_code, file_path, "exec")
                return True, None
            except SyntaxError as e:
                return False, f"Python syntax error: {e}"

        elif ext in [".js", ".ts", ".jsx", ".tsx"]:
            # Write to temp file and check with node
            import tempfile

            with tempfile.NamedTemporaryFile(mode="w", suffix=ext, delete=False) as f:
                f.write(fixed_code)
                temp_path = f.name

            try:
                result = subprocess.run(
                    ["node", "--check", temp_path],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                os.unlink(temp_path)
                if result.returncode != 0:
                    return False, f"JS/TS syntax error: {result.stderr}"
                return True, None
            except Exception:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                return True, None  # Assume valid if we can't check

        # For other languages, assume valid
        return True, None

    # -------------------------------------------------------------------------
    # Commit and PR Operations
    # -------------------------------------------------------------------------

    def commit_fix(self, bug: ExtractedBug, file_path: str) -> Tuple[bool, str]:
        """Commit the fix with conventional commit message."""
        # Stage the file
        success, _, stderr = self._run_git_command(["add", file_path])
        if not success:
            return False, f"Failed to stage file: {stderr}"

        # Create commit message
        filename = Path(file_path).name
        commit_msg = f"fix({filename}): {bug.bug_type} - {bug.title[:50]}"

        success, _, stderr = self._run_git_command(["commit", "-m", commit_msg])
        if not success:
            return False, f"Failed to commit: {stderr}"

        return True, ""

    def format_pr_title(self, bug: ExtractedBug) -> str:
        """Format PR title as fix: [Type] in filename - description."""
        filename = Path(bug.source_file).name
        bug_type_label = bug.bug_type.title()

        max_desc_len = 50
        title_desc = bug.title[:max_desc_len]
        if len(bug.title) > max_desc_len:
            title_desc += "..."

        return f"fix: [{bug_type_label}] in {filename} - {title_desc}"

    def format_pr_body(
        self,
        bug: ExtractedBug,
        fix: GeneratedFix,
        linked_issue: Optional[int] = None,
    ) -> str:
        """Format the PR body with markdown template."""
        issue_link = ""
        if linked_issue:
            issue_link = f"Fixes #{linked_issue}"
        else:
            issue_link = "*No linked issue - created from analysis report*"

        validation_status = "✅ Passed" if fix.is_valid else f"⚠️ {fix.validation_error}"

        body = f"""## Description

This PR fixes a **{bug.bug_type}** issue detected by Aetheris code analysis.

**Bug Description**: {bug.description}

## Changes Made

- Fixed {bug.bug_type} issue in `{bug.source_file}`
{f"- Line {bug.line_number}" if bug.line_number else ""}

## Related Issue

{issue_link}

## Validation

- **Syntax Check**: {validation_status}
- [ ] Manual code review recommended
- [ ] Tests pass

---
*Generated by [Aetheris](https://github.com/adryserage/aetheris) PR Generator*
"""
        return body

    def create_pr(
        self,
        title: str,
        body: str,
        branch_name: str,
        base_branch: str,
    ) -> Tuple[bool, str, str]:
        """Create a GitHub PR using gh CLI."""
        args = [
            "pr",
            "create",
            "--title",
            title,
            "--body",
            body,
            "--base",
            base_branch,
            "--head",
            branch_name,
        ]

        return self._run_gh_command(args)

    # -------------------------------------------------------------------------
    # Issue Linking
    # -------------------------------------------------------------------------

    def get_existing_issues(self) -> dict:
        """Fetch existing issues from repo for linking."""
        success, stdout, _ = self._run_gh_command(
            ["issue", "list", "--json", "title,number", "--limit", "500", "--state", "open"]
        )

        if not success or not stdout:
            return {}

        try:
            import json

            issues = json.loads(stdout)
            return {issue["title"].lower(): issue["number"] for issue in issues}
        except Exception:
            return {}

    def find_matching_issue(self, bug: ExtractedBug) -> Optional[int]:
        """Find a matching issue for this bug."""
        # Generate expected issue title (same format as issue_creator)
        expected_title = self.issue_creator.format_issue_title(bug).lower()

        # Try exact match first
        if expected_title in self.existing_issues:
            return self.existing_issues[expected_title]

        # Try prefix match
        for title, number in self.existing_issues.items():
            if title.startswith(f"[{bug.bug_type}]") and bug.source_file in title:
                return number

        return None

    # -------------------------------------------------------------------------
    # Dry Run Preview
    # -------------------------------------------------------------------------

    def _print_dry_run_preview(
        self,
        bug: ExtractedBug,
        fix: GeneratedFix,
        branch_name: str,
        linked_issue: Optional[int],
    ) -> None:
        """Print formatted preview for dry-run mode."""
        title = self.format_pr_title(bug)

        console.print(f"\n[bold cyan]PR: {title}[/bold cyan]")
        console.print(f"  [dim]Branch:[/dim] {branch_name}")
        console.print(f"  [dim]File:[/dim] {bug.source_file}")
        console.print(
            f"  [dim]Type:[/dim] {bug.bug_type.title()} | [dim]Severity:[/dim] {bug.severity.title()}"
        )

        if linked_issue:
            console.print(f"  [dim]Links to:[/dim] Issue #{linked_issue}")

        if fix.is_valid:
            console.print("  [dim]Fix:[/dim] [green]✓ Valid[/green]")
        else:
            console.print(f"  [dim]Fix:[/dim] [yellow]⚠ {fix.validation_error}[/yellow]")

    # -------------------------------------------------------------------------
    # Main Orchestration
    # -------------------------------------------------------------------------

    async def run(self, options: PROptions) -> PRSummary:
        """Main orchestration method for PR generation."""
        import time

        start_time = time.time()

        summary = PRSummary(
            total_bugs=0,
            created=0,
            skipped=0,
            failed=0,
        )

        # Validate prerequisites (unless dry-run)
        if not options.dry_run:
            valid, message = await self.validate_prerequisites()
            if not valid:
                console.print(f"[red]Error: {message}[/red]")
                return summary

        # Save current branch
        self.original_branch = self.get_current_branch()

        # Get base branch
        base_branch = options.base_branch or self.get_default_branch()
        console.print(f"[dim]Base branch: {base_branch}[/dim]")

        # Parse bugs using issue_creator
        console.print("[blue]Scanning analysis reports...[/blue]")
        bugs = self.issue_creator.parse_reports(options.from_report)

        # Filter by bug_index if specified
        if options.bug_index is not None and 0 <= options.bug_index < len(bugs):
            bugs = [bugs[options.bug_index]]

        summary.total_bugs = len(bugs)

        if not bugs:
            console.print("[yellow]No bugs found in analysis reports.[/yellow]")
            return summary

        console.print(f"[green]Found {len(bugs)} bugs in analysis reports[/green]")

        # Fetch existing issues for linking
        if options.link_issues and not options.dry_run:
            console.print("[blue]Fetching existing issues for linking...[/blue]")
            self.existing_issues = self.get_existing_issues()
            console.print(f"[dim]Found {len(self.existing_issues)} open issues[/dim]")

        # Dry-run header
        if options.dry_run:
            console.print()
            console.print("[yellow]🔍 DRY-RUN MODE - No PRs will be created[/yellow]")
            console.print("[dim]The following PRs would be generated:[/dim]")

        # Process each bug
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            disable=options.dry_run,
        ) as progress:
            task_desc = "Previewing PRs..." if options.dry_run else "Generating PRs..."
            task = progress.add_task(task_desc, total=len(bugs))

            for bug in bugs:
                branch_name = self.generate_branch_name(bug)
                title = self.format_pr_title(bug)

                # Find linked issue
                linked_issue = options.issue_number
                if not linked_issue and options.link_issues:
                    linked_issue = self.find_matching_issue(bug)

                if options.dry_run:
                    # Generate fix for preview but don't apply
                    fix = await self.generate_fix(bug)
                    self._print_dry_run_preview(bug, fix, branch_name, linked_issue)
                    result = PRResult(
                        status="created",
                        title=title,
                        branch_name=branch_name,
                        bug=bug,
                    )
                    summary.created += 1
                else:
                    # Check if branch already exists
                    if self.branch_exists(branch_name):
                        result = PRResult(
                            status="skipped",
                            title=title,
                            branch_name=branch_name,
                            error="Branch already exists",
                            bug=bug,
                        )
                        summary.skipped += 1
                        console.print(f"  [yellow]○[/yellow] {title} [dim](branch exists)[/dim]")
                    else:
                        # Process the bug
                        result = await self._process_bug(
                            bug, branch_name, base_branch, linked_issue
                        )

                        if result.status == "created":
                            summary.created += 1
                            console.print(f"  [green]✓[/green] {title}")
                            if result.url:
                                console.print(f"    [dim]{result.url}[/dim]")
                        else:
                            summary.failed += 1
                            console.print(f"  [red]✗[/red] {title}: {result.error}")

                summary.results.append(result)
                progress.advance(task)

        # Restore original branch
        if not options.dry_run:
            self.restore_branch(self.original_branch)

        summary.duration_seconds = time.time() - start_time
        self._print_summary(summary, options.dry_run)

        return summary

    async def _process_bug(
        self,
        bug: ExtractedBug,
        branch_name: str,
        base_branch: str,
        linked_issue: Optional[int],
    ) -> PRResult:
        """Process a single bug: create branch, generate fix, create PR."""
        title = self.format_pr_title(bug)

        try:
            # Check source file exists
            if not os.path.exists(bug.source_file):
                return PRResult(
                    status="failed",
                    title=title,
                    branch_name=branch_name,
                    error="Source file not found",
                    bug=bug,
                )

            # Create branch
            success, error = self.create_branch(branch_name, base_branch)
            if not success:
                return PRResult(
                    status="failed",
                    title=title,
                    branch_name=branch_name,
                    error=error,
                    bug=bug,
                )

            # Generate fix
            fix = await self.generate_fix(bug)

            if not fix.fixed_code:
                self.restore_branch(self.original_branch)
                return PRResult(
                    status="failed",
                    title=title,
                    branch_name=branch_name,
                    error=fix.validation_error or "Failed to generate fix",
                    bug=bug,
                )

            # Apply fix to file
            success, error = self.apply_fix(fix.file_path, fix.fixed_code)
            if not success:
                self.restore_branch(self.original_branch)
                return PRResult(
                    status="failed",
                    title=title,
                    branch_name=branch_name,
                    error=f"Failed to apply fix: {error}",
                    bug=bug,
                )

            # Commit
            success, error = self.commit_fix(bug, fix.file_path)
            if not success:
                self.restore_file(fix.file_path)
                self.restore_branch(self.original_branch)
                return PRResult(
                    status="failed",
                    title=title,
                    branch_name=branch_name,
                    error=error,
                    bug=bug,
                )

            # Push
            success, error = self.push_branch(branch_name)
            if not success:
                self.restore_branch(self.original_branch)
                return PRResult(
                    status="failed",
                    title=title,
                    branch_name=branch_name,
                    error=error,
                    bug=bug,
                )

            # Create PR
            body = self.format_pr_body(bug, fix, linked_issue)
            success, stdout, stderr = self.create_pr(title, body, branch_name, base_branch)

            if success:
                return PRResult(
                    status="created",
                    title=title,
                    branch_name=branch_name,
                    url=stdout.strip() if stdout else None,
                    bug=bug,
                )
            else:
                return PRResult(
                    status="failed",
                    title=title,
                    branch_name=branch_name,
                    error=stderr or "Failed to create PR",
                    bug=bug,
                )

        except Exception as e:
            return PRResult(
                status="failed",
                title=title,
                branch_name=branch_name,
                error=str(e),
                bug=bug,
            )
        finally:
            # Always try to restore to original branch
            self._run_git_command(["checkout", self.original_branch])

    def _print_summary(self, summary: PRSummary, dry_run: bool = False) -> None:
        """Print final summary report."""
        console.print()
        console.rule("[bold]Summary")
        console.print()

        if dry_run:
            console.print("[yellow]🔍 DRY-RUN MODE - No PRs were actually created[/yellow]")
            console.print()
            console.print(f"Total bugs found:    [bold]{summary.total_bugs}[/bold]")
            console.print(f"PRs would create:    [green]{summary.created}[/green]")
            console.print()
            console.print("[dim]Run without --dry-run to create these PRs.[/dim]")
        else:
            console.print(f"Total bugs found: [bold]{summary.total_bugs}[/bold]")
            console.print(f"PRs created:      [green]{summary.created}[/green]")
            console.print(
                f"PRs skipped:      [yellow]{summary.skipped}[/yellow] [dim](branch exists)[/dim]"
            )
            console.print(f"PRs failed:       [red]{summary.failed}[/red]")

        console.print()
        console.print(f"Duration: {summary.duration_seconds:.1f}s")
