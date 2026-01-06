"""
Agent d'Assurance Qualité - Synthétise toutes les informations d'analyse (QAA)
"""

import json
import os
from collections import defaultdict
from typing import List

from src.agents.base_agent import BaseAgent
from src.core.config import AnalysisConfig
from src.models.data_models import DependencyVulnerability
from src.models.data_models import FileAnalysis


class QualityAssuranceAgent(BaseAgent):
    """Agent d'Assurance Qualité - Synthétise toutes les informations d'analyse (QAA)"""

    def __init__(self, config: AnalysisConfig, doc_searcher=None, progress_manager=None):
        super().__init__(config, progress_manager)
        self.doc_searcher = doc_searcher

    async def generate_quality_report(
        self,
        analyses: List[FileAnalysis],
        architecture_report: str,
        dep_vulnerabilities: List[DependencyVulnerability],
        cycles: List[List[str]],
    ) -> str:
        """Génère un rapport d'assurance qualité synthétisant toutes les analyses"""
        try:
            # Compiler les statistiques globales
            total_files = len(analyses)
            successful_analyses = [a for a in analyses if a.success]
            failed_analyses = [a for a in analyses if not a.success]

            # Statistiques par catégorie
            security_issues_count = sum(len(a.security_issues) for a in successful_analyses)
            security_by_severity = defaultdict(int)
            for analysis in successful_analyses:
                for issue in analysis.security_issues:
                    security_by_severity[issue.severity] += 1

            # Métriques de code
            metrics_summary = {
                "total_loc": 0,
                "total_complexity": 0,
                "high_complexity_files": 0,
                "deep_nesting_files": 0,
                "duplicate_blocks": 0,
                "avg_maintainability": 0.0,
            }
            files_with_metrics = 0
            for analysis in successful_analyses:
                if analysis.code_metrics:
                    metrics = analysis.code_metrics
                    metrics_summary["total_loc"] += metrics.lines_of_code
                    metrics_summary["total_complexity"] += metrics.cyclomatic_complexity
                    if metrics.cyclomatic_complexity > 20:
                        metrics_summary["high_complexity_files"] += 1
                    if metrics.max_nesting_depth > 5:
                        metrics_summary["deep_nesting_files"] += 1
                    metrics_summary["duplicate_blocks"] += len(metrics.duplicate_code_blocks)
                    metrics_summary["avg_maintainability"] += metrics.maintainability_index
                    files_with_metrics += 1

            if files_with_metrics > 0:
                metrics_summary["avg_maintainability"] /= files_with_metrics

            # Dépendances
            total_dependencies = sum(len(a.dependencies) for a in successful_analyses)
            missing_dependencies = sum(
                sum(1 for d in a.dependencies if not d.exists) for a in successful_analyses
            )

            # Incohérences
            total_inconsistencies = sum(len(a.inconsistencies) for a in successful_analyses)

            # Vulnérabilités des dépendances
            vuln_by_severity = defaultdict(int)
            for vuln in dep_vulnerabilities:
                vuln_by_severity[vuln.severity] += 1

            # Préparer les échantillons de problèmes critiques
            critical_issues = []
            for analysis in successful_analyses:
                # Problèmes de sécurité critiques/high
                for issue in analysis.security_issues:
                    if issue.severity in ["critical", "high"]:
                        critical_issues.append(
                            {
                                "file": os.path.relpath(analysis.file_path, self.config.root_dir),
                                "type": "security",
                                "severity": issue.severity,
                                "description": issue.description,
                            }
                        )

                # Métriques problématiques
                if analysis.code_metrics:
                    if analysis.code_metrics.cyclomatic_complexity > 30:
                        critical_issues.append(
                            {
                                "file": os.path.relpath(analysis.file_path, self.config.root_dir),
                                "type": "complexity",
                                "severity": "high",
                                "description": f"Complexité cyclomatique très élevée: {analysis.code_metrics.cyclomatic_complexity}",
                            }
                        )

            # Recherche de documentation qualité si activé
            web_docs = ""
            if self.doc_searcher:
                try:
                    web_docs = await self.doc_searcher.search_documentation(
                        "Quality Assurance",
                        "quality_report",
                        "software quality assurance best practices",
                    )
                except Exception:
                    pass

            # Construire le prompt
            prompt = f"""Tu es un expert en Assurance Qualité Logicielle. Synthétise toutes les analyses effectuées et génère un rapport d'assurance qualité complet.

STATISTIQUES GLOBALES:
- Fichiers analysés: {total_files}
- Analyses réussies: {len(successful_analyses)}
- Analyses échouées: {len(failed_analyses)}

SÉCURITÉ:
- Total problèmes de sécurité: {security_issues_count}
- Répartition: {dict(security_by_severity)}
- Vulnérabilités dépendances: {len(dep_vulnerabilities)}
- Répartition vulnérabilités: {dict(vuln_by_severity)}

MÉTRIQUES DE CODE:
- Lignes de code totales: {metrics_summary['total_loc']}
- Complexité cyclomatique totale: {metrics_summary['total_complexity']}
- Fichiers avec complexité élevée (>20): {metrics_summary['high_complexity_files']}
- Fichiers avec imbrication profonde (>5): {metrics_summary['deep_nesting_files']}
- Blocs de code dupliqués: {metrics_summary['duplicate_blocks']}
- Indice de maintenabilité moyen: {metrics_summary['avg_maintainability']:.2f}/100

DÉPENDANCES:
- Total dépendances: {total_dependencies}
- Dépendances manquantes: {missing_dependencies}
- Cycles de dépendances: {len(cycles)}

INCOHÉRENCES:
- Total incohérences détectées: {total_inconsistencies}

PROBLÈMES CRITIQUES (échantillon):
{json.dumps(critical_issues[:20], indent=2, ensure_ascii=False)}

RAPPORT D'ARCHITECTURE:
{architecture_report[:5000]}

{web_docs}

Génère un rapport d'assurance qualité complet en Markdown avec les sections suivantes:

# Rapport d'Assurance Qualité

## Vue d'ensemble
Synthèse exécutive de l'état de la qualité du code avec score global et recommandations prioritaires.

## Score de Qualité Global
Fournis un score sur 100 avec justification basé sur:
- Sécurité (poids: 30%)
- Maintenabilité (poids: 25%)
- Architecture (poids: 20%)
- Métriques de code (poids: 15%)
- Dépendances (poids: 10%)

## Analyse par Dimension

### Sécurité
- État général de la sécurité
- Problèmes critiques identifiés
- Vulnérabilités des dépendances
- Recommandations prioritaires

### Maintenabilité
- Indice de maintenabilité global
- Complexité du code
- Code dupliqué
- Recommandations d'amélioration

### Architecture
- Points forts architecturaux
- Problèmes architecturaux identifiés
- Cycles de dépendances
- Recommandations de refactoring

### Métriques de Code
- Statistiques globales
- Fichiers problématiques
- Tendances et patterns
- Objectifs de qualité

### Dépendances
- État des dépendances
- Vulnérabilités connues
- Dépendances manquantes
- Recommandations de mise à jour

## Plan d'Action Priorisé
Liste des actions à entreprendre par ordre de priorité avec estimation d'effort.

## Roadmap d'Amélioration
Plan à court, moyen et long terme pour améliorer la qualité globale.

Sois précis, actionnable et basé sur les données réelles. Focus sur les priorités et les actions concrètes."""

            # Appel à Gemini (utilise la méthode de BaseAgent avec timeout_multiplier=3.0)
            response_text = await self._call_gemini_with_retry(prompt, timeout_multiplier=3.0)
            return response_text

        except Exception as e:
            return f"""# Rapport d'Assurance Qualité

## Erreur lors de la génération

Une erreur s'est produite lors de la génération du rapport d'assurance qualité:

```
{str(e)}
```

Nombre de fichiers analysés: {len(analyses)}
"""
