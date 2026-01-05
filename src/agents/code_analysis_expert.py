"""
Agent d'analyse de code individuel (CAE)

Utilise les Structured Outputs de Gemini pour des analyses plus riches
et les capacités de Thinking pour un raisonnement approfondi.
"""

import os
import pathlib
import re
from typing import List, Optional

from src.agents.base_agent import BaseAgent
from src.core.config import AnalysisConfig
from src.models.analysis_schemas import FileAnalysisResult
from src.models.data_models import FileAnalysis


class CodeAnalysisExpert(BaseAgent):
    """Agent d'analyse de code individuel (CAE)"""

    def __init__(
        self,
        config: AnalysisConfig,
        dependency_analyzer=None,
        doc_searcher=None,
        code_generator=None,
        progress_manager=None,
    ):
        super().__init__(config, progress_manager)
        self.dependency_analyzer = dependency_analyzer
        self.doc_searcher = doc_searcher
        self.code_generator = code_generator

    def detect_language(self, file_path: str) -> str:
        """Détecte le langage du fichier basé sur l'extension"""
        ext = pathlib.Path(file_path).suffix.lower()
        lang_map = {
            ".dart": "Dart",
            ".ts": "TypeScript",
            ".tsx": "TypeScript (React)",
            ".js": "JavaScript",
            ".jsx": "JavaScript (React)",
            ".py": "Python",
            ".java": "Java",
            ".kt": "Kotlin",
            ".swift": "Swift",
            ".go": "Go",
            ".rs": "Rust",
            ".cpp": "C++",
            ".c": "C",
            ".h": "C/C++ Header",
            ".cs": "C#",
            ".php": "PHP",
            ".rb": "Ruby",
            ".sh": "Shell",
            ".yaml": "YAML",
            ".yml": "YAML",
            ".json": "JSON",
            ".xml": "XML",
            ".md": "Markdown",
            ".sql": "SQL",
            ".html": "HTML",
            ".css": "CSS",
            ".scss": "SCSS",
            ".sass": "SASS",
        }
        return lang_map.get(ext, "Unknown")

    async def analyze_file(self, file_path: str) -> FileAnalysis:
        """Analyse un fichier individuel avec Gemini"""
        try:
            # Lire le contenu du fichier
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            if not content.strip():
                language = self.detect_language(file_path)
                relative_path = os.path.relpath(file_path, self.config.root_dir)
                relative_path = relative_path.replace("\\", "/")

                # Générer une analyse conforme au template même pour les fichiers vides
                empty_analysis = f"""Voici l'analyse structurée du fichier `{relative_path}`.

# Analyse: {relative_path}

## Langage détecté

{language}

## Objectif / Fonction principale

Fichier vide. Vérifier si ce fichier est nécessaire ou s'il doit être supprimé.

## Points forts / Bonnes pratiques

Aucun point fort identifié pour un fichier vide.

## Risques, dettes techniques ou incohérences

- **Fichier vide :** Ce fichier ne contient aucun code. Il peut s'agir d'un fichier oublié, d'un placeholder non complété, ou d'un fichier à supprimer.

## Suggestions d'amélioration

1.  **Vérifier la nécessité du fichier :**
    Si le fichier n'est pas utilisé, le supprimer pour éviter la confusion.

2.  **Compléter le fichier si nécessaire :**
    Si le fichier doit contenir du code, l'implémenter selon les besoins du projet.
"""

                return FileAnalysis(
                    file_path=file_path,
                    language=language,
                    objective="Fichier vide",
                    strengths=[],
                    risks=["Fichier vide - vérifier si nécessaire"],
                    suggestions=[
                        "Vérifier la nécessité du fichier",
                        "Compléter le fichier si nécessaire",
                    ],
                    analysis_markdown=empty_analysis,
                    success=True,
                    dependencies=[],
                    inconsistencies=[],
                )

            language = self.detect_language(file_path)
            relative_path = os.path.relpath(file_path, self.config.root_dir)
            # Normaliser les séparateurs pour utiliser des slashes (comme dans le template)
            relative_path = relative_path.replace("\\", "/")

            # Extraire les dépendances si l'analyseur est disponible
            dependencies = []
            dependencies_info = ""
            inconsistencies = []

            if self.dependency_analyzer:
                dependencies = self.dependency_analyzer.extract_dependencies(
                    file_path, content, language
                )

                # Préparer les informations sur les dépendances
                if dependencies:
                    deps_list = []
                    missing_deps = []
                    for dep in dependencies:
                        if dep.exists and dep.resolved_path:
                            rel_dep_path = os.path.relpath(
                                dep.resolved_path, self.config.root_dir
                            ).replace("\\", "/")
                            deps_list.append(
                                f"  - Ligne {dep.line_number}: `{dep.import_path}` → `{rel_dep_path}` ✅"
                            )
                        else:
                            missing_deps.append(
                                f"  - Ligne {dep.line_number}: `{dep.import_path}` ❌ (fichier introuvable)"
                            )
                            inconsistencies.append(
                                f"Import introuvable: `{dep.import_path}` à la ligne {dep.line_number}"
                            )

                    if deps_list:
                        dependencies_info = "\n\nDépendances détectées:\n" + "\n".join(deps_list)
                    if missing_deps:
                        dependencies_info += "\n\n⚠️ Imports introuvables:\n" + "\n".join(
                            missing_deps
                        )

            # Rechercher de la documentation en ligne si activé
            web_docs = ""
            if self.doc_searcher:
                try:
                    web_docs = await self.doc_searcher.search_documentation(
                        language, file_path, content
                    )
                except Exception as e:
                    print(
                        f"⚠️  Erreur lors de la recherche de documentation pour {relative_path}: {e}"
                    )

            # Générer du code d'analyse approfondie (si activé)
            generated_code_info = ""
            if self.code_generator and self.config.enable_code_generation:
                try:
                    # Générer du code d'analyse pour mieux comprendre le code source
                    analysis_code = await self.code_generator.generate_analysis_code(
                        content[:5000],
                        language,
                        "Analyse approfondie de la structure, des dépendances et des patterns",
                    )
                    if analysis_code:
                        generated_code_info = f"\n\n## Code d'analyse généré pour compréhension approfondie\n\n```{language.lower()}\n{analysis_code[:2000]}\n```\n"
                except Exception as e:
                    print(
                        f"⚠️  Erreur lors de la génération de code d'analyse pour {relative_path}: {e}"
                    )

            # Prompt pour l'analyse conforme au template
            prompt = f"""Tu es un expert en analyse de code. Analyse ce fichier et génère une synthèse structurée en Markdown en respectant EXACTEMENT le format suivant.

Fichier: {relative_path}
Langage: {language}
{dependencies_info}

{web_docs}
{generated_code_info}

Contenu du fichier:
```
{content[:50000]}  # Limite à 50k caractères pour éviter les limites de contexte
```

Génère une analyse complète en Markdown avec EXACTEMENT ce format (respecte l'ordre et la structure):

Voici l'analyse structurée du fichier `{relative_path}`.

# Analyse: {relative_path}

## Langage détecté

{language}

## Objectif / Fonction principale

Décris clairement l'objectif et la fonction principale de ce fichier. Peut contenir une liste numérotée des fonctions principales si pertinent.

## Points forts / Bonnes pratiques

- **Titre du point :** Description détaillée
- **Autre point :** Description

Utilise des listes à puces avec des titres en gras suivis de deux-points. Sois spécifique et actionnable.

## Relations et dépendances

Analyse les imports et dépendances de ce fichier. Identifie:
- Les dépendances manquantes ou introuvables
- Les incohérences de types/interfaces entre fichiers
- Les problèmes de couplage ou de dépendances circulaires
- Les exports manquants ou incorrects

Si des dépendances sont listées ci-dessus, analyse chaque relation et détecte les incohérences potentielles (types incompatibles, interfaces manquantes, etc.).

## Risques, dettes techniques ou incohérences

- **Titre du risque :** Description détaillée du problème et de son impact
- **Autre risque :** Description

Utilise des listes à puces avec des titres en gras suivis de deux-points. Sois constructif et précis. Inclus les problèmes détectés dans les relations et dépendances.

## Suggestions d'amélioration

1.  **Titre de l'amélioration :**
    Description détaillée de la suggestion et comment l'implémenter.

2.  **Autre amélioration :**
    Description.

Utilise des listes numérotées avec des titres en gras suivis de deux-points. Fournis des suggestions actionnables et concrètes. Inclus des exemples de code si pertinent.

IMPORTANT:
- Commence toujours par "Voici l'analyse structurée du fichier `{relative_path}`."
- Utilise des slashes (/) pour les chemins, jamais des backslashes
- Respecte exactement l'ordre des sections
- Utilise le format de liste spécifié pour chaque section
- Sois précis, concis et actionnable. Focus sur la qualité du code, la maintenabilité et les bonnes pratiques.
- Si une documentation en ligne est fournie ci-dessus, utilise-la pour enrichir tes suggestions et identifier les meilleures pratiques actuelles."""

            # Appel à Gemini avec retry (utilise la méthode de BaseAgent)
            analysis_text = await self._call_gemini_with_retry(prompt)

            # Extraire les sections
            objective = self._extract_section(analysis_text, "Objectif", "Points forts")
            strengths = self._extract_list_items(analysis_text, "Points forts", "Relations")
            # Extraire les relations si présentes
            relations_section = self._extract_section(analysis_text, "Relations", "Risques")
            if not relations_section:
                # Essayer sans la section Relations
                strengths = self._extract_list_items(analysis_text, "Points forts", "Risques")
            risks = self._extract_list_items(analysis_text, "Risques", "Suggestions")
            suggestions = self._extract_list_items(analysis_text, "Suggestions", None)

            # Extraire les incohérences depuis la section Relations ou Risques
            if relations_section:
                # Chercher des incohérences mentionnées dans la section Relations
                relation_lines = relations_section.split("\n")
                for line in relation_lines:
                    if any(
                        keyword in line.lower()
                        for keyword in [
                            "incohérence",
                            "manquant",
                            "introuvable",
                            "incompatible",
                            "erreur",
                        ]
                    ):
                        if line.strip() and not line.strip().startswith("#"):
                            inconsistencies.append(line.strip())

            return FileAnalysis(
                file_path=file_path,
                language=language,
                objective=objective or "Non spécifié",
                strengths=strengths,
                risks=risks,
                suggestions=suggestions,
                analysis_markdown=analysis_text,
                success=True,
                dependencies=dependencies,
                inconsistencies=inconsistencies,
            )

        except Exception as e:
            return FileAnalysis(
                file_path=file_path,
                language=self.detect_language(file_path),
                objective="Erreur lors de l'analyse",
                strengths=[],
                risks=[f"Erreur: {str(e)}"],
                suggestions=[],
                analysis_markdown="",
                success=False,
                error=str(e),
            )

    def _extract_section(self, text: str, start_marker: str, end_marker: Optional[str]) -> str:
        """Extrait une section du texte entre deux marqueurs"""
        pattern = (
            f"## {start_marker}[^\n]*\n(.*?)(?=## {end_marker}|$)"
            if end_marker
            else f"## {start_marker}[^\n]*\n(.*?)$"
        )
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""

    def _extract_list_items(
        self, text: str, start_marker: str, end_marker: Optional[str]
    ) -> List[str]:
        """Extrait les éléments de liste d'une section"""
        section = self._extract_section(text, start_marker, end_marker)
        if not section:
            return []

        # Extraire les items de liste (bullet points)
        items = re.findall(r"^[-*+]\s+(.+)$", section, re.MULTILINE)
        if not items:
            # Essayer avec numérotation
            items = re.findall(r"^\d+\.\s+(.+)$", section, re.MULTILINE)
        if not items:
            # Prendre les lignes non vides
            items = [
                line.strip()
                for line in section.split("\n")
                if line.strip() and not line.strip().startswith("#")
            ]

        return [item.strip() for item in items if item.strip()]

    async def analyze_file_structured(
        self, file_path: str, use_thinking: bool = False
    ) -> Optional[FileAnalysisResult]:
        """
        Analyse un fichier avec sortie structurée (Gemini Structured Outputs)

        Cette méthode utilise les Structured Outputs de Gemini pour garantir
        des analyses JSON validées via Pydantic.

        Args:
            file_path: Chemin du fichier à analyser
            use_thinking: Activer le mode thinking pour un raisonnement plus profond

        Returns:
            FileAnalysisResult validé par Pydantic, ou None en cas d'erreur
        """
        try:
            # Lire le contenu du fichier
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            if not content.strip():
                return None

            language = self.detect_language(file_path)
            relative_path = os.path.relpath(file_path, self.config.root_dir)
            relative_path = relative_path.replace("\\", "/")

            prompt = f"""Tu es un expert en analyse de code. Analyse ce fichier de manière approfondie.

Fichier: {relative_path}
Langage: {language}

Contenu du fichier:
```
{content[:50000]}
```

Effectue une analyse complète incluant:
1. Le résumé et l'objectif du fichier
2. Les issues de qualité (maintenabilité, lisibilité, style)
3. Les issues de sécurité potentielles
4. Les métriques de code (complexité, lignes, fonctions, classes)
5. Les dépendances du fichier
6. Les recommandations d'amélioration
7. Les fonctions et classes principales

Sois précis, constructif et actionnable."""

            # Utiliser structured output ou thinking selon la config
            if self.config.enable_structured_outputs:
                try:
                    result = await self._call_ai_structured(prompt, FileAnalysisResult)
                    return result
                except Exception:
                    # Fallback vers l'analyse standard
                    pass

            if use_thinking and self.config.enable_thinking:
                response, thoughts = await self._call_ai_with_thinking(prompt)
                if thoughts and self.progress_manager:
                    self.progress_manager.print_reasoning(thoughts, self.config.ai_model)
                # Parse JSON de la réponse (format moins garanti)
                return None

            return None

        except Exception:
            return None

    async def analyze_with_code_execution(self, file_path: str, analysis_task: str) -> dict:
        """
        Analyse un fichier avec exécution de code Python

        Cette méthode permet au modèle d'exécuter du code Python pour
        effectuer des analyses dynamiques (ex: parsing AST, métriques avancées).

        Args:
            file_path: Chemin du fichier à analyser
            analysis_task: Description de l'analyse à effectuer

        Returns:
            Dict avec text, executable_code, code_output, error
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            language = self.detect_language(file_path)
            relative_path = os.path.relpath(file_path, self.config.root_dir)
            relative_path = relative_path.replace("\\", "/")

            prompt = f"""Tu es un expert en analyse de code avec la capacité d'exécuter du Python.

Fichier à analyser: {relative_path}
Langage: {language}
Tâche: {analysis_task}

Contenu du fichier:
```
{content[:30000]}
```

Écris et exécute du code Python pour analyser ce fichier.
Par exemple, tu peux:
- Parser le code avec ast (pour Python) ou des regex
- Calculer des métriques (complexité, lignes, fonctions)
- Détecter des patterns ou anti-patterns
- Extraire des informations structurées

Explique tes résultats après l'exécution du code."""

            return await self._call_ai_with_code_execution(prompt)

        except Exception as e:
            return {
                "text": f"Erreur lors de l'analyse: {str(e)}",
                "executable_code": None,
                "code_output": None,
                "error": str(e),
            }
