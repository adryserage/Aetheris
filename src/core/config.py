"""
Configuration de l'analyse
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# Modèles par défaut par fournisseur
DEFAULT_MODELS = {
    "gemini": "gemini-2.5-flash",  # Nouveau modèle avec toutes les fonctionnalités
    "openai": "gpt-4o",
    "claude": "claude-3-5-sonnet-20241022",
}

# Modèles supportés par fournisseur
SUPPORTED_MODELS = {
    "gemini": [
        # Dernière génération (fonctionnalités complètes)
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        # Génération précédente
        "gemini-2.0-flash-exp",
        "gemini-1.5-pro",
        "gemini-1.5-pro-latest",
        "gemini-1.5-flash",
        "gemini-pro",
    ],
    "openai": [
        "gpt-4o",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
        "gpt-4-turbo-preview",
        "o1-preview",
        "o1-mini",
    ],
    "claude": ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-haiku-20240307"],
}


def get_default_model(provider: str) -> str:
    """Retourne le modèle par défaut pour un provider"""
    return DEFAULT_MODELS.get(provider.lower(), DEFAULT_MODELS["gemini"])


def validate_provider_model(provider: str, model: str) -> bool:
    """
    Valide qu'un modèle est supporté pour un provider donné

    Args:
        provider: Le provider AI ("gemini", "openai", "claude")
        model: Le nom du modèle

    Returns:
        True si la combinaison est valide, False sinon
    """
    provider = provider.lower()
    if provider not in SUPPORTED_MODELS:
        return False
    return model in SUPPORTED_MODELS[provider]


@dataclass
class AnalysisConfig:
    """Configuration de l'analyse"""

    ai_provider: str = "gemini"  # Provider AI: "gemini", "openai", "claude"
    ai_api_key: str = ""  # Clé API du provider sélectionné
    ai_model: str = ""  # Modèle à utiliser (défaut selon provider)
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
    enable_dependency_vulnerability: bool = (
        True  # Activer l'analyse de vulnérabilités des dépendances
    )
    enable_code_generation: bool = True  # Permettre aux agents de générer du code pour l'analyse
    analyze_changed_files_only: bool = (
        False  # Analyser uniquement les fichiers modifiés (pour PR/commits)
    )
    changed_files: List[str] = field(default_factory=list)  # Liste des fichiers à analyser
    pr_number: Optional[int] = None  # Numéro de PR (optionnel)
    show_reasoning: bool = False  # Afficher le processus de reasoning du modèle (si disponible)
    enable_cache: bool = True  # Activer le cache des analyses (réduit les coûts API)
    cache_ttl_days: int = 7  # Durée de vie du cache en jours
    analyze_dependent_files: bool = True  # Analyser les fichiers dépendants des fichiers modifiés
    max_dependency_depth: int = 2  # Profondeur maximale pour l'analyse des dépendances
    enable_metrics: bool = True  # Activer la collecte de métriques
    enable_priority_analysis: bool = True  # Activer l'analyse par priorité (PR files = HIGH)

    # Options d'analyse des exports et dépendances inverses
    enable_export_analysis: bool = True  # Activer l'extraction des exports
    enable_reverse_dependency: bool = True  # Activer le graphe de dépendances inverses
    enable_impact_analysis: bool = True  # Activer l'analyse d'impact des bugs
    max_impact_depth: int = 3  # Profondeur maximale pour l'analyse d'impact

    # Options Claude Code
    enable_claude_code_fix: bool = True  # Activer l'intégration Claude Code pour la correction
    fix_severity_threshold: str = "medium"  # Seuil de sévérité minimale pour les corrections
    bugs_cache_file: str = ".bugs_cache.json"  # Fichier cache des bugs

    # === Gemini Advanced Features (google-genai SDK) ===
    # Ces options ne s'appliquent qu'au provider Gemini

    # Code Execution : permet au modèle d'exécuter du code Python en sandbox
    enable_code_execution: bool = False

    # Structured Outputs : utilise des schémas Pydantic pour des réponses JSON garanties
    enable_structured_outputs: bool = True

    # Function Calling : permet au modèle d'appeler des fonctions Python
    enable_function_calling: bool = False

    # Thinking/Reasoning : affiche le processus de raisonnement du modèle
    enable_thinking: bool = False
    thinking_budget: int = 1024  # Budget de tokens pour le raisonnement (min 128)

    # Context Caching : cache API pour réduire les coûts (~50%)
    enable_context_caching: bool = True
    cache_ttl_seconds: int = 3600  # Durée de vie du cache en secondes (1h par défaut)

    # Batch API : traitement en lot à coût réduit (-50%)
    enable_batch_mode: bool = False

    # Google Search : recherche web intégrée pour grounding
    enable_google_search: bool = False

    def __post_init__(self):
        """Initialise les valeurs par défaut après création"""
        # Normaliser le provider
        self.ai_provider = self.ai_provider.lower()

        # Si le modèle n'est pas spécifié, utiliser le défaut du provider
        if not self.ai_model:
            self.ai_model = get_default_model(self.ai_provider)

        # Valider la combinaison provider/model
        if not validate_provider_model(self.ai_provider, self.ai_model):
            # Avertir mais ne pas bloquer (certains modèles peuvent être valides mais pas dans la liste)
            pass


def load_env_file(env_path: str = ".env") -> Dict[str, str]:
    """Charge les variables d'environnement depuis un fichier .env"""
    env_vars = {}
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # Ignorer les lignes vides et les commentaires
                    if not line or line.startswith("#"):
                        continue
                    # Parser KEY=VALUE ou KEY="VALUE"
                    if "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip()
                        # Enlever les guillemets si présents
                        if (value.startswith('"') and value.endswith('"')) or (
                            value.startswith("'") and value.endswith("'")
                        ):
                            value = value[1:-1]
                        env_vars[key] = value
        except Exception as e:
            print(f"⚠️  Erreur lors de la lecture de {env_path}: {e}")
    return env_vars
