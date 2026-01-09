"""
Gestionnaire de priorités pour l'analyse de fichiers
Optimise les PR reviews en priorisant les fichiers modifiés
"""

from enum import Enum
from typing import Dict, List, Optional


class Priority(Enum):
    """Niveaux de priorité"""

    HIGH = "high"  # Fichiers modifiés dans PR
    MEDIUM = "medium"  # Dépendances directes des fichiers PR
    LOW = "low"  # Autres fichiers


class PriorityManager:
    """Gestionnaire de priorités pour les fichiers à analyser"""

    def __init__(
        self,
        pr_files: Optional[List[str]] = None,
        dependencies_map: Optional[Dict[str, List[str]]] = None,
    ):
        """
        Initialise le gestionnaire de priorités

        Args:
            pr_files: Liste des fichiers modifiés dans la PR (HIGH priority)
            dependencies_map: Map des fichiers vers leurs dépendances résolues
        """
        self.pr_files = set(pr_files) if pr_files else set()
        self.dependencies_map = dependencies_map or {}
        self._priority_cache: Dict[str, Priority] = {}

    def get_priority(self, file_path: str) -> Priority:
        """
        Détermine la priorité d'un fichier

        Args:
            file_path: Chemin du fichier

        Returns:
            Priorité du fichier
        """
        if file_path in self._priority_cache:
            return self._priority_cache[file_path]

        # HIGH: Fichiers modifiés dans PR
        if file_path in self.pr_files:
            priority = Priority.HIGH
        # MEDIUM: Dépendances directes des fichiers PR
        elif self._is_dependent_of_pr_file(file_path):
            priority = Priority.MEDIUM
        # LOW: Autres fichiers
        else:
            priority = Priority.LOW

        self._priority_cache[file_path] = priority
        return priority

    def _is_dependent_of_pr_file(self, file_path: str) -> bool:
        """
        Vérifie si un fichier est une dépendance directe d'un fichier PR

        Args:
            file_path: Chemin du fichier à vérifier

        Returns:
            True si le fichier est une dépendance directe d'un fichier PR
        """
        for pr_file, deps in self.dependencies_map.items():
            if pr_file in self.pr_files:
                if file_path in deps:
                    return True
        return False

    def sort_by_priority(self, files: List[str]) -> List[str]:
        """
        Trie les fichiers par priorité (HIGH → MEDIUM → LOW)

        Args:
            files: Liste des fichiers à trier

        Returns:
            Liste triée par priorité
        """
        priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}

        def priority_key(file_path: str) -> int:
            return priority_order[self.get_priority(file_path)]

        return sorted(files, key=priority_key)

    def group_by_priority(self, files: List[str]) -> Dict[Priority, List[str]]:
        """
        Groupe les fichiers par priorité

        Args:
            files: Liste des fichiers à grouper

        Returns:
            Dict groupant les fichiers par priorité
        """
        groups: Dict[Priority, List[str]] = {
            Priority.HIGH: [],
            Priority.MEDIUM: [],
            Priority.LOW: [],
        }

        for file_path in files:
            priority = self.get_priority(file_path)
            groups[priority].append(file_path)

        return groups

    def get_priority_stats(self, files: List[str]) -> Dict[str, int]:
        """
        Retourne des statistiques sur les priorités

        Args:
            files: Liste des fichiers

        Returns:
            Dict avec le nombre de fichiers par priorité
        """
        groups = self.group_by_priority(files)
        return {
            "high": len(groups[Priority.HIGH]),
            "medium": len(groups[Priority.MEDIUM]),
            "low": len(groups[Priority.LOW]),
        }
