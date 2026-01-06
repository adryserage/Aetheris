"""
GitHub Service - Intégration avec GitHub via gh CLI

Gère toutes les opérations GitHub pour l'analyse de Pull Requests:
- Récupération d'informations sur les PRs
- Récupération des diffs
- Publication de commentaires
- Détection de propriété des PRs
"""

import asyncio
import json
import re
import shutil
import subprocess
from typing import List
from typing import Optional
from typing import Tuple

from rich.console import Console

from src.models.pr_models import PRFile
from src.models.pr_models import PRFileStatus
from src.models.pr_models import PRInfo


class GitHubServiceError(Exception):
    """Erreur du service GitHub"""


class GitHubService:
    """Service pour les opérations GitHub via gh CLI"""

    def __init__(self, repo: Optional[str] = None):
        """
        Initialise le service GitHub.

        Args:
            repo: Repository au format owner/repo (optionnel)
        """
        self.repo = repo
        self.console = Console()
        self._gh_path: Optional[str] = None
        self._is_available: Optional[bool] = None

    @property
    def is_available(self) -> bool:
        """Vérifie si gh CLI est disponible."""
        if self._is_available is None:
            self._is_available = self._validate_gh_cli()
        return self._is_available

    def _validate_gh_cli(self) -> bool:
        """
        Vérifie si gh CLI est installé et authentifié.

        Returns:
            True si gh est disponible et authentifié
        """
        gh_path = shutil.which("gh")
        if not gh_path:
            return False

        self._gh_path = gh_path

        # Vérifier l'authentification
        try:
            result = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def parse_pr_url(self, url: str) -> Tuple[str, int]:
        """
        Parse une URL de PR GitHub pour extraire repo et numéro.

        Args:
            url: URL de la PR (ex: https://github.com/owner/repo/pull/123)

        Returns:
            Tuple (repo, pr_number)

        Raises:
            GitHubServiceError: Si l'URL est invalide
        """
        patterns = [
            r"github\.com/([^/]+/[^/]+)/pull/(\d+)",
            r"github\.com/([^/]+/[^/]+)/pulls/(\d+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                repo = match.group(1)
                pr_number = int(match.group(2))
                return repo, pr_number

        raise GitHubServiceError(f"URL de PR invalide: {url}")

    async def fetch_pr_info(self, repo: str, pr_number: int) -> PRInfo:
        """
        Récupère les informations d'une PR.

        Args:
            repo: Repository au format owner/repo
            pr_number: Numéro de la PR

        Returns:
            PRInfo avec les métadonnées de la PR
        """
        if not self.is_available:
            raise GitHubServiceError("gh CLI n'est pas disponible ou non authentifié")

        cmd = [
            "gh",
            "pr",
            "view",
            str(pr_number),
            "--repo",
            repo,
            "--json",
            "title,body,author,state,additions,deletions,files,headRefName,baseRefName,url,headRefOid",
        ]

        result = await asyncio.to_thread(
            subprocess.run,
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            raise GitHubServiceError(f"Erreur lors de la récupération de la PR: {result.stderr}")

        data = json.loads(result.stdout)

        # Récupérer l'email de l'auteur via l'API
        author_email = await self._get_author_email(repo, data.get("author", {}).get("login", ""))

        return PRInfo(
            repo=repo,
            pr_number=pr_number,
            title=data.get("title", ""),
            description=data.get("body", "") or "",
            author_login=data.get("author", {}).get("login", ""),
            author_email=author_email,
            base_branch=data.get("baseRefName", "main"),
            head_branch=data.get("headRefName", ""),
            url=data.get("url", ""),
            state=data.get("state", "").lower(),
            files_count=len(data.get("files", [])),
            additions=data.get("additions", 0),
            deletions=data.get("deletions", 0),
            head_sha=data.get("headRefOid"),
        )

    async def _get_author_email(self, repo: str, login: str) -> Optional[str]:
        """
        Récupère l'email d'un utilisateur GitHub via l'API.

        Args:
            repo: Repository (non utilisé directement, mais utile pour le contexte)
            login: Login GitHub de l'utilisateur

        Returns:
            Email de l'utilisateur ou None
        """
        if not login:
            return None

        try:
            # Essayer de récupérer via les commits de l'utilisateur
            cmd = [
                "gh",
                "api",
                f"users/{login}",
                "--jq",
                ".email",
            ]

            result = await asyncio.to_thread(
                subprocess.run,
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0 and result.stdout.strip():
                email = result.stdout.strip()
                if email and email != "null":
                    return email

            return None
        except Exception:
            return None

    async def fetch_pr_diff(self, repo: str, pr_number: int) -> str:
        """
        Récupère le diff d'une PR.

        Args:
            repo: Repository au format owner/repo
            pr_number: Numéro de la PR

        Returns:
            Contenu du diff
        """
        if not self.is_available:
            raise GitHubServiceError("gh CLI n'est pas disponible ou non authentifié")

        cmd = [
            "gh",
            "pr",
            "diff",
            str(pr_number),
            "--repo",
            repo,
        ]

        result = await asyncio.to_thread(
            subprocess.run,
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode != 0:
            raise GitHubServiceError(f"Erreur lors de la récupération du diff: {result.stderr}")

        return result.stdout

    async def fetch_pr_files(self, repo: str, pr_number: int) -> List[PRFile]:
        """
        Récupère la liste des fichiers modifiés dans une PR.

        Args:
            repo: Repository au format owner/repo
            pr_number: Numéro de la PR

        Returns:
            Liste des fichiers modifiés avec leurs patches
        """
        if not self.is_available:
            raise GitHubServiceError("gh CLI n'est pas disponible ou non authentifié")

        cmd = [
            "gh",
            "api",
            f"repos/{repo}/pulls/{pr_number}/files",
            "--paginate",
        ]

        result = await asyncio.to_thread(
            subprocess.run,
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode != 0:
            raise GitHubServiceError(
                f"Erreur lors de la récupération des fichiers: {result.stderr}"
            )

        files_data = json.loads(result.stdout)
        files = []

        for file_data in files_data:
            status_map = {
                "added": PRFileStatus.ADDED,
                "modified": PRFileStatus.MODIFIED,
                "removed": PRFileStatus.DELETED,
                "renamed": PRFileStatus.RENAMED,
            }

            status = status_map.get(file_data.get("status", "modified"), PRFileStatus.MODIFIED)

            files.append(
                PRFile(
                    path=file_data.get("filename", ""),
                    status=status,
                    additions=file_data.get("additions", 0),
                    deletions=file_data.get("deletions", 0),
                    patch=file_data.get("patch"),
                    previous_path=file_data.get("previous_filename"),
                )
            )

        return files

    async def post_review_comment(
        self,
        repo: str,
        pr_number: int,
        body: str,
        event: str = "COMMENT",
    ) -> bool:
        """
        Poste un commentaire de revue sur la PR.

        Args:
            repo: Repository au format owner/repo
            pr_number: Numéro de la PR
            body: Contenu du commentaire
            event: Type de revue (COMMENT, APPROVE, REQUEST_CHANGES)

        Returns:
            True si le commentaire a été posté avec succès
        """
        if not self.is_available:
            raise GitHubServiceError("gh CLI n'est pas disponible ou non authentifié")

        event_flag = {
            "COMMENT": "--comment",
            "APPROVE": "--approve",
            "REQUEST_CHANGES": "--request-changes",
        }.get(event.upper(), "--comment")

        cmd = [
            "gh",
            "pr",
            "review",
            str(pr_number),
            "--repo",
            repo,
            "--body",
            body,
            event_flag,
        ]

        result = await asyncio.to_thread(
            subprocess.run,
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            self.console.print(
                f"[red]Erreur lors de la publication du commentaire: {result.stderr}[/red]"
            )
            return False

        return True

    async def post_inline_comment(
        self,
        repo: str,
        pr_number: int,
        commit_id: str,
        file_path: str,
        line_number: int,
        body: str,
        side: str = "RIGHT",
    ) -> bool:
        """
        Poste un commentaire inline sur une ligne spécifique.

        Args:
            repo: Repository au format owner/repo
            pr_number: Numéro de la PR
            commit_id: SHA du commit
            file_path: Chemin du fichier
            line_number: Numéro de ligne
            body: Contenu du commentaire
            side: Côté du diff (LEFT ou RIGHT)

        Returns:
            True si le commentaire a été posté avec succès
        """
        if not self.is_available:
            raise GitHubServiceError("gh CLI n'est pas disponible ou non authentifié")

        # Utiliser l'API GitHub pour les commentaires inline
        cmd = [
            "gh",
            "api",
            f"repos/{repo}/pulls/{pr_number}/comments",
            "-X",
            "POST",
            "-f",
            f"body={body}",
            "-f",
            f"commit_id={commit_id}",
            "-f",
            f"path={file_path}",
            "-F",
            f"line={line_number}",
            "-f",
            f"side={side.upper()}",
        ]

        result = await asyncio.to_thread(
            subprocess.run,
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            # Les commentaires inline peuvent échouer si la ligne n'est pas dans le diff
            return False

        return True

    def get_local_user_email(self) -> Optional[str]:
        """
        Récupère l'email de l'utilisateur git local.

        Returns:
            Email de l'utilisateur ou None
        """
        try:
            result = subprocess.run(
                ["git", "config", "user.email"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                return result.stdout.strip()

            return None
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return None

    def get_gh_user_email(self) -> Optional[str]:
        """
        Récupère l'email de l'utilisateur GitHub authentifié.

        Returns:
            Email de l'utilisateur ou None
        """
        if not self.is_available:
            return None

        try:
            result = subprocess.run(
                ["gh", "api", "user", "--jq", ".email"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0 and result.stdout.strip():
                email = result.stdout.strip()
                if email and email != "null":
                    return email

            return None
        except Exception:
            return None

    def is_own_pr(self, pr_info: PRInfo) -> bool:
        """
        Vérifie si la PR appartient à l'utilisateur local.

        Compare l'email de l'auteur de la PR avec:
        1. git config user.email
        2. Email GitHub de l'utilisateur authentifié

        Args:
            pr_info: Informations sur la PR

        Returns:
            True si c'est la PR de l'utilisateur
        """
        local_email = self.get_local_user_email()
        gh_email = self.get_gh_user_email()

        if not pr_info.author_email:
            # Si pas d'email, comparer les logins
            try:
                result = subprocess.run(
                    ["gh", "api", "user", "--jq", ".login"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0:
                    gh_login = result.stdout.strip()
                    return gh_login.lower() == pr_info.author_login.lower()
            except Exception:
                pass
            return False

        author_email = pr_info.author_email.lower()

        if local_email and local_email.lower() == author_email:
            return True

        if gh_email and gh_email.lower() == author_email:
            return True

        return False

    async def get_pr_commits(self, repo: str, pr_number: int) -> List[dict]:
        """
        Récupère la liste des commits d'une PR.

        Args:
            repo: Repository au format owner/repo
            pr_number: Numéro de la PR

        Returns:
            Liste des commits avec leurs métadonnées
        """
        if not self.is_available:
            raise GitHubServiceError("gh CLI n'est pas disponible ou non authentifié")

        cmd = [
            "gh",
            "api",
            f"repos/{repo}/pulls/{pr_number}/commits",
        ]

        result = await asyncio.to_thread(
            subprocess.run,
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            raise GitHubServiceError(f"Erreur lors de la récupération des commits: {result.stderr}")

        return json.loads(result.stdout)
