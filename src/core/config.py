"""
Configuration de l'analyse
"""

import os
import re
from dataclasses import dataclass
from dataclasses import field
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

# === Timeout Configuration ===
# Default timeout: 60 minutes (v2.6.1)
DEFAULT_TIMEOUT_SECONDS = 3600  # 60 minutes
HEARTBEAT_INTERVAL_SECONDS = 600  # 10 minutes


class TimeoutParseError(ValueError):
    """Exception raised when timeout format is invalid"""

    pass


@dataclass
class TimeoutConfig:
    """Configuration for analysis timeout (v2.6.1)

    Supports formats:
    - Integer: seconds (e.g., 3600)
    - String with suffix: "30m" (minutes), "2h" (hours), "3600s" (seconds)
    - Special values: "0" or "no-limit" for unlimited
    """

    value: int  # Timeout in seconds
    enabled: bool  # Whether timeout is active (False when value=0 or no-limit)

    @classmethod
    def parse(cls, timeout_str: Union[str, int, None]) -> "TimeoutConfig":
        """Parse timeout from CLI string or integer

        Args:
            timeout_str: Timeout value as string ("30m", "2h", "3600", "0", "no-limit")
                        or as integer (seconds), or None for default

        Returns:
            TimeoutConfig instance

        Raises:
            TimeoutParseError: If format is invalid or value is negative
        """
        # None means use default
        if timeout_str is None:
            return cls(value=DEFAULT_TIMEOUT_SECONDS, enabled=True)

        # Already an integer
        if isinstance(timeout_str, int):
            if timeout_str < 0:
                raise TimeoutParseError(
                    f"Timeout cannot be negative: {timeout_str}. "
                    f"Use 0 or 'no-limit' to disable timeout."
                )
            if timeout_str == 0:
                return cls(value=0, enabled=False)
            return cls(value=timeout_str, enabled=True)

        # Convert to string and strip
        timeout_str = str(timeout_str).strip().lower()

        # Handle special "no-limit" value
        if timeout_str in ("no-limit", "no_limit", "nolimit", "unlimited", "none"):
            return cls(value=0, enabled=False)

        # Handle "0" as unlimited
        if timeout_str == "0":
            return cls(value=0, enabled=False)

        # Parse format: number + optional suffix (s/m/h)
        pattern = r"^(\d+)(s|m|h)?$"
        match = re.match(pattern, timeout_str)

        if not match:
            raise TimeoutParseError(
                f"Invalid timeout format: '{timeout_str}'. "
                f"Valid formats: 3600 (seconds), 30m (minutes), 2h (hours), 0 or no-limit (unlimited)"
            )

        value = int(match.group(1))
        suffix = match.group(2)

        # Convert to seconds based on suffix
        if suffix == "m":
            value = value * 60
        elif suffix == "h":
            value = value * 3600
        # 's' or no suffix means seconds

        if value < 0:
            raise TimeoutParseError(
                f"Timeout cannot be negative: {timeout_str}. "
                f"Use 0 or 'no-limit' to disable timeout."
            )

        if value == 0:
            return cls(value=0, enabled=False)

        return cls(value=value, enabled=True)

    def format_human(self) -> str:
        """Return human-readable timeout string"""
        if not self.enabled:
            return "unlimited"

        if self.value >= 3600 and self.value % 3600 == 0:
            hours = self.value // 3600
            return f"{hours}h" if hours > 1 else "1h"
        elif self.value >= 60 and self.value % 60 == 0:
            minutes = self.value // 60
            return f"{minutes}m"
        else:
            return f"{self.value}s"


# Modèles par défaut par fournisseur
DEFAULT_MODELS = {
    "gemini": "gemini-3-pro-preview",  # Nouveau modèle avec toutes les fonctionnalités
    "openai": "gpt-4o",
    "claude": "claude-3-5-sonnet-20241022",
}

