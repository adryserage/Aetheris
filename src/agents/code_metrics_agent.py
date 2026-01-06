"""
Agent d'analyse de métriques de code (CMA)
"""

import re
from typing import List
from typing import Tuple

from src.core.config import AnalysisConfig
from src.models.data_models import CodeMetrics


class CodeMetricsAgent:
    """Agent d'analyse de métriques de code (CMA)"""

    def __init__(self, config: AnalysisConfig):
        self.config = config

    def _count_lines(self, content: str, language: str) -> int:
        """Compte les lignes de code (exclut les lignes vides et commentaires)"""
        lines = content.split("\n")
        code_lines = 0
        in_multiline_comment = False

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            # Gérer les commentaires multi-lignes
            if "/*" in stripped or (language == "Python" and '"""' in stripped):
                in_multiline_comment = True
            if "*/" in stripped or (
                language == "Python" and '"""' in stripped and stripped.count('"""') >= 2
            ):
                in_multiline_comment = False
                continue

            if in_multiline_comment:
                continue

            # Ignorer les commentaires simples
            if stripped.startswith("//") or stripped.startswith("#") or stripped.startswith("*"):
                continue

            code_lines += 1

        return code_lines

    def _calculate_cyclomatic_complexity(self, content: str, language: str) -> int:
        """Calcule la complexité cyclomatique"""
        complexity = 1  # Base complexity

        # Patterns qui augmentent la complexité
        complexity_patterns = [
            r"\bif\s*\(",
            r"\belse\s*\{",
            r"\bwhile\s*\(",
            r"\bfor\s*\(",
            r"\bswitch\s*\(",
            r"\bcase\s+",
            r"\bcatch\s*\(",
            r"\?\s*.*\s*:",
            r"\b&&\b",
            r"\b\|\|\b",
            r"\band\b",
            r"\bor\b",
        ]

        for pattern in complexity_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            complexity += len(matches)

        return complexity

    def _calculate_nesting_depth(self, content: str) -> int:
        """Calcule la profondeur d'imbrication maximale"""
        max_depth = 0
        current_depth = 0

        for line in content.split("\n"):
            # Compter les ouvertures de blocs
            current_depth += line.count("{") - line.count("}")
            max_depth = max(max_depth, current_depth)

        return max_depth

    def _count_functions(self, content: str, language: str) -> int:
        """Compte le nombre de fonctions/méthodes"""
        if language in ["TypeScript", "TypeScript (React)", "JavaScript", "JavaScript (React)"]:
            patterns = [
                r"\bfunction\s+\w+\s*\(",
                r"const\s+\w+\s*=\s*(?:async\s+)?\([^)]*\)\s*=>",
                r"\w+\s*:\s*(?:async\s+)?\([^)]*\)\s*=>",
            ]
        elif language == "Dart":
            patterns = [
                r"\w+\s+\w+\s*\([^)]*\)\s*\{",
            ]
        elif language == "Python":
            patterns = [
                r"\bdef\s+\w+\s*\(",
                r"\basync\s+def\s+\w+\s*\(",
            ]
        else:
            patterns = [r"\bfunction\s+\w+\s*\("]

        count = 0
        for pattern in patterns:
            matches = re.findall(pattern, content)
            count += len(matches)

        return count

    def _detect_duplicate_code(self, content: str, min_lines: int = 5) -> List[Tuple[int, int]]:
        """Détecte les blocs de code dupliqués (simplifié)"""
        # Version simplifiée - en production, utiliser un outil dédié
        lines = content.split("\n")
        duplicates = []

        # Chercher des séquences répétées
        for i in range(len(lines) - min_lines):
            sequence = "\n".join(lines[i : i + min_lines])
            # Chercher cette séquence ailleurs dans le fichier
            for j in range(i + min_lines, len(lines) - min_lines):
                other_sequence = "\n".join(lines[j : j + min_lines])
                if sequence.strip() == other_sequence.strip() and sequence.strip():
                    duplicates.append((i + 1, i + min_lines))
                    break

        return duplicates

    def calculate_metrics(self, file_path: str, content: str, language: str) -> CodeMetrics:
        """Calcule les métriques de code pour un fichier"""
        if not content.strip():
            return CodeMetrics(
                file_path=file_path,
                language=language,
                lines_of_code=0,
                cyclomatic_complexity=0,
                max_nesting_depth=0,
                function_count=0,
                average_function_length=0.0,
            )

        lines_of_code = self._count_lines(content, language)
        cyclomatic_complexity = self._calculate_cyclomatic_complexity(content, language)
        max_nesting_depth = self._calculate_nesting_depth(content)
        function_count = self._count_functions(content, language)

        # Calculer la longueur moyenne des fonctions (approximation)
        avg_function_length = lines_of_code / function_count if function_count > 0 else 0

        # Détecter les duplications
        duplicate_blocks = self._detect_duplicate_code(content)

        # Calculer l'indice de maintenabilité (formule simplifiée)
        # MI = 171 - 5.2 * ln(Halstead Volume) - 0.23 * (Cyclomatic Complexity) - 16.2 * ln(Lines of Code)
        # Version simplifiée:
        maintainability_index = max(
            0, min(100, 171 - 0.23 * cyclomatic_complexity - 16.2 * (lines_of_code / 100))
        )

        return CodeMetrics(
            file_path=file_path,
            language=language,
            lines_of_code=lines_of_code,
            cyclomatic_complexity=cyclomatic_complexity,
            max_nesting_depth=max_nesting_depth,
            function_count=function_count,
            average_function_length=avg_function_length,
            duplicate_code_blocks=duplicate_blocks,
            maintainability_index=maintainability_index,
        )
