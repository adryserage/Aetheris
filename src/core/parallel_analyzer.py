"""
Module de parallélisation intelligente pour l'analyse de fichiers
Analyse les fichiers indépendants en parallèle en utilisant le graphe de dépendances
"""

from collections import deque
from typing import Dict
from typing import List
from typing import Set
from typing import Tuple


def build_dependency_graph(
    files: List[str], dependencies_map: Dict[str, List[str]]
) -> Dict[str, Set[str]]:
    """
    Construit un graphe de dépendances entre fichiers

    Args:
        files: Liste des fichiers à analyser
        dependencies_map: Map des fichiers vers leurs dépendances (chemins résolus)

    Returns:
        Graphe de dépendances: {file_path: set(dependencies)}
    """
    graph = {file: set() for file in files}

    for file_path, deps in dependencies_map.items():
        if file_path in graph:
            # Ajouter seulement les dépendances qui sont dans la liste des fichiers à analyser
            for dep in deps:
                if dep in graph:
                    graph[file_path].add(dep)

    return graph


def topological_sort(graph: Dict[str, Set[str]]) -> List[List[str]]:
    """
    Effectue un tri topologique du graphe pour déterminer l'ordre d'analyse

    Args:
        graph: Graphe de dépendances

    Returns:
        Liste de niveaux, chaque niveau contient les fichiers qui peuvent être analysés en parallèle
    """
    # Calculer les degrés entrants
    in_degree = {node: 0 for node in graph}
    for node in graph:
        for dep in graph[node]:
            if dep in in_degree:
                in_degree[dep] += 1

    # Trouver les fichiers sans dépendances (niveau 0)
    queue = deque([node for node in graph if in_degree[node] == 0])
    levels = []

    while queue:
        # Tous les fichiers dans la queue peuvent être analysés en parallèle
        current_level = list(queue)
        levels.append(current_level)
        queue.clear()

        # Mettre à jour les degrés entrants
        for node in current_level:
            for dep in graph[node]:
                if dep in in_degree:
                    in_degree[dep] -= 1
                    if in_degree[dep] == 0:
                        queue.append(dep)

    # Gérer les cycles (fichiers restants)
    remaining = [node for node in graph if in_degree[node] > 0]
    if remaining:
        # Les fichiers restants forment probablement un cycle
        # On les ajoute au dernier niveau
        if levels:
            levels[-1].extend(remaining)
        else:
            levels.append(remaining)

    return levels


def detect_independent_files(
    files: List[str], dependencies_map: Dict[str, List[str]]
) -> List[List[str]]:
    """
    Détecte les fichiers indépendants et les groupe par niveau pour parallélisation

    Args:
        files: Liste des fichiers à analyser
        dependencies_map: Map des fichiers vers leurs dépendances (chemins résolus)

    Returns:
        Liste de niveaux, chaque niveau contient les fichiers qui peuvent être analysés en parallèle
    """
    if not files:
        return []

    # Construire le graphe de dépendances
    graph = build_dependency_graph(files, dependencies_map)

    # Effectuer un tri topologique
    levels = topological_sort(graph)

    return levels


def group_files_by_dependency_level(
    files: List[str], dependencies_map: Dict[str, List[str]]
) -> Tuple[List[List[str]], Dict[str, int]]:
    """
    Groupe les fichiers par niveau de dépendance et retourne aussi un map de priorité

    Args:
        files: Liste des fichiers à analyser
        dependencies_map: Map des fichiers vers leurs dépendances

    Returns:
        Tuple (niveaux, priorité_map) où:
        - niveaux: Liste de niveaux pour parallélisation
        - priorité_map: Map file_path -> niveau (0 = indépendant, plus élevé = plus de dépendances)
    """
    levels = detect_independent_files(files, dependencies_map)
    priority_map = {}

    for level_idx, level_files in enumerate(levels):
        for file in level_files:
            priority_map[file] = level_idx

    return levels, priority_map


def get_parallelizable_batches(
    files: List[str],
    dependencies_map: Dict[str, List[str]],
    batch_size: int,
) -> List[List[str]]:
    """
    Crée des batches optimisés pour la parallélisation en respectant les dépendances

    Args:
        files: Liste des fichiers à analyser
        dependencies_map: Map des fichiers vers leurs dépendances
        batch_size: Taille maximale d'un batch

    Returns:
        Liste de batches, chaque batch peut être analysé en parallèle
    """
    levels, _ = group_files_by_dependency_level(files, dependencies_map)

    batches = []
    for level in levels:
        # Diviser chaque niveau en batches de taille batch_size
        for i in range(0, len(level), batch_size):
            batch = level[i : i + batch_size]
            batches.append(batch)

    return batches
