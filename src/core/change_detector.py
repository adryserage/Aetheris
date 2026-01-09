"""
Change Detector for incremental analysis (v2.6.1)

Detects files modified since the last analysis run to enable
efficient reanalysis of only changed files.
"""

import json
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from src.core.logger import log_print


@dataclass
class LastAnalysisInfo:
    """Information about the last analysis run"""

    timestamp: datetime
    files_analyzed: List[str]
    git_commit_sha: Optional[str]
    metrics_file: str


class ChangeDetector:
    """Detects files changed since the last analysis.

    Uses git diff when available, falls back to file modification timestamps.

    Usage:
        detector = ChangeDetector(metrics_dir="docs/metrics")
        last_analysis = detector.get_last_analysis_info()
        if last_analysis:
            changed_files = detector.get_changed_files(last_analysis)
    """

    def __init__(self, metrics_dir: str = "docs/metrics", root_dir: str = "."):
        """Initialize the change detector.

        Args:
            metrics_dir: Directory containing metrics JSON files
            root_dir: Root directory of the project
        """
        self.metrics_dir = metrics_dir
        self.root_dir = root_dir

    def get_last_analysis_info(self) -> Optional[LastAnalysisInfo]:
        """Get information about the last analysis run.

        Returns:
            LastAnalysisInfo if a previous analysis exists, None otherwise
        """
        metrics_path = Path(self.metrics_dir)
        if not metrics_path.exists():
            return None

        # Find the most recent metrics file
        metrics_files = sorted(metrics_path.glob("metrics_*.json"), reverse=True)
        if not metrics_files:
            return None

        latest_file = metrics_files[0]

        try:
            with open(latest_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Parse the timestamp
            end_time_str = data.get("end_time") or data.get("start_time")
            if not end_time_str:
                return None

            timestamp = datetime.fromisoformat(end_time_str)

            # Get analyzed files from metadata if available
            files_analyzed = data.get("metadata", {}).get("analyzed_files", [])

            # Get git commit SHA if stored
            git_sha = data.get("metadata", {}).get("git_commit_sha")

            return LastAnalysisInfo(
                timestamp=timestamp,
                files_analyzed=files_analyzed,
                git_commit_sha=git_sha,
                metrics_file=str(latest_file),
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            log_print(f"⚠️  Error reading metrics file {latest_file}: {e}")
            return None

    def get_changed_files(
        self,
        since: Optional[LastAnalysisInfo] = None,
        file_extensions: Optional[List[str]] = None,
    ) -> Tuple[List[str], str]:
        """Get list of files changed since the last analysis.

        Args:
            since: LastAnalysisInfo from get_last_analysis_info()
            file_extensions: Optional list of extensions to filter (e.g., ['.py', '.js'])

        Returns:
            Tuple of (list of changed file paths, detection method used)
        """
        if since is None:
            since = self.get_last_analysis_info()

        if since is None:
            return [], "no_previous_analysis"

        # Try git first (more accurate)
        changed_files, method = self._get_changed_via_git(since)

        # Fall back to timestamp if git fails
        if method == "git_unavailable":
            changed_files, method = self._get_changed_via_timestamps(since.timestamp)

        # Filter by extension if specified
        if file_extensions and changed_files:
            changed_files = [
                f for f in changed_files if any(f.endswith(ext) for ext in file_extensions)
            ]

        return changed_files, method

    def _get_changed_via_git(self, since: LastAnalysisInfo) -> Tuple[List[str], str]:
        """Detect changed files using git.

        Args:
            since: Information about the last analysis

        Returns:
            Tuple of (changed files list, detection method)
        """
        try:
            # Check if git is available
            subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                capture_output=True,
                check=True,
                cwd=self.root_dir,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            return [], "git_unavailable"

        changed_files = set()

        # If we have a commit SHA, use git diff
        if since.git_commit_sha:
            try:
                result = subprocess.run(
                    ["git", "diff", "--name-only", since.git_commit_sha, "HEAD"],
                    capture_output=True,
                    text=True,
                    cwd=self.root_dir,
                )
                if result.returncode == 0:
                    changed_files.update(result.stdout.strip().split("\n"))
            except subprocess.CalledProcessError:
                pass

        # Also check for uncommitted changes
        try:
            # Staged changes
            result = subprocess.run(
                ["git", "diff", "--name-only", "--cached"],
                capture_output=True,
                text=True,
                cwd=self.root_dir,
            )
            if result.returncode == 0:
                changed_files.update(result.stdout.strip().split("\n"))

            # Unstaged changes
            result = subprocess.run(
                ["git", "diff", "--name-only"],
                capture_output=True,
                text=True,
                cwd=self.root_dir,
            )
            if result.returncode == 0:
                changed_files.update(result.stdout.strip().split("\n"))

            # Untracked files
            result = subprocess.run(
                ["git", "ls-files", "--others", "--exclude-standard"],
                capture_output=True,
                text=True,
                cwd=self.root_dir,
            )
            if result.returncode == 0:
                changed_files.update(result.stdout.strip().split("\n"))
        except subprocess.CalledProcessError:
            pass

        # Filter out empty strings and non-existent files
        filtered_files = [
            f for f in changed_files if f and os.path.exists(os.path.join(self.root_dir, f))
        ]

        return filtered_files, "git"

    def _get_changed_via_timestamps(self, since_timestamp: datetime) -> Tuple[List[str], str]:
        """Detect changed files using file modification timestamps.

        Args:
            since_timestamp: Timestamp to compare against

        Returns:
            Tuple of (changed files list, detection method)
        """
        changed_files = []
        since_ts = since_timestamp.timestamp()

        for root, _, files in os.walk(self.root_dir):
            # Skip hidden directories and common non-code directories
            if any(
                skip in root
                for skip in [".git", "__pycache__", "node_modules", ".venv", "venv", ".tox"]
            ):
                continue

            for file in files:
                filepath = os.path.join(root, file)
                try:
                    mtime = os.path.getmtime(filepath)
                    if mtime > since_ts:
                        rel_path = os.path.relpath(filepath, self.root_dir)
                        changed_files.append(rel_path)
                except OSError:
                    continue

        return changed_files, "timestamps"

    def get_current_git_sha(self) -> Optional[str]:
        """Get the current git commit SHA.

        Returns:
            Current commit SHA or None if git is unavailable
        """
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.root_dir,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        return None

    def get_deleted_files(self, since: LastAnalysisInfo) -> List[str]:
        """Get list of files that were analyzed before but no longer exist.

        Args:
            since: Information about the last analysis

        Returns:
            List of deleted file paths
        """
        if not since.files_analyzed:
            return []

        deleted = []
        for filepath in since.files_analyzed:
            full_path = os.path.join(self.root_dir, filepath)
            if not os.path.exists(full_path):
                deleted.append(filepath)

        return deleted