# Modèles supportés par fournisseur
SUPPORTED_MODELS = {
    "gemini": [
        # Dernière génération (fonctionnalités complètes)
        "gemini-3-pro-preview",
        "gemini-2.5-pro",
        "gemini-3-pro-preview",
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
    batch_size: int = 15  # Optimal pour parallélisation + rate limits
    max_retries: int = 3
    timeout_seconds: int = 60  # Legacy: per-request timeout (kept for compatibility)

    # === Timeout Configuration (v2.6.1) ===
    # Global timeout for the entire analysis workflow
    timeout_config: Optional[TimeoutConfig] = None  # Parsed from --timeout CLI flag
    heartbeat_interval: int = HEARTBEAT_INTERVAL_SECONDS  # Heartbeat interval (default: 10 min)
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
    cache_ttl_seconds: int = 604800  # Durée de vie du cache en secondes (7 jours)
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
    enable_batch_mode: bool = True

    # Google Search : recherche web intégrée pour grounding
    enable_google_search: bool = False

    # === User Story Analysis Options ===
    # Analyse des flux frontend ↔ backend et détection d'incohérences

    # Activer l'analyse de user stories
    enable_user_story_analysis: bool = True

    # Profondeur maximale des flux (nombre d'étapes)
    user_story_max_depth: int = 15

    # Détection des endpoints orphelins (définis mais jamais appelés)
    detect_orphan_endpoints: bool = True

    # Détection du code mort dans les flux
    detect_dead_code: bool = True

    # Détection des race conditions potentielles
    detect_race_conditions: bool = True

    # Détection de la gestion d'erreurs manquante
    detect_missing_error_handling: bool = True

    # Détection des problèmes d'authentification
    detect_auth_issues: bool = True

    # Format de diagramme par défaut (mermaid, plantuml)
    user_story_diagram_format: str = "mermaid"

    # Répertoire de sortie pour les rapports de user stories
    user_story_output_dir: str = "docs/user-stories"

    # Sévérité minimale pour les issues (critical, high, medium, low, info)
    user_story_min_severity: str = "low"

    # === PR Review Options ===
    # Options pour la commande `aetheris pr`

    # Providers AI à utiliser pour la revue de PR (séparés par virgule)
    pr_providers: List[str] = field(default_factory=lambda: ["gemini"])

    # Mode consensus : ne retient que les issues trouvées par TOUS les providers
    pr_consensus_mode: bool = True

    # Sévérité minimale des issues à reporter
    pr_min_severity: str = "low"

    # Poster des commentaires inline sur les lignes spécifiques
    pr_post_inline_comments: bool = True

    # Proposer de corriger automatiquement si c'est notre PR
    pr_auto_fix_own_pr: bool = False

    # Mode dry-run : analyser sans poster de commentaires
    pr_dry_run: bool = False

    def __post_init__(self):
        """Initialise les valeurs par défaut après création"""
        # Normaliser le provider
        self.ai_provider = self.ai_provider.lower()

        # Si le modèle n'est pas spécifié ou est "default", utiliser le défaut du provider
        # Cela permet aux utilisateurs de spécifier "default" dans config.json/.env
        # pour toujours utiliser le modèle recommandé sans hardcoder les noms de modèles
        if not self.ai_model or self.ai_model.lower() == "default":
            self.ai_model = get_default_model(self.ai_provider)

        # Valider la combinaison provider/model
        if not validate_provider_model(self.ai_provider, self.ai_model):
            # Avertir mais ne pas bloquer (certains modèles peuvent être valides mais pas dans la liste)
            pass

        # Initialize timeout_config with default if not set (v2.6.1)
        if self.timeout_config is None:
            self.timeout_config = TimeoutConfig(value=DEFAULT_TIMEOUT_SECONDS, enabled=True)


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
                        else:
                            # Supprimer les commentaires inline (sauf si entre guillemets)
                            # Ex: API_KEY=abc123  # commentaire -> API_KEY=abc123
                            if "#" in value:
                                value = value.split("#")[0].strip()
                        env_vars[key] = value
        except Exception as e:
            print(f"⚠️  Erreur lors de la lecture de {env_path}: {e}")
    return env_vars
