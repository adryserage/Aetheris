"""
Générateur de code pour les agents - permet de créer du code temporaire pour l'analyse
"""

import os
from typing import List, Optional

from src.core.ai_providers import create_ai_provider
from src.core.config import AnalysisConfig


class CodeGenerator:
    """Générateur de code pour les agents - permet de créer du code temporaire pour l'analyse"""

    def __init__(self, config: AnalysisConfig):
        self.config = config
        self.temp_dir = os.path.join(config.root_dir, ".analysis_temp")
        self.generated_files: List[str] = []
        os.makedirs(self.temp_dir, exist_ok=True)
        self.ai_provider = create_ai_provider(
            provider=config.ai_provider,
            api_key=config.ai_api_key,
            model=config.ai_model,
            timeout_seconds=config.timeout_seconds,
            max_retries=config.max_retries,
        )

    async def generate_analysis_code(
        self, original_code: str, language: str, analysis_focus: str
    ) -> Optional[str]:
        """Génère du code d'analyse approfondie pour mieux comprendre le code source"""
        try:
            prompt = f"""Tu es un expert en analyse de code. Génère du code d'analyse approfondie pour mieux comprendre et analyser le code suivant.

Langage: {language}
Focus d'analyse: {analysis_focus}

Code source à analyser:
```
{original_code[:10000]}
```

Génère du code d'analyse qui:
1. Explore la structure et les dépendances internes
2. Identifie les patterns et anti-patterns
3. Analyse les flux de données et de contrôle
4. Détecte les problèmes potentiels de logique
5. Vérifie la cohérence des types et interfaces

IMPORTANT:
- Génère UNIQUEMENT du code d'analyse, pas d'exemples d'utilisation
- Pas de conseils de code à utiliser
- Focus sur la compréhension et l'analyse, pas sur l'implémentation
- Le code généré doit aider à mieux comprendre le code source, pas à le remplacer

Retourne UNIQUEMENT le code d'analyse généré, sans explications supplémentaires."""

            generated_code = await self.ai_provider.generate_content_with_retry(prompt)
            generated_code = generated_code.strip()

            # Nettoyer le code (enlever les blocs markdown si présents)
            if generated_code.startswith("```"):
                lines = generated_code.split("\n")
                # Enlever la première ligne (```langage) et la dernière (```)
                generated_code = "\n".join(lines[1:-1])

            return generated_code
        except Exception as e:
            print(f"⚠️  Erreur lors de la génération de code d'analyse: {e}")
            return None

    def save_temp_file(self, content: str, extension: str, prefix: str = "temp") -> Optional[str]:
        """Sauvegarde un fichier temporaire et retourne son chemin"""
        try:
            import uuid

            filename = f"{prefix}_{uuid.uuid4().hex[:8]}.{extension}"
            file_path = os.path.join(self.temp_dir, filename)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            self.generated_files.append(file_path)
            return file_path
        except Exception as e:
            print(f"⚠️  Erreur lors de la sauvegarde du fichier temporaire: {e}")
            return None

    def cleanup(self):
        """Nettoie les fichiers temporaires générés"""
        try:
            for file_path in self.generated_files:
                if os.path.exists(file_path):
                    os.remove(file_path)
            if os.path.exists(self.temp_dir) and not os.listdir(self.temp_dir):
                os.rmdir(self.temp_dir)
        except Exception as e:
            print(f"⚠️  Erreur lors du nettoyage: {e}")
