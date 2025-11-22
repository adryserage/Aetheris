"""
Configuration de l'analyse
"""

import os
from dataclasses import dataclass
from typing import Dict


@dataclass
class AnalysisConfig:
    """Configuration de l'analyse"""
    gemini_api_key: str
    gemini_model: str = "gemini-3-pro-preview"  # Modèle Gemini (peut être changé via GEMINI_MODEL)
    batch_size: int = 10
    max_retries: int = 3
    timeout_seconds: int = 60
    output_dir: str = "docs/analyses"
    architecture_report_path: str = "docs/architecture_overview.md"
    root_dir: str = "."
    enable_web_search: bool = True  # Activer la recherche web pour les documentations
    max_web_results: int = 3  # Nombre maximum de résultats de recherche par requête
    enable_security_analysis: bool = True  # Activer l'analyse de sécurité
    enable_metrics_analysis: bool = True  # Activer l'analyse de métriques
    enable_dependency_vulnerability: bool = True  # Activer l'analyse de vulnérabilités des dépendances
    enable_code_generation: bool = True  # Permettre aux agents de générer du code pour l'analyse


def load_env_file(env_path: str = '.env') -> Dict[str, str]:
    """Charge les variables d'environnement depuis un fichier .env"""
    env_vars = {}
    if os.path.exists(env_path):
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Ignorer les lignes vides et les commentaires
                    if not line or line.startswith('#'):
                        continue
                    # Parser KEY=VALUE ou KEY="VALUE"
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        # Enlever les guillemets si présents
                        if (value.startswith('"') and value.endswith('"')) or \
                           (value.startswith("'") and value.endswith("'")):
                            value = value[1:-1]
                        env_vars[key] = value
        except Exception as e:
            print(f"⚠️  Erreur lors de la lecture de {env_path}: {e}")
    return env_vars

