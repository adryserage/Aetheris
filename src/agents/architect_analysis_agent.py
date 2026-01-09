"""
Agent d'analyse architecturale (AAA)
"""

import json
import os
from typing import Dict, List, Optional

from src.agents.base_agent import BaseAgent
from src.core.config import AnalysisConfig
from src.models.data_models import FileAnalysis


class ArchitectAnalysisAgent(BaseAgent):
    """Agent d'analyse architecturale (AAA)"""

    def __init__(self, config: AnalysisConfig, doc_searcher=None, progress_manager=None):
        super().__init__(config, progress_manager)
        self.doc_searcher = doc_searcher

    async def generate_architecture_report(
        self, analyses: List[FileAnalysis], cycles: Optional[List[List[str]]] = None
    ) -> str:
        """Génère le rapport d'architecture global"""
        try:
            if cycles is None:
                cycles = []

            # Préparer les synthèses
            summaries = []
            all_inconsistencies = []
            dependency_stats = {
                "total_dependencies": 0,
                "missing_dependencies": 0,
                "files_with_dependencies": 0,
            }

            for analysis in analyses:
                if analysis.success:
                    summaries.append(
                        {
                            "file": os.path.relpath(analysis.file_path, self.config.root_dir),
                            "language": analysis.language,
                            "objective": analysis.objective,
                            "strengths": analysis.strengths,
                            "risks": analysis.risks,
                            "suggestions": analysis.suggestions,
                            "dependencies_count": len(analysis.dependencies),
                            "inconsistencies": analysis.inconsistencies,
                        }
                    )

                    # Compiler les statistiques de dépendances
                    if analysis.dependencies:
                        dependency_stats["files_with_dependencies"] += 1
                        dependency_stats["total_dependencies"] += len(analysis.dependencies)
                        dependency_stats["missing_dependencies"] += sum(
                            1 for d in analysis.dependencies if not d.exists
                        )

                    # Compiler les incohérences
                    if analysis.inconsistencies:
                        all_inconsistencies.extend(analysis.inconsistencies)

            # Grouper par langage et module
            by_language: Dict[str, List[Dict[str, object]]] = {}
            by_module: Dict[str, List[Dict[str, object]]] = {}

            for summary in summaries:
                lang = str(summary["language"])
                if lang not in by_language:
                    by_language[lang] = []
                by_language[lang].append(summary)

                # Extraire le module (dossier parent)
                file_path = str(summary["file"])
                module = (
                    "/".join(file_path.split("/")[:2])
                    if "/" in file_path
                    else file_path.split("/")[0]
                )
                if module not in by_module:
                    by_module[module] = []
                by_module[module].append(summary)

            # Préparer les informations sur les cycles
            cycles_info = ""
            if cycles:
                cycles_paths = []
                for cycle in cycles:
                    cycles_paths.append(
                        [os.path.relpath(f, self.config.root_dir).replace("\\", "/") for f in cycle]
                    )
                cycles_info = f"""

⚠️ CYCLES DE DÉPENDANCES DÉTECTÉS ({len(cycles)}):
{json.dumps(cycles_paths, indent=2, ensure_ascii=False)}
"""

            # Rechercher de la documentation architecturale si activé
            web_docs = ""
            if self.doc_searcher:
                try:
                    # Rechercher des documentations sur les patterns architecturaux utilisés
                    languages_used = list(by_language.keys())
                    search_content = f"Architecture patterns for {', '.join(languages_used)}"
                    web_docs = await self.doc_searcher.search_documentation(
                        languages_used[0] if languages_used else "Unknown",
                        "architecture",
                        search_content,
                    )
                except Exception as e:
                    print(f"⚠️  Erreur lors de la recherche de documentation architecturale: {e}")

            # Construire le prompt
            prompt = f"""Tu es un Architecte Logiciel Expert. Analyse l'ensemble des synthèses de code et génère un rapport d'architecture complet.

Nombre total de fichiers analysés: {len(summaries)}

Répartition par langage:
{json.dumps({k: len(v) for k, v in by_language.items()}, indent=2, ensure_ascii=False)}

Répartition par module:
{json.dumps({k: len(v) for k, v in by_module.items()}, indent=2, ensure_ascii=False)}

Statistiques des dépendances:
- Fichiers avec dépendances: {dependency_stats['files_with_dependencies']}
- Total des dépendances: {dependency_stats['total_dependencies']}
- Dépendances manquantes: {dependency_stats['missing_dependencies']}
- Incohérences détectées: {len(all_inconsistencies)}
{cycles_info}

Synthèses des fichiers (échantillon représentatif):
{json.dumps(summaries[:50], indent=2, ensure_ascii=False)}

Incohérences détectées (échantillon):
{json.dumps(all_inconsistencies[:20], indent=2, ensure_ascii=False)}
{web_docs}

Génère un rapport d'architecture complet en Markdown avec les sections suivantes:

# Vue d'ensemble de l'architecture

## Table des matières
- Architecture et patterns identifiés
- Cohérence inter-modules
- Redondances et dépendances
- Recommandations d'optimisation
- Plan de refactoring
- Gouvernance du code

## Architecture et patterns identifiés
Analyse les patterns architecturaux utilisés, les choix de design, et la structure globale.

## Cohérence inter-modules
Évalue la cohérence entre les différents modules, la communication inter-modules, et les interfaces.

## Redondances, dépendances ou couplages excessifs
Identifie les redondances de code, les dépendances circulaires (cycles détectés ci-dessus), les couplages forts, et les problèmes d'architecture. Analyse spécifiquement les cycles de dépendances détectés et propose des solutions pour les résoudre.

## Recommandations d'optimisation
Propose des optimisations architecturales, de performance, et de maintenabilité.

## Plan de refactoring
Suggère un plan de refactoring priorisé avec les étapes concrètes.

## Gouvernance du code
Recommandations pour améliorer la gouvernance, les standards, et la qualité du code.

Sois précis, structuré et actionnable. Focus sur l'architecture globale et les améliorations systémiques.
Si une documentation en ligne est fournie ci-dessus, utilise-la pour enrichir tes recommandations avec les meilleures pratiques actuelles et les patterns architecturaux modernes."""

            # Appel à Gemini (utilise la méthode de BaseAgent avec timeout_multiplier=2.0)
            response_text = await self._call_gemini_with_retry(prompt, timeout_multiplier=2.0)
            return response_text

        except Exception as e:
            return f"""# Vue d'ensemble de l'architecture

## Erreur lors de la génération

Une erreur s'est produite lors de la génération du rapport d'architecture:

```
{str(e)}
```

Nombre de fichiers analysés: {len(analyses)}
"""
