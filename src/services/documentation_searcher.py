"""
Rechercheur de documentation en ligne pour enrichir les analyses
"""

import asyncio
from typing import List

from duckduckgo_search import DDGS

from src.core.config import AnalysisConfig


class DocumentationSearcher:
    """Rechercheur de documentation en ligne pour enrichir les analyses"""

    def __init__(self, config: AnalysisConfig):
        self.config = config
        self.enabled = config.enable_web_search
        self.ddgs = None
        if self.enabled:
            try:
                self.ddgs = DDGS()
            except Exception as e:
                print(f"⚠️  Impossible d'initialiser la recherche web: {e}")
                self.enabled = False

    def _generate_search_queries(self, language: str, file_path: str, content: str) -> List[str]:
        """Génère des requêtes de recherche basées sur le langage et le contenu"""
        queries = []

        # Requêtes génériques par langage
        lang_docs = {
            "Dart": ["Dart documentation", "Flutter best practices", "Dart language guide"],
            "TypeScript": [
                "TypeScript documentation",
                "TypeScript best practices",
                "TypeScript handbook",
            ],
            "TypeScript (React)": [
                "React TypeScript documentation",
                "React best practices",
                "TypeScript React patterns",
            ],
            "JavaScript": [
                "JavaScript documentation",
                "JavaScript best practices",
                "ES6+ features",
            ],
            "JavaScript (React)": [
                "React documentation",
                "React best practices",
                "React hooks guide",
            ],
            "Python": ["Python documentation", "Python best practices", "PEP 8 style guide"],
        }

        # Ajouter des requêtes spécifiques au langage
        if language in lang_docs:
            queries.extend(lang_docs[language])

        # Extraire des frameworks/bibliothèques du contenu
        content_lower = content.lower()

        # Détecter React
        if "react" in content_lower or "react" in file_path.lower():
            queries.append("React latest documentation")

        # Détecter Next.js
        if "next" in content_lower or "next.js" in content_lower:
            queries.append("Next.js documentation")

        # Détecter Flutter
        if "flutter" in content_lower or "flutter" in file_path.lower():
            queries.append("Flutter documentation")

        # Détecter FastAPI
        if "fastapi" in content_lower:
            queries.append("FastAPI documentation")

        # Détecter Express
        if "express" in content_lower:
            queries.append("Express.js documentation")

        return queries[:3]  # Limiter à 3 requêtes

    async def search_documentation(self, language: str, file_path: str, content: str) -> str:
        """Recherche de la documentation en ligne et retourne un résumé"""
        if not self.enabled:
            return ""

        try:
            queries = self._generate_search_queries(language, file_path, content)
            all_results = []

            for query in queries:
                try:
                    # Recherche avec DuckDuckGo (exécutée dans un thread pour ne pas bloquer)
                    results = await asyncio.to_thread(
                        lambda: list(self.ddgs.text(query, max_results=self.config.max_web_results))
                    )

                    for result in results:
                        all_results.append(
                            {
                                "title": result.get("title", ""),
                                "snippet": result.get("body", ""),
                                "url": result.get("href", ""),
                            }
                        )

                    # Petite pause pour éviter les rate limits
                    await asyncio.sleep(0.5)

                except Exception as e:
                    print(f"⚠️  Erreur lors de la recherche '{query}': {e}")
                    continue

            if not all_results:
                return ""

            # Formater les résultats pour inclusion dans le prompt
            formatted_results = "## Documentation en ligne récente\n\n"
            formatted_results += (
                "Les informations suivantes proviennent de recherches web récentes:\n\n"
            )

            seen_urls = set()
            for i, result in enumerate(
                all_results[: self.config.max_web_results * len(queries)], 1
            ):
                url = result.get("url", "")
                if url in seen_urls:
                    continue
                seen_urls.add(url)

                formatted_results += f"### {result.get('title', 'Résultat sans titre')}\n"
                formatted_results += f"**URL:** {url}\n\n"
                formatted_results += f"{result.get('snippet', '')}\n\n"

            return formatted_results

        except Exception as e:
            print(f"⚠️  Erreur lors de la recherche de documentation: {e}")
            return ""
