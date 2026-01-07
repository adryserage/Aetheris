"""
Gestionnaire de progression avec Rich pour afficher des barres de progression modernes
"""

import os
import sys
from contextlib import contextmanager
from typing import Optional

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import BarColumn
    from rich.progress import Progress
    from rich.progress import SpinnerColumn
    from rich.progress import TaskID
    from rich.progress import TextColumn
    from rich.progress import TimeElapsedColumn
    from rich.progress import TimeRemainingColumn

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class ProgressManager:
    """Gestionnaire de progression utilisant Rich pour afficher des barres de progression"""

    def __init__(self, enabled: bool = True):
        """
        Initialise le gestionnaire de progression

        Args:
            enabled: Si False, désactive l'affichage Rich (utilise les logs simples)
        """
        self.enabled = enabled and RICH_AVAILABLE and self._is_interactive_terminal()
        self.console = Console() if self.enabled else None
        self.progress: Optional[Progress] = None
        self.tasks: dict = {}

    def _is_interactive_terminal(self) -> bool:
        """Vérifie si on est dans un terminal interactif"""
        return (
            sys.stdout.isatty() and hasattr(sys.stdout, "fileno") and os.isatty(sys.stdout.fileno())
        )

    @contextmanager
    def create_progress(self):
        """Context manager pour créer et gérer une instance Progress"""
        if not self.enabled:
            yield None
            return

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=self.console,
            expand=True,
            refresh_per_second=4,  # Limiter le rafraîchissement pour éviter les duplications
            transient=False,  # Garder les barres de progression visibles
        ) as progress:
            self.progress = progress
            yield progress
            self.progress = None

    def add_task(
        self, description: str, total: int = 100, task_id: Optional[TaskID] = None
    ) -> TaskID:
        """
        Ajoute une nouvelle tâche à la barre de progression

        Args:
            description: Description de la tâche
            total: Nombre total d'éléments à traiter
            task_id: ID de la tâche (optionnel, généré automatiquement si non fourni)

        Returns:
            L'ID de la tâche créée
        """
        if not self.enabled or not self.progress:
            return None

        task_id = self.progress.add_task(description, total=total)
        self.tasks[description] = task_id
        return task_id

    def update_task(
        self,
        task_id: TaskID,
        advance: int = 1,
        description: Optional[str] = None,
        total: Optional[int] = None,
    ):
        """
        Met à jour une tâche de progression

        Args:
            task_id: ID de la tâche
            advance: Nombre d'éléments à avancer
            description: Nouvelle description (optionnel)
            total: Nouveau total (optionnel)
        """
        if not self.enabled or not self.progress:
            return

        self.progress.update(task_id, advance=advance, description=description, total=total)

    def complete_task(self, task_id: TaskID):
        """
        Marque une tâche comme complétée

        Args:
            task_id: ID de la tâche
        """
        if not self.enabled or not self.progress:
            return

        self.progress.update(task_id, completed=self.progress.tasks[task_id].total)

    def print(self, *args, **kwargs):
        """
        Affiche un message (compatible avec log_print)

        Args:
            *args: Arguments à afficher
            **kwargs: Options d'affichage
        """
        if self.enabled and self.console:
            # Utiliser console.log pour une meilleure intégration avec les barres de progression
            # Cela évite les problèmes de duplication
            self.console.print(*args, **kwargs)
        else:
            # Fallback vers print standard avec flush pour garantir la visibilité
            kwargs.setdefault("flush", True)
            print(*args, **kwargs)

    def print_panel(self, content: str, title: str = "", style: str = "blue"):
        """
        Affiche un panneau Rich avec du contenu

        Args:
            content: Contenu du panneau
            title: Titre du panneau
            style: Style du panneau
        """
        if not self.enabled or not self.console:
            print(f"{title}: {content}")
            return

        panel = Panel(content, title=title, style=style)
        self.console.print(panel)

    def print_reasoning(self, reasoning_text: str, model_name: str = ""):
        """
        Affiche le reasoning du modèle dans un panneau dédié

        Args:
            reasoning_text: Texte du reasoning
            model_name: Nom du modèle (optionnel)
        """
        if not self.enabled or not self.console:
            print(f"🤔 Reasoning ({model_name}):\n{reasoning_text}")
            return

        title = f"🤔 Reasoning {model_name}" if model_name else "🤔 Reasoning"
        panel = Panel(
            reasoning_text,
            title=title,
            style="cyan",
            border_style="cyan",
        )
        self.console.print(panel)
