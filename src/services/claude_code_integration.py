"""
Claude Code Integration - Intégration avec Claude Code CLI pour la correction de bugs
Exécute Claude Code directement en arrière-plan pour corriger les bugs
Supporte le mode parallèle pour accélérer les corrections
"""

import asyncio
import os
import platform
import re
import shutil
import signal
import subprocess
import tempfile
from datetime import datetime
from typing import Callable
from typing import List
from typing import Optional
from typing import Tuple

# Constante pour identifier les erreurs de rate limit (patterns spécifiques aux erreurs)
RATE_LIMIT_PATTERNS = [
    r"rate.?limit.*(?:error|exceeded|reached|hit)",
    r"(?:error|failed).*rate.?limit",
    r"too many requests",
    r"usage.?limit.*exceeded",
    r"quota.*exceeded",
    r"limit.*reached",
    r"(?:please\s+)?try again (?:in|after) (\d+)\s*(hour|minute|second|hr|min|sec)",
    r"(?:please\s+)?wait.*?(\d+)\s*(hour|minute|second|hr|min|sec).*(?:before|to|and)",
    r"you(?:'ve| have)? (?:exceeded|reached|hit).*(?:limit|quota)",
    r"(?:api|request).*limit.*(?:exceeded|reached)",
]

# Patterns qui indiquent que ce N'EST PAS un rate limit (status display, etc.)
RATE_LIMIT_EXCLUSIONS = [
    r"resets?\s+\w+\s*\d",  # "Resets 11pm", "Resets Jan 8"
    r"\d+%\s*used",  # "75% used"
    r"current\s+(?:session|week)",  # Status display headers
    r"extra usage",  # Settings display
]

# Pattern pour supprimer les codes ANSI
ANSI_ESCAPE_PATTERN = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]|\x1b\].*?\x07|\x1b[PX^_].*?\x1b\\")


def sanitize_terminal_output(text: str) -> str:
    """
    Nettoie le texte pour un affichage compatible avec le terminal.

    - Supprime les codes ANSI
    - Remplace les caractères non-imprimables
    - Gère les caractères Unicode problématiques sur Windows

    Args:
        text: Le texte à nettoyer

    Returns:
        Le texte nettoyé compatible terminal
    """
    if not text:
        return ""

    # Supprimer les codes ANSI
    text = ANSI_ESCAPE_PATTERN.sub("", text)

    # Remplacer les caractères de contrôle (sauf newline, tab, carriage return)
    cleaned = []
    for char in text:
        code = ord(char)
        if code < 32 and code not in (9, 10, 13):  # Tab, LF, CR
            cleaned.append(" ")
        elif code == 0x9D:  # Caractère problématique Windows
            cleaned.append(" ")
        elif code >= 127 and code < 160:  # Caractères de contrôle étendus
            cleaned.append(" ")
        else:
            cleaned.append(char)

    return "".join(cleaned)


from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn
from rich.progress import Progress
from rich.progress import SpinnerColumn
from rich.progress import TaskID
from rich.progress import TaskProgressColumn
from rich.progress import TextColumn
from rich.progress import TimeElapsedColumn
from rich.prompt import Confirm
from rich.table import Table

from src.models.data_models import BugIdentifier


class RateLimitError(Exception):
    """Exception levée quand Claude Code atteint sa limite d'usage."""

    def __init__(self, message: str, wait_hours: float = 0):
        super().__init__(message)
        self.wait_hours = wait_hours


