"""
Impact Analyzer - Analyse l'impact des bugs à travers le codebase via le graphe de dépendances
"""

import hashlib
from typing import List, Dict, Optional

from src.models.data_models import (
    BugIdentifier,
    ImpactAnalysis,
    FileAnalysis,
)
from src.services.dependency_analyzer import DependencyAnalyzer


class ImpactAnalyzer:
    """Analyse l'impact des bugs à travers le codebase via les dépendances"""

    def __init__(self, dependency_analyzer: DependencyAnalyzer, max_impact_depth: int = 3):
        """
        Args:
            dependency_analyzer: Analyseur de dépendances avec graphe inverse construit
            max_impact_depth: Profondeur maximale pour l'analyse d'impact
        """
        self.dependency_analyzer = dependency_analyzer
        self.max_impact_depth = max_impact_depth
        self.bugs_registry: Dict[str, BugIdentifier] = {}

    def generate_bug_id(
        self,
        file_path: str,
        line_number: Optional[int],
        bug_type: str,
        description: str,
    ) -> str:
        """
        Génère un ID unique et déterministe pour un bug.

        Args:
            file_path: Chemin du fichier
            line_number: Numéro de ligne (optionnel)
            bug_type: Type de bug
            description: Description du bug

        Returns:
            ID unique au format "BUG-XXXXXXXX"
        """
        content = f"{file_path}:{line_number}:{bug_type}:{description[:50]}"
        hash_value = hashlib.sha256(content.encode()).hexdigest()[:8]
        return f"BUG-{hash_value.upper()}"

    def extract_bugs_from_analysis(self, analysis: FileAnalysis) -> List[BugIdentifier]:
        """
        Extrait tous les bugs d'une FileAnalysis et leur assigne des IDs uniques.

        Args:
            analysis: Résultat d'analyse d'un fichier

        Returns:
            Liste des bugs identifiés
        """
        bugs = []

        # Extraire depuis les problèmes de sécurité
        for issue in analysis.security_issues:
            bug = BugIdentifier(
                id=self.generate_bug_id(
                    analysis.file_path, issue.line_number, "security", issue.description
                ),
                file_path=analysis.file_path,
                line_number=issue.line_number,
                bug_type="security",
                severity=issue.severity,
                description=issue.description,
                recommendation=issue.recommendation,
                impacted_files=[],
            )
            bugs.append(bug)
            self.bugs_registry[bug.id] = bug

        # Extraire depuis les risques
        for risk in analysis.risks:
            # Parser la sévérité depuis le texte du risque
            severity = self._parse_severity_from_text(risk)

            bug = BugIdentifier(
                id=self.generate_bug_id(analysis.file_path, None, "risk", risk),
                file_path=analysis.file_path,
                line_number=None,
                bug_type="risk",
                severity=severity,
                description=risk,
                recommendation="",
                impacted_files=[],
            )
            bugs.append(bug)
            self.bugs_registry[bug.id] = bug

        # Extraire depuis les incohérences
        for inc in analysis.inconsistencies:
            bug = BugIdentifier(
                id=self.generate_bug_id(analysis.file_path, None, "inconsistency", inc),
                file_path=analysis.file_path,
                line_number=None,
                bug_type="inconsistency",
                severity="medium",
                description=inc,
                recommendation="Vérifier et corriger l'incohérence",
                impacted_files=[],
            )
            bugs.append(bug)
            self.bugs_registry[bug.id] = bug

        return bugs

    def _parse_severity_from_text(self, text: str) -> str:
        """Parse la sévérité depuis le texte d'un risque."""
        text_lower = text.lower()
        if "critical" in text_lower or "critique" in text_lower:
            return "critical"
        elif "high" in text_lower or "haute" in text_lower or "élevé" in text_lower:
            return "high"
        elif "low" in text_lower or "basse" in text_lower or "faible" in text_lower:
            return "low"
        return "medium"

    def analyze_bug_impact(self, bug: BugIdentifier) -> ImpactAnalysis:
        """
        Analyse l'impact d'un bug sur le codebase.
        Utilise le graphe de dépendances inverse pour trouver les fichiers affectés.

        Args:
            bug: Le bug à analyser

        Returns:
            Analyse d'impact avec fichiers directement et transitivement impactés
        """
        dependents = self.dependency_analyzer.get_dependents(
            bug.file_path, self.max_impact_depth
        )

        directly_impacted = dependents.get(1, [])
        transitively_impacted = []

        for depth in range(2, self.max_impact_depth + 1):
            if depth in dependents:
                transitively_impacted.extend(dependents[depth])

        # Mettre à jour les fichiers impactés du bug
        bug.impacted_files = directly_impacted + transitively_impacted

        # Construire les chaînes d'impact (simplifié)
        impact_chains = []
        for file in directly_impacted:
            impact_chains.append([bug.file_path, file])

        return ImpactAnalysis(
            bug_id=bug.id,
            source_file=bug.file_path,
            directly_impacted=directly_impacted,
            transitively_impacted=transitively_impacted,
            impact_chain=impact_chains,
        )

    def generate_impact_report(
        self, analyses: List[FileAnalysis]
    ) -> Dict[str, List[ImpactAnalysis]]:
        """
        Génère un rapport d'impact pour tous les bugs de toutes les analyses.

        Args:
            analyses: Liste des analyses de fichiers

        Returns:
            Dict mappant la sévérité vers la liste des analyses d'impact
        """
        all_bugs: List[BugIdentifier] = []

        # Extraire tous les bugs
        for analysis in analyses:
            bugs = self.extract_bugs_from_analysis(analysis)
            analysis.bugs = bugs
            all_bugs.extend(bugs)

        # Analyser l'impact de chaque bug
        impact_by_severity: Dict[str, List[ImpactAnalysis]] = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
        }

        for bug in all_bugs:
            impact = self.analyze_bug_impact(bug)
            impact_by_severity[bug.severity].append(impact)

        return impact_by_severity

    def get_bugs_by_severity(self, min_severity: str = "medium") -> List[BugIdentifier]:
        """
        Retourne les bugs filtrés par sévérité minimale.

        Args:
            min_severity: Sévérité minimale ('critical', 'high', 'medium', 'low')

        Returns:
            Liste des bugs avec sévérité >= min_severity
        """
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        min_level = severity_order.get(min_severity, 2)

        return [
            bug
            for bug in self.bugs_registry.values()
            if severity_order.get(bug.severity, 3) <= min_level
        ]

    def get_all_bugs(self) -> List[BugIdentifier]:
        """Retourne tous les bugs enregistrés."""
        return list(self.bugs_registry.values())

    def bugs_to_dict(self) -> List[Dict]:
        """
        Convertit tous les bugs en dictionnaires pour la sérialisation JSON.

        Returns:
            Liste de dictionnaires représentant les bugs
        """
        return [
            {
                "id": bug.id,
                "file_path": bug.file_path,
                "line_number": bug.line_number,
                "bug_type": bug.bug_type,
                "severity": bug.severity,
                "description": bug.description,
                "recommendation": bug.recommendation,
                "impacted_files": bug.impacted_files,
            }
            for bug in self.bugs_registry.values()
        ]
