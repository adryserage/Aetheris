"""
Claude Code Integration - Intégration avec Claude Code CLI pour la correction de bugs
Exécute Claude Code directement en arrière-plan pour corriger les bugs
"""

import os
import platform
import shutil
import subprocess
import tempfile
from typing import Optional, List, Tuple

from rich.console import Console
from rich.prompt import Confirm
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.models.data_models import BugIdentifier


class ClaudeCodeIntegration:
    """Intégration avec Claude Code CLI pour la correction automatique de bugs"""

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
            result = subprocess.run(
                [self._claude_path or "claude", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                version = result.stdout.strip() or result.stderr.strip()
                return True, f"Claude Code OK: {version}"
            else:
                return False, f"Erreur: {result.stderr}"
        except subprocess.TimeoutExpired:
            return False, "Timeout lors du test"
        except Exception as e:
            return False, f"Erreur: {e}"

    def run_claude_direct(
        self, prompt: str, timeout: int = 300
    ) -> Tuple[bool, str, str]:
        """
        Exécute Claude Code directement en arrière-plan (sans terminal).

        Args:
            prompt: Le prompt à envoyer
            timeout: Timeout en secondes (défaut: 5 minutes)

        Returns:
            Tuple (success, stdout, stderr)
        """
        if not self.is_available:
            return False, "", "Claude Code n'est pas installé"

        try:
            # Écrire le prompt dans un fichier temporaire pour éviter les problèmes d'échappement
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".txt", delete=False, encoding="utf-8"
            ) as f:
                f.write(prompt)
                prompt_file = f.name

            try:
                # Lire le prompt depuis le fichier
                cmd = [
                    self._claude_path or "claude",
                    "--dangerously-skip-permissions",
                    "-p",
                    prompt,
                ]

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=self.root_dir,
                    env={**os.environ, "FORCE_COLOR": "0"},  # Désactiver les couleurs ANSI
                )

                return result.returncode == 0, result.stdout, result.stderr

            finally:
                # Nettoyer le fichier temporaire
                try:
                    os.unlink(prompt_file)
                except:
                    pass

        except subprocess.TimeoutExpired:
            return False, "", f"Timeout après {timeout}s"
        except Exception as e:
            return False, "", f"Erreur: {e}"

    def fix_bug_direct(self, bug: BugIdentifier, timeout: int = 300) -> Tuple[bool, str]:
        """
        Corrige un bug directement via Claude Code (sans fenêtre terminal).

        Args:
            bug: Le bug à corriger
            timeout: Timeout en secondes

        Returns:
            Tuple (success, output)
        """
        prompt = self._generate_fix_prompt(bug)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task(
                f"🔧 Correction de {bug.id}...", total=None
            )
            success, stdout, stderr = self.run_claude_direct(prompt, timeout)

        if success:
            return True, stdout
        else:
            return False, stderr or stdout

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
            applescript = f'''
            tell application "Terminal"
                activate
                do script "{claude_cmd} --dangerously-skip-permissions -p \\"{escaped_prompt}\\""
            end tell
            '''
            return ["osascript", "-e", applescript]

        else:  # Linux
            # Linux: détecter le terminal disponible
            terminals = [
                ("gnome-terminal", ["gnome-terminal", "--", claude_cmd, "--dangerously-skip-permissions", "-p", prompt]),
                ("konsole", ["konsole", "-e", claude_cmd, "--dangerously-skip-permissions", "-p", prompt]),
                ("xfce4-terminal", ["xfce4-terminal", "-e", f'{claude_cmd} --dangerously-skip-permissions -p "{escaped_prompt}"']),
                ("xterm", ["xterm", "-e", claude_cmd, "--dangerously-skip-permissions", "-p", prompt]),
                ("terminator", ["terminator", "-e", f'{claude_cmd} --dangerously-skip-permissions -p "{escaped_prompt}"']),
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
            self.console.print(
                "[red]❌ Impossible de détecter un terminal compatible[/red]"
            )
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
        self.console.print(
            "[cyan]💡 Claude Code a été lancé dans une nouvelle fenêtre.[/cyan]"
        )
        self.console.print(
            "[cyan]   Corrigez le bug, puis revenez ici pour confirmer.[/cyan]"
        )
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
                f"[bold]Description:[/bold]",
                f"  {bug.description}",
            ]
        )

        if bug.recommendation:
            content.extend(
                [
                    "",
                    f"[bold]Recommandation:[/bold]",
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

    def display_bugs_table(self, bugs: List[BugIdentifier]):
        """
        Affiche un tableau récapitulatif des bugs.

        Args:
            bugs: Liste des bugs à afficher
        """
        table = Table(title="🐛 Bugs détectés", show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Fichier", style="dim")
        table.add_column("Ligne", justify="right")
        table.add_column("Type", style="blue")
        table.add_column("Sévérité")
        table.add_column("Description", max_width=40)

        severity_colors = {
            "critical": "red bold",
            "high": "red",
            "medium": "yellow",
            "low": "green",
        }

        for bug in bugs:
            severity_color = severity_colors.get(bug.severity, "white")
            # Tronquer la description si trop longue
            desc = bug.description[:37] + "..." if len(bug.description) > 40 else bug.description

            table.add_row(
                bug.id,
                bug.file_path,
                str(bug.line_number) if bug.line_number else "-",
                bug.bug_type,
                f"[{severity_color}]{bug.severity}[/{severity_color}]",
                desc,
            )

        self.console.print(table)

    def run_fix_session(
        self,
        bugs: List[BugIdentifier],
        auto_mode: bool = False,
        direct_mode: bool = True,
    ) -> dict:
        """
        Exécute une session de correction de bugs.

        Args:
            bugs: Liste des bugs à corriger
            auto_mode: Si True, ne demande pas de confirmation entre les bugs
            direct_mode: Si True, exécute Claude Code en arrière-plan (sans fenêtre terminal)

        Returns:
            Statistiques de la session (fixed, skipped, failed)
        """
        stats = {"fixed": 0, "skipped": 0, "failed": 0, "total": len(bugs)}

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

        mode_msg = "en arrière-plan" if direct_mode else "dans une nouvelle fenêtre"
        self.console.print(f"[dim]Mode: Claude Code sera exécuté {mode_msg}[/dim]")
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
            self.console.print()
            self.console.rule(f"[bold blue]Bug {i}/{len(bugs)}")
            self._display_bug_details(bug)

            if direct_mode:
                # Mode direct: exécuter en arrière-plan
                success, output = self.fix_bug_direct(bug)
                if success:
                    stats["fixed"] += 1
                    self.console.print(f"[green]✅ {bug.id} corrigé[/green]")
                    if output:
                        # Afficher un résumé de la sortie
                        lines = output.strip().split("\n")
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
                    if output:
                        self.console.print(f"[red]{output[:500]}[/red]")

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

        # Afficher le résumé
        self.console.print()
        self.console.rule("[bold green]Résumé de la session")
        self.console.print(f"[green]✅ Corrigés:[/green] {stats['fixed']}")
        self.console.print(f"[yellow]⏭️  Passés:[/yellow] {stats['skipped']}")
        self.console.print(f"[red]❌ Échoués:[/red] {stats['failed']}")
        self.console.print(f"[dim]Total:[/dim] {stats['total']}")

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

        return [
            bug
            for bug in bugs
            if severity_order.get(bug.severity, 3) <= min_level
        ]