class ClaudeCodeIntegration:
    """Intégration avec Claude Code CLI pour la correction automatique de bugs"""

    @staticmethod
    def _detect_rate_limit(output: str) -> Optional[Tuple[bool, float]]:
        """
        Détecte si la sortie contient une erreur de rate limit.

        Args:
            output: La sortie (stdout ou stderr) de Claude Code

        Returns:
            Tuple (is_rate_limited, wait_hours) ou None si pas de rate limit
        """
        if not output:
            return None

        output_lower = output.lower()

        # D'abord, vérifier les patterns d'exclusion (status display, etc.)
        for exclusion in RATE_LIMIT_EXCLUSIONS:
            if re.search(exclusion, output_lower):
                # C'est probablement un affichage de status, pas une erreur
                return None

        # Vérifier les patterns de rate limit
        for pattern in RATE_LIMIT_PATTERNS:
            match = re.search(pattern, output_lower)
            if match:
                # Essayer d'extraire le temps d'attente
                wait_hours = 0.0

                # Chercher un pattern de temps dans le message d'erreur
                time_match = re.search(
                    r"(\d+(?:\.\d+)?)\s*(hour|hr|minute|min|second|sec)s?",
                    output_lower,
                )
                if time_match:
                    value = float(time_match.group(1))
                    unit = time_match.group(2)

                    if "hour" in unit or "hr" in unit:
                        wait_hours = value
                    elif "minute" in unit or "min" in unit:
                        wait_hours = value / 60
                    elif "second" in unit or "sec" in unit:
                        wait_hours = value / 3600

                # Si pas de temps trouvé, supposer ~5 heures (limite typique)
                if wait_hours == 0:
                    wait_hours = 5.0

                return (True, wait_hours)

        return None

    def __init__(self, root_dir: str):
        """
        Initialise l'intégration Claude Code.

        Args:
            root_dir: Répertoire racine du projet à analyser
        """
        self.root_dir = root_dir
        self.console = Console()
        self._claude_path: Optional[str] = None
        self._is_available: Optional[bool] = None

    @property
    def is_available(self) -> bool:
        """Vérifie si Claude Code est disponible sur le système."""
        if self._is_available is None:
            self._is_available = self.detect_claude_code()
        return self._is_available

    @property
    def claude_path(self) -> Optional[str]:
        """Retourne le chemin vers l'exécutable Claude Code."""
        if self._claude_path is None:
            self.detect_claude_code()
        return self._claude_path

    def detect_claude_code(self) -> bool:
        """
        Détecte si Claude Code est installé sur le système.

        Cherche 'claude' dans:
        1. PATH système
        2. Emplacements standards par OS

        Returns:
            True si Claude Code est trouvé, False sinon
        """
        # Chercher dans PATH
        claude_in_path = shutil.which("claude")
        if claude_in_path:
            self._claude_path = claude_in_path
            return True

        # Emplacements standards par OS
        system = platform.system()
        standard_paths: List[str] = []

        if system == "Windows":
            standard_paths = [
                os.path.expandvars(r"%LOCALAPPDATA%\Programs\claude\claude.exe"),
                os.path.expandvars(r"%APPDATA%\npm\claude.cmd"),
                os.path.expandvars(r"%PROGRAMFILES%\Claude\claude.exe"),
            ]
        elif system == "Darwin":  # macOS
            standard_paths = [
                "/usr/local/bin/claude",
                os.path.expanduser("~/.npm-global/bin/claude"),
                os.path.expanduser("~/Library/Application Support/Claude/claude"),
            ]
        else:  # Linux
            standard_paths = [
                "/usr/local/bin/claude",
                "/usr/bin/claude",
                os.path.expanduser("~/.local/bin/claude"),
                os.path.expanduser("~/.npm-global/bin/claude"),
            ]

        for path in standard_paths:
            if os.path.isfile(path) and os.access(path, os.X_OK):
                self._claude_path = path
                return True

        return False

    def test_claude_code(self) -> Tuple[bool, str]:
        """
        Teste si Claude Code fonctionne correctement.

        Returns:
            Tuple (success, message)
        """
        if not self.is_available:
            return False, "Claude Code n'est pas installé"

        try:
            # Test 1: Vérifier la version
            result = subprocess.run(
                [self._claude_path or "claude", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
                encoding="utf-8",
                errors="replace",
            )
            if result.returncode == 0:
                version = result.stdout.strip() or result.stderr.strip()
                return True, f"Claude Code v{version}"
            else:
                return False, f"Erreur: {result.stderr}"
        except subprocess.TimeoutExpired:
            return False, "Timeout lors du test"
        except Exception as e:
            return False, f"Erreur: {e}"

    def test_claude_code_execution(self, timeout: int = 60) -> Tuple[bool, str]:
        """
        Teste si Claude Code peut exécuter des commandes.

        Returns:
            Tuple (success, message)
        """
        if not self.is_available:
            return False, "Claude Code n'est pas installé"

        try:
            cmd = [
                self._claude_path or "claude",
                "--print",
                "--dangerously-skip-permissions",
                "--output-format",
                "text",
                "--no-session-persistence",
                "Réponds uniquement par 'OK' sans rien d'autre.",
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.root_dir,
                env={**os.environ, "FORCE_COLOR": "0", "NO_COLOR": "1"},
                encoding="utf-8",
                errors="replace",
            )

            if result.returncode == 0:
                response = result.stdout.strip()[:100]
                return True, f"Réponse: {response}"
            else:
                return False, f"Erreur: {result.stderr[:200]}"
        except subprocess.TimeoutExpired:
            return False, f"Timeout après {timeout}s"
        except Exception as e:
            return False, f"Erreur: {e}"

    def run_claude_direct(
        self, prompt: str, timeout: int = 300
    ) -> Tuple[bool, str, str, Optional[float]]:
        """
        Exécute Claude Code directement en arrière-plan (sans terminal).

        Args:
            prompt: Le prompt à envoyer
            timeout: Timeout en secondes (défaut: 5 minutes)

        Returns:
            Tuple (success, stdout, stderr, rate_limit_hours)
            rate_limit_hours est None si pas de rate limit
        """
        if not self.is_available:
            return False, "", "Claude Code n'est pas installé", None

        try:
            # Écrire le prompt dans un fichier temporaire pour éviter les problèmes d'échappement
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".txt", delete=False, encoding="utf-8"
            ) as f:
                f.write(prompt)
                prompt_file = f.name

            try:
                # Construire la commande avec tous les flags nécessaires pour le mode non-interactif
                cmd = [
                    self._claude_path or "claude",
                    "--print",  # Mode non-interactif (print et exit)
                    "--dangerously-skip-permissions",  # Bypass permissions
                    "--output-format",
                    "text",  # Sortie texte simple
                    "--no-session-persistence",  # Pas de persistance de session
                    prompt,
                ]

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=self.root_dir,
                    env={
                        **os.environ,
                        "FORCE_COLOR": "0",
                        "NO_COLOR": "1",
                    },  # Désactiver les couleurs
                    encoding="utf-8",
                    errors="replace",  # Remplace les caractères non-décodables (Windows)
                )

                # Vérifier si c'est un rate limit
                combined_output = f"{result.stdout}\n{result.stderr}"
                rate_limit_info = self._detect_rate_limit(combined_output)
                if rate_limit_info:
                    _, wait_hours = rate_limit_info
                    return False, result.stdout, result.stderr, wait_hours

                return result.returncode == 0, result.stdout, result.stderr, None

            finally:
                # Nettoyer le fichier temporaire
                try:
                    os.unlink(prompt_file)
                except Exception:
                    pass

        except subprocess.TimeoutExpired:
            return False, "", f"Timeout après {timeout}s", None
        except Exception as e:
            return False, "", f"Erreur: {e}", None

    def fix_bug_direct(
        self, bug: BugIdentifier, timeout: int = 300
    ) -> Tuple[bool, str, Optional[float]]:
        """
        Corrige un bug directement via Claude Code (sans fenêtre terminal).

        Args:
            bug: Le bug à corriger
            timeout: Timeout en secondes

        Returns:
            Tuple (success, output, rate_limit_hours)
            rate_limit_hours est None si pas de rate limit
        """
        prompt = self._generate_fix_prompt(bug)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            progress.add_task(f"🔧 Correction de {bug.id}...", total=None)
            success, stdout, stderr, rate_limit_hours = self.run_claude_direct(prompt, timeout)

        if rate_limit_hours is not None:
            return False, stderr or stdout, rate_limit_hours

        if success:
            return True, stdout, None
        else:
            return False, stderr or stdout, None

    def _escape_prompt_for_shell(self, prompt: str) -> str:
        """
        Échappe le prompt pour utilisation en ligne de commande.

        Args:
            prompt: Le prompt à échapper

        Returns:
            Le prompt échappé pour le shell
        """
        # Remplacer les caractères problématiques
        escaped = prompt.replace("\\", "\\\\")
        escaped = escaped.replace('"', '\\"')
        escaped = escaped.replace("'", "\\'")
        escaped = escaped.replace("\n", " ")
        escaped = escaped.replace("\r", "")
        return escaped

    def _generate_fix_prompt(self, bug: BugIdentifier) -> str:
        """
        Génère le prompt de correction pour Claude Code.

        Args:
            bug: Le bug à corriger

        Returns:
            Le prompt formaté pour Claude Code
        """
        prompt_parts = [
            f"Tu dois corriger le bug suivant dans le fichier '{bug.file_path}':",
            "",
            f"**ID du Bug**: {bug.id}",
            f"**Type**: {bug.bug_type}",
            f"**Sévérité**: {bug.severity}",
        ]

        if bug.line_number:
            prompt_parts.append(f"**Ligne**: {bug.line_number}")

        prompt_parts.extend(
            [
                "",
                f"**Description**: {bug.description}",
            ]
        )

        if bug.recommendation:
            prompt_parts.append(f"**Recommandation**: {bug.recommendation}")

        if bug.impacted_files:
            prompt_parts.append("")
            prompt_parts.append(
                f"**Fichiers impactés** ({len(bug.impacted_files)}): {', '.join(bug.impacted_files[:5])}"
            )
            if len(bug.impacted_files) > 5:
                prompt_parts.append(f"  ... et {len(bug.impacted_files) - 5} autres")

        prompt_parts.extend(
            [
                "",
                "Instructions:",
                "1. Lis le fichier concerné",
                "2. Identifie et corrige le problème",
                "3. Vérifie que la correction n'introduit pas de régression",
                "4. Confirme la correction une fois terminée",
            ]
        )

        return "\n".join(prompt_parts)

    def _get_terminal_command(self, prompt: str) -> Optional[List[str]]:
        """
        Génère la commande pour lancer Claude Code dans un nouveau terminal.

        Args:
            prompt: Le prompt à passer à Claude Code

        Returns:
            La commande à exécuter, ou None si non supporté
        """
        system = platform.system()
        escaped_prompt = self._escape_prompt_for_shell(prompt)
        claude_cmd = self._claude_path or "claude"

        if system == "Windows":
            # Windows: utiliser start avec cmd
            full_cmd = f'{claude_cmd} --dangerously-skip-permissions -p "{escaped_prompt}"'
            return ["cmd", "/c", "start", "cmd", "/k", full_cmd]

        elif system == "Darwin":  # macOS
            # macOS: utiliser osascript pour ouvrir Terminal
            applescript = f"""
            tell application "Terminal"
                activate
                do script "{claude_cmd} --dangerously-skip-permissions -p \\"{escaped_prompt}\\""
            end tell
            """
            return ["osascript", "-e", applescript]

        else:  # Linux
            # Linux: détecter le terminal disponible
            terminals = [
                (
                    "gnome-terminal",
                    [
                        "gnome-terminal",
                        "--",
                        claude_cmd,
                        "--dangerously-skip-permissions",
                        "-p",
                        prompt,
                    ],
                ),
                (
                    "konsole",
                    ["konsole", "-e", claude_cmd, "--dangerously-skip-permissions", "-p", prompt],
                ),
                (
                    "xfce4-terminal",
                    [
                        "xfce4-terminal",
                        "-e",
                        f'{claude_cmd} --dangerously-skip-permissions -p "{escaped_prompt}"',
                    ],
                ),
                (
                    "xterm",
                    ["xterm", "-e", claude_cmd, "--dangerously-skip-permissions", "-p", prompt],
                ),
                (
                    "terminator",
                    [
                        "terminator",
                        "-e",
                        f'{claude_cmd} --dangerously-skip-permissions -p "{escaped_prompt}"',
                    ],
                ),
            ]

            for term_name, term_cmd in terminals:
                if shutil.which(term_name):
                    return term_cmd

            # Fallback: essayer avec x-terminal-emulator (Debian/Ubuntu)
            if shutil.which("x-terminal-emulator"):
                return [
                    "x-terminal-emulator",
                    "-e",
                    f'{claude_cmd} --dangerously-skip-permissions -p "{escaped_prompt}"',
                ]

        return None

    def fix_bug_in_new_terminal(self, bug: BugIdentifier) -> bool:
        """
        Lance Claude Code dans un nouveau terminal pour corriger un bug.

        Args:
            bug: Le bug à corriger

        Returns:
            True si le processus a été lancé avec succès
        """
        if not self.is_available:
            self.console.print("[red]❌ Claude Code n'est pas installé[/red]")
            return False

        prompt = self._generate_fix_prompt(bug)
        terminal_cmd = self._get_terminal_command(prompt)

        if not terminal_cmd:
            self.console.print("[red]❌ Impossible de détecter un terminal compatible[/red]")
            return False

        try:
            # Lancer le terminal en arrière-plan
            if platform.system() == "Windows":
                # Windows: utiliser shell=True pour la commande start
                subprocess.Popen(" ".join(terminal_cmd), shell=True, cwd=self.root_dir)
            else:
                subprocess.Popen(terminal_cmd, cwd=self.root_dir)

            return True
        except Exception as e:
            self.console.print(f"[red]❌ Erreur lors du lancement de Claude Code: {e}[/red]")
            return False

    def fix_bug_interactive(self, bug: BugIdentifier) -> bool:
        """
        Lance Claude Code de manière interactive pour corriger un bug.
        Attend que l'utilisateur confirme la correction.

        Args:
            bug: Le bug à corriger

        Returns:
            True si le bug a été corrigé, False sinon
        """
        # Afficher les détails du bug
        self._display_bug_details(bug)

        # Lancer Claude Code
        launched = self.fix_bug_in_new_terminal(bug)
        if not launched:
            return False

        self.console.print()
        self.console.print("[cyan]💡 Claude Code a été lancé dans une nouvelle fenêtre.[/cyan]")
        self.console.print("[cyan]   Corrigez le bug, puis revenez ici pour confirmer.[/cyan]")
        self.console.print()

        # Attendre la confirmation de l'utilisateur
        fixed = Confirm.ask("Ce bug a-t-il été corrigé?", default=True)
        return fixed

    def _display_bug_details(self, bug: BugIdentifier):
        """Affiche les détails d'un bug dans un panel formaté."""
        severity_colors = {
            "critical": "red bold",
            "high": "red",
            "medium": "yellow",
            "low": "green",
        }
        severity_color = severity_colors.get(bug.severity, "white")

        content = [
            f"[bold]ID:[/bold] {bug.id}",
            f"[bold]Fichier:[/bold] {bug.file_path}",
        ]

        if bug.line_number:
            content.append(f"[bold]Ligne:[/bold] {bug.line_number}")

        content.extend(
            [
                f"[bold]Type:[/bold] {bug.bug_type}",
                f"[bold]Sévérité:[/bold] [{severity_color}]{bug.severity}[/{severity_color}]",
                "",
                "[bold]Description:[/bold]",
                f"  {bug.description}",
            ]
        )

        if bug.recommendation:
            content.extend(
                [
                    "",
                    "[bold]Recommandation:[/bold]",
                    f"  {bug.recommendation}",
                ]
            )

        if bug.impacted_files:
            content.extend(
                [
                    "",
                    f"[bold]Fichiers impactés ({len(bug.impacted_files)}):[/bold]",
                ]
            )
            for f in bug.impacted_files[:5]:
                content.append(f"  • {f}")
            if len(bug.impacted_files) > 5:
                content.append(f"  ... et {len(bug.impacted_files) - 5} autres")

        self.console.print(
            Panel(
                "\n".join(content),
                title=f"🐛 Bug {bug.id}",
                border_style="blue",
            )
        )

    def display_bugs_summary(self, bugs: List[BugIdentifier]):
        """
        Affiche un résumé compact des bugs à corriger.

        Args:
            bugs: Liste des bugs à afficher
        """
        from collections import Counter

        # Calculer les statistiques
        unique_files = set(bug.file_path for bug in bugs)
        lines_with_number = [bug.line_number for bug in bugs if bug.line_number]

        # Compteurs par type et sévérité
        type_counts = Counter(bug.bug_type for bug in bugs)
        severity_counts = Counter(bug.severity for bug in bugs)

        # Couleurs pour les sévérités
        severity_colors = {
            "critical": "red bold",
            "high": "red",
            "medium": "yellow",
            "low": "green",
        }

        # Afficher le résumé compact
        self.console.print()
        self.console.print("[bold cyan]📊 Résumé des bugs à corriger[/bold cyan]")
        self.console.print("─" * 50)

        # Stats principales
        self.console.print(f"  [bold]Total:[/bold] {len(bugs)} bugs")
        self.console.print(f"  [bold]Fichiers:[/bold] {len(unique_files)} fichiers affectés")
        if lines_with_number:
            self.console.print(
                f"  [bold]Lignes:[/bold] {len(lines_with_number)} emplacements précis"
            )

        # Sévérité breakdown
        self.console.print()
        self.console.print("  [bold]Par sévérité:[/bold]")
        for sev in ["critical", "high", "medium", "low"]:
            count = severity_counts.get(sev, 0)
            if count > 0:
                color = severity_colors.get(sev, "white")
                bar = "█" * min(count // 5 + 1, 20)
                self.console.print(f"    [{color}]{sev:8}[/{color}] {bar} {count}")

        # Types breakdown
        if type_counts:
            self.console.print()
            self.console.print("  [bold]Par type:[/bold]")
            for bug_type, count in type_counts.most_common():
                self.console.print(f"    [blue]{bug_type:12}[/blue] {count}")

        self.console.print("─" * 50)

    # Alias pour compatibilité
    def display_bugs_table(self, bugs: List[BugIdentifier]):
        """Alias vers display_bugs_summary pour compatibilité."""
        self.display_bugs_summary(bugs)

    def run_fix_session(
        self,
        bugs: List[BugIdentifier],
        auto_mode: bool = False,
        direct_mode: bool = True,
        on_bug_status: Optional[Callable[[BugIdentifier], None]] = None,
    ) -> dict:
        """
        Exécute une session de correction de bugs.

        Args:
            bugs: Liste des bugs à corriger
            auto_mode: Si True, ne demande pas de confirmation entre les bugs
            direct_mode: Si True, exécute Claude Code en arrière-plan (sans fenêtre terminal)
            on_bug_status: Callback appelé après chaque bug (corrigé ou échoué) pour sauvegarder l'état

        Returns:
            Statistiques de la session (fixed, skipped, failed, rate_limited, remaining, wait_hours)
        """
        stats = {
            "fixed": 0,
            "skipped": 0,
            "failed": 0,
            "total": len(bugs),
            "rate_limited": False,
            "user_stopped": False,
            "remaining": 0,
            "wait_hours": 0.0,
        }

        if not bugs:
            self.console.print("[yellow]Aucun bug à corriger.[/yellow]")
            return stats

        # Variable pour l'arrêt utilisateur
        user_stopped = False

        def handle_interrupt(signum, frame):
            nonlocal user_stopped
            user_stopped = True
            self.console.print("\n[yellow]⏹️  Arrêt demandé après ce bug...[/yellow]")

        # Installer le handler
        original_handler = signal.signal(signal.SIGINT, handle_interrupt)

        # Tester Claude Code avant de commencer
        self.console.print("[cyan]🔍 Vérification de Claude Code...[/cyan]")
        test_ok, test_msg = self.test_claude_code()
        if not test_ok:
            self.console.print(f"[red]❌ {test_msg}[/red]")
            return stats
        self.console.print(f"[green]✅ {test_msg}[/green]")
        self.console.print()

        # Afficher le tableau récapitulatif
        self.display_bugs_table(bugs)
        self.console.print()

        mode_msg = "en arrière-plan" if direct_mode else "dans une nouvelle fenêtre"
        self.console.print(f"[dim]Mode: Claude Code sera exécuté {mode_msg}[/dim]")
        self.console.print("[dim]Appuyez sur Ctrl+C pour arrêter[/dim]")
        self.console.print()

        if not auto_mode:
            proceed = Confirm.ask(
                f"Voulez-vous corriger ces {len(bugs)} bug(s) avec Claude Code?",
                default=True,
            )
            if not proceed:
                self.console.print("[yellow]Correction annulée.[/yellow]")
                return stats

        # Corriger chaque bug un par un
        for i, bug in enumerate(bugs, 1):
            # Vérifier si l'utilisateur a demandé l'arrêt
            if user_stopped:
                stats["user_stopped"] = True
                stats["remaining"] = len(bugs) - i + 1
                break

            self.console.print()
            self.console.rule(f"[bold blue]Bug {i}/{len(bugs)}")
            self._display_bug_details(bug)

            if direct_mode:
                # Mode direct: exécuter en arrière-plan
                success, output, rate_limit_hours = self.fix_bug_direct(bug)

                # Vérifier si rate limit atteint
                if rate_limit_hours is not None:
                    stats["rate_limited"] = True
                    stats["wait_hours"] = rate_limit_hours
                    stats["remaining"] = len(bugs) - i + 1
                    break

                # Nettoyer l'output pour le terminal
                clean_output = sanitize_terminal_output(output) if output else ""

                if success:
                    stats["fixed"] += 1
                    self.console.print(f"[green]✅ {bug.id} corrigé[/green]")

                    # Marquer le bug comme corrigé
                    bug.fixed = True
                    bug.fixed_at = datetime.now().isoformat()
                    bug.failed = False  # Reset si précédemment échoué
                    # Extraire un résumé de la correction (dernières lignes utiles)
                    if clean_output:
                        lines = [ln for ln in clean_output.strip().split("\n") if ln.strip()]
                        bug.fix_summary = "\n".join(lines[-5:]) if lines else "Corrigé"
                    else:
                        bug.fix_summary = "Corrigé sans détails"

                    # Sauvegarder l'état via callback
                    if on_bug_status:
                        on_bug_status(bug)

                    if clean_output:
                        # Afficher un résumé de la sortie
                        lines = clean_output.strip().split("\n")
                        if len(lines) > 10:
                            self.console.print("[dim]Résumé de la correction:[/dim]")
                            for line in lines[-10:]:
                                self.console.print(f"  [dim]{line}[/dim]")
                        else:
                            for line in lines:
                                self.console.print(f"  [dim]{line}[/dim]")
                else:
                    stats["failed"] += 1
                    self.console.print(f"[red]❌ Échec de la correction de {bug.id}[/red]")

                    # Marquer le bug comme échoué
                    bug.failed = True
                    bug.failed_at = datetime.now().isoformat()
                    bug.failure_reason = (
                        clean_output[:500] if clean_output else "Échec sans détails"
                    )

                    # Sauvegarder l'état via callback
                    if on_bug_status:
                        on_bug_status(bug)

                    if clean_output:
                        self.console.print(f"[red]{clean_output[:500]}[/red]")

                    if not auto_mode and i < len(bugs):
                        skip = Confirm.ask("Continuer avec le bug suivant?", default=True)
                        if not skip:
                            stats["failed"] += len(bugs) - i - 1
                            self.console.print("[yellow]Session interrompue.[/yellow]")
                            break
            else:
                # Mode terminal: ouvrir une fenêtre
                fixed = self.fix_bug_interactive(bug)

                if fixed:
                    stats["fixed"] += 1
                    self.console.print(f"[green]✅ {bug.id} marqué comme corrigé[/green]")

                    # Marquer le bug comme corrigé
                    bug.fixed = True
                    bug.fixed_at = datetime.now().isoformat()
                    bug.failed = False  # Reset si précédemment échoué
                    bug.fix_summary = "Corrigé via mode terminal interactif"

                    # Sauvegarder l'état via callback
                    if on_bug_status:
                        on_bug_status(bug)
                else:
                    if not auto_mode and i < len(bugs):
                        skip = Confirm.ask("Passer au bug suivant?", default=True)
                        if skip:
                            stats["skipped"] += 1
                            self.console.print(
                                f"[yellow]⏭️  {bug.id} passé, continuation...[/yellow]"
                            )
                        else:
                            stats["failed"] += len(bugs) - i
                            self.console.print("[yellow]Session interrompue.[/yellow]")
                            break
                    else:
                        stats["skipped"] += 1

        # Restaurer le handler original
        signal.signal(signal.SIGINT, original_handler)

        # Afficher le résumé
        self.console.print()

        if stats["rate_limited"]:
            # Afficher le message de rate limit
            wait_hours = stats["wait_hours"]
            if wait_hours >= 1:
                wait_display = f"{wait_hours:.1f} heures"
            else:
                wait_display = f"{int(wait_hours * 60)} minutes"

            self.console.print(
                Panel(
                    f"[bold red]⚠️  LIMITE D'USAGE CLAUDE CODE ATTEINTE[/bold red]\n\n"
                    f"[yellow]La limite d'utilisation de Claude Code a été atteinte.[/yellow]\n"
                    f"[cyan]Reprendre dans environ [bold]{wait_display}[/bold][/cyan]\n\n"
                    f"[dim]Bugs corrigés avant la limite: {stats['fixed']}/{stats['total']}[/dim]\n"
                    f"[dim]Bugs restants à traiter: {stats['remaining']}[/dim]\n\n"
                    f"[green]💡 Astuce: Relancez la commande plus tard pour continuer.[/green]",
                    title="🛑 Rate Limit",
                    border_style="red",
                )
            )
        elif stats["user_stopped"]:
            # Afficher le message d'arrêt utilisateur
            self.console.print(
                Panel(
                    f"[bold yellow]⏹️  SESSION ARRÊTÉE PAR L'UTILISATEUR[/bold yellow]\n\n"
                    f"[dim]Bugs corrigés: {stats['fixed']}/{stats['total']}[/dim]\n"
                    f"[dim]Bugs échoués: {stats['failed']}[/dim]\n"
                    f"[dim]Bugs restants: {stats['remaining']}[/dim]\n\n"
                    f"[green]💡 Relancez la commande pour continuer avec les bugs restants.[/green]",
                    title="⏹️ Arrêt manuel",
                    border_style="yellow",
                )
            )
        else:
            self.console.rule("[bold green]Résumé de la session")
            self.console.print(f"[green]✅ Corrigés:[/green] {stats['fixed']}")
            self.console.print(f"[yellow]⏭️  Passés:[/yellow] {stats['skipped']}")
            self.console.print(f"[red]❌ Échoués:[/red] {stats['failed']}")
            self.console.print(f"[dim]Total:[/dim] {stats['total']}")

        return stats

    async def _fix_bug_async(
        self,
        bug: BugIdentifier,
        timeout: int = 300,
    ) -> Tuple[BugIdentifier, bool, str, Optional[float]]:
        """
        Corrige un bug de manière asynchrone.

        Args:
            bug: Le bug à corriger
            timeout: Timeout en secondes

        Returns:
            Tuple (bug, success, output, rate_limit_hours)
            rate_limit_hours est None si pas de rate limit, sinon le temps d'attente en heures
        """
        prompt = self._generate_fix_prompt(bug)

        try:
            # Utiliser asyncio.to_thread pour exécuter subprocess de manière non-bloquante
            def run_fix():
                cmd = [
                    self._claude_path or "claude",
                    "--print",
                    "--dangerously-skip-permissions",
                    "--output-format",
                    "text",
                    "--no-session-persistence",
                    prompt,
                ]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=self.root_dir,
                    env={**os.environ, "FORCE_COLOR": "0", "NO_COLOR": "1"},
                    encoding="utf-8",
                    errors="replace",  # Remplace les caractères non-décodables
                )
                return result.returncode == 0, result.stdout, result.stderr

            success, stdout, stderr = await asyncio.to_thread(run_fix)
            output = stdout if success else (stderr or stdout)

            # Vérifier si c'est un rate limit
            combined_output = f"{stdout}\n{stderr}"
            rate_limit_info = self._detect_rate_limit(combined_output)
            if rate_limit_info:
                _, wait_hours = rate_limit_info
                return bug, False, output, wait_hours

            return bug, success, output, None

        except subprocess.TimeoutExpired:
            return bug, False, f"Timeout après {timeout}s", None
        except Exception as e:
            return bug, False, f"Erreur: {e}", None

    async def run_fix_session_parallel(
        self,
        bugs: List[BugIdentifier],
        batch_size: int = 10,
        timeout: int = 300,
        on_bug_status: Optional[Callable[[BugIdentifier], None]] = None,
    ) -> dict:
        """
        Exécute une session de correction de bugs en parallèle.

        Utilise un pool de workers qui exécutent les corrections simultanément.
        Quand un worker termine, il prend immédiatement le bug suivant de la queue.
        Détecte les rate limits et arrête proprement la session si atteint.

        Args:
            bugs: Liste des bugs à corriger
            batch_size: Nombre de corrections parallèles (défaut: 10)
            timeout: Timeout par bug en secondes (défaut: 300)
            on_bug_status: Callback appelé après chaque bug (corrigé ou échoué)

        Returns:
            Statistiques de la session (fixed, skipped, failed, rate_limited, remaining)
        """
        stats = {
            "fixed": 0,
            "skipped": 0,
            "failed": 0,
            "total": len(bugs),
            "rate_limited": False,
            "user_stopped": False,
            "remaining": 0,
            "wait_hours": 0.0,
        }

        if not bugs:
            self.console.print("[yellow]Aucun bug à corriger.[/yellow]")
            return stats

        # Tester Claude Code avant de commencer
        self.console.print("[cyan]🔍 Vérification de Claude Code...[/cyan]")
        test_ok, test_msg = self.test_claude_code()
        if not test_ok:
            self.console.print(f"[red]❌ {test_msg}[/red]")
            return stats
        self.console.print(f"[green]✅ {test_msg}[/green]")
        self.console.print()

        # Afficher le tableau récapitulatif
        self.display_bugs_table(bugs)
        self.console.print()

        effective_batch_size = min(batch_size, len(bugs))
        self.console.print(
            f"[cyan]⚡ Mode parallèle: {effective_batch_size} corrections simultanées[/cyan]"
        )
        self.console.print("[dim]   Appuyez sur Ctrl+C pour arrêter[/dim]")
        self.console.print()

        # Queue des bugs à traiter
        bug_queue: asyncio.Queue = asyncio.Queue()
        for bug in bugs:
            await bug_queue.put(bug)

        # Compteurs et événements thread-safe
        completed_count = 0
        lock = asyncio.Lock()
        rate_limit_event = asyncio.Event()  # Signal pour arrêter tous les workers
        user_stop_event = asyncio.Event()  # Signal pour arrêt utilisateur (Ctrl+C)
        rate_limit_wait_hours = 0.0
        user_stopped = False

        # Handler pour Ctrl+C
        def handle_interrupt(signum, frame):
            nonlocal user_stopped
            user_stopped = True
            user_stop_event.set()
            self.console.print("\n[yellow]⏹️  Arrêt demandé... Finalisation en cours...[/yellow]")

        # Installer le handler
        original_handler = signal.signal(signal.SIGINT, handle_interrupt)

        # Créer la barre de progression
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TextColumn("•"),
            TimeElapsedColumn(),
            console=self.console,
        )

        async def worker(worker_id: int, main_task: TaskID):
            """Worker qui traite les bugs de la queue."""
            nonlocal completed_count, rate_limit_wait_hours
            worker_prefix = f"[dim cyan]Worker {worker_id + 1}[/dim cyan]"

            while not rate_limit_event.is_set() and not user_stop_event.is_set():
                try:
                    bug = bug_queue.get_nowait()
                except asyncio.QueueEmpty:
                    break

                # Afficher le démarrage verbose
                file_short = bug.file_path.split("/")[-1] if "/" in bug.file_path else bug.file_path
                desc_short = (
                    bug.description[:60] + "..." if len(bug.description) > 60 else bug.description
                )
                self.console.print(
                    f"  {worker_prefix} [bold]→[/bold] [cyan]{bug.id}[/cyan] "
                    f"[dim]({file_short}:{bug.line_number or '-'})[/dim]"
                )
                sev_color = {
                    "critical": "red bold",
                    "high": "red",
                    "medium": "yellow",
                    "low": "green",
                }.get(bug.severity, "white")
                self.console.print(
                    f"    [dim]Type:[/dim] [blue]{bug.bug_type}[/blue] "
                    f"[dim]Sev:[/dim] [{sev_color}]{bug.severity}[/{sev_color}]"
                )
                self.console.print(f"    [dim]{desc_short}[/dim]")

                # Mettre à jour la description
                progress.update(
                    main_task,
                    description=f"[bold]Worker {worker_id + 1}: {file_short}[/bold]",
                )

                # Exécuter la correction
                bug, success, output, wait_hours = await self._fix_bug_async(bug, timeout)

                async with lock:
                    # Vérifier si rate limit atteint
                    if wait_hours is not None:
                        rate_limit_wait_hours = wait_hours
                        rate_limit_event.set()  # Signal aux autres workers d'arrêter
                        stats["rate_limited"] = True
                        stats["wait_hours"] = wait_hours
                        bug_queue.task_done()
                        break

                    # Nettoyer l'output pour le terminal
                    clean_output = sanitize_terminal_output(output) if output else ""

                    completed_count += 1

                    if success:
                        stats["fixed"] += 1
                        bug.fixed = True
                        bug.fixed_at = datetime.now().isoformat()
                        bug.failed = False  # Reset si précédemment échoué
                        if clean_output:
                            lines = [ln for ln in clean_output.strip().split("\n") if ln.strip()]
                            bug.fix_summary = "\n".join(lines[-3:]) if lines else "Corrigé"
                            # Afficher les dernières lignes de l'output (verbose)
                            summary_lines = lines[-2:] if len(lines) >= 2 else lines
                            for line in summary_lines:
                                if line.strip():
                                    self.console.print(f"    [dim green]│ {line[:80]}[/dim green]")
                        else:
                            bug.fix_summary = "Corrigé"

                        if on_bug_status:
                            on_bug_status(bug)

                        self.console.print(
                            f"  {worker_prefix} [green]✅ {bug.id}[/green] "
                            f"[dim]corrigé en {file_short}[/dim]"
                        )
                    else:
                        stats["failed"] += 1

                        # Marquer le bug comme échoué
                        bug.failed = True
                        bug.failed_at = datetime.now().isoformat()
                        bug.failure_reason = (
                            clean_output[:500] if clean_output else "Échec sans détails"
                        )
                        # Afficher la raison de l'échec (verbose)
                        if clean_output:
                            err_lines = [
                                ln for ln in clean_output.strip().split("\n") if ln.strip()
                            ]
                            for line in err_lines[-2:]:
                                if line.strip():
                                    self.console.print(f"    [dim red]│ {line[:80]}[/dim red]")

                        if on_bug_status:
                            on_bug_status(bug)

                        self.console.print(
                            f"  {worker_prefix} [red]❌ {bug.id}[/red] "
                            f"[dim]échec dans {file_short}[/dim]"
                        )

                    progress.update(main_task, completed=completed_count)

                bug_queue.task_done()

        # Lancer la session
        with progress:
            main_task = progress.add_task(
                "[bold]Correction en cours...[/bold]",
                total=len(bugs),
            )

            # Créer et lancer les workers
            workers = [
                asyncio.create_task(worker(i, main_task)) for i in range(effective_batch_size)
            ]

            # Attendre que tous les workers terminent
            await asyncio.gather(*workers)

        # Restaurer le handler original
        signal.signal(signal.SIGINT, original_handler)

        # Calculer les bugs restants si rate limited ou user stopped
        if stats["rate_limited"] or user_stopped:
            stats["remaining"] = bug_queue.qsize()
            if user_stopped:
                stats["user_stopped"] = True

        # Afficher le résumé
        self.console.print()

        if stats["rate_limited"]:
            # Afficher le message de rate limit
            wait_hours = stats["wait_hours"]
            if wait_hours >= 1:
                wait_display = f"{wait_hours:.1f} heures"
            else:
                wait_display = f"{int(wait_hours * 60)} minutes"

            self.console.print()
            self.console.print(
                Panel(
                    f"[bold red]⚠️  LIMITE D'USAGE CLAUDE CODE ATTEINTE[/bold red]\n\n"
                    f"[yellow]La limite d'utilisation de Claude Code a été atteinte.[/yellow]\n"
                    f"[cyan]Reprendre dans environ [bold]{wait_display}[/bold][/cyan]\n\n"
                    f"[dim]Bugs corrigés avant la limite: {stats['fixed']}/{stats['total']}[/dim]\n"
                    f"[dim]Bugs restants à traiter: {stats['remaining']}[/dim]\n\n"
                    f"[green]💡 Astuce: Relancez la commande plus tard pour continuer.[/green]",
                    title="🛑 Rate Limit",
                    border_style="red",
                )
            )
        elif stats["user_stopped"]:
            # Afficher le message d'arrêt utilisateur
            self.console.print()
            self.console.print(
                Panel(
                    f"[bold yellow]⏹️  SESSION ARRÊTÉE PAR L'UTILISATEUR[/bold yellow]\n\n"
                    f"[dim]Bugs corrigés: {stats['fixed']}/{stats['total']}[/dim]\n"
                    f"[dim]Bugs échoués: {stats['failed']}[/dim]\n"
                    f"[dim]Bugs restants: {stats['remaining']}[/dim]\n\n"
                    f"[green]💡 Relancez la commande pour continuer avec les bugs restants.[/green]",
                    title="⏹️ Arrêt manuel",
                    border_style="yellow",
                )
            )
        else:
            self.console.rule("[bold green]Résumé de la session parallèle")
            self.console.print(f"[green]✅ Corrigés:[/green] {stats['fixed']}")
            self.console.print(f"[yellow]⏭️  Passés:[/yellow] {stats['skipped']}")
            self.console.print(f"[red]❌ Échoués:[/red] {stats['failed']}")
            self.console.print(f"[dim]Total:[/dim] {stats['total']}")
            self.console.print(f"[dim]Batch size:[/dim] {effective_batch_size} workers")

        return stats

    def filter_bugs_by_severity(
        self, bugs: List[BugIdentifier], min_severity: str = "medium"
    ) -> List[BugIdentifier]:
        """
        Filtre les bugs par sévérité minimale.

        Args:
            bugs: Liste des bugs à filtrer
            min_severity: Sévérité minimale ('critical', 'high', 'medium', 'low')

        Returns:
            Liste des bugs avec sévérité >= min_severity
        """
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        min_level = severity_order.get(min_severity, 2)

        return [bug for bug in bugs if severity_order.get(bug.severity, 3) <= min_level]
