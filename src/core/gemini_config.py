"""
Configuration des fonctionnalités avancées Gemini 3 Pro

Ce module définit les options de configuration pour les fonctionnalités
avancées du SDK google-genai :
- Code Execution : exécution de Python en sandbox
- Structured Outputs : réponses JSON validées via Pydantic
- Function Calling : appel automatique de fonctions Python
- Thinking/Reasoning : affichage du processus de raisonnement
- Context Caching : cache API pour réduire les coûts
- Batch API : traitement en lot à coût réduit
- Google Search : recherche web intégrée (grounding)
"""

from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Type

if TYPE_CHECKING:
    from pydantic import BaseModel


@dataclass
class GeminiFeatureConfig:
    """Configuration des fonctionnalités avancées Gemini"""

    # === Code Execution ===
    enable_code_execution: bool = False

    # === Structured Outputs ===
    response_schema: Optional[Type["BaseModel"]] = None
    response_mime_type: str = "text/plain"  # ou "application/json"

    # === Function Calling ===
    tools: List[Any] = field(default_factory=list)
    automatic_function_calling: bool = True

    # === Thinking/Reasoning ===
    enable_thinking: bool = False
    thinking_budget: int = 0  # 0 = désactivé, min 128 pour gemini-2.5+
    include_thoughts: bool = False

    # === Context Caching ===
    use_cached_content: Optional[str] = None  # nom du cache à utiliser

    # === Google Search (Grounding) ===
    enable_google_search: bool = False

    # === Generation Parameters ===
    temperature: float = 0.7
    max_output_tokens: int = 8192
    top_p: float = 0.95
    top_k: int = 40
    stop_sequences: List[str] = field(default_factory=list)

    # === System Instruction ===
    system_instruction: Optional[str] = None


@dataclass
class CodeExecutionResult:
    """Résultat d'une exécution de code par le modèle"""

    text: str  # Texte explicatif généré
    executable_code: Optional[str] = None  # Code Python généré
    code_output: Optional[str] = None  # Résultat de l'exécution
    error: Optional[str] = None  # Erreur si l'exécution a échoué


@dataclass
class ThinkingResult:
    """Résultat avec processus de raisonnement"""

    text: str  # Réponse finale
    thoughts: Optional[str] = None  # Processus de raisonnement


@dataclass
class CacheConfig:
    """Configuration pour le cache de contexte"""

    display_name: str
    system_instruction: str
    ttl_seconds: int = 3600  # 1 heure par défaut
    contents: List[str] = field(default_factory=list)


@dataclass
class BatchRequest:
    """Requête pour le batch API"""

    key: str  # Identifiant unique de la requête
    contents: str  # Prompt/contenu
    config: Optional[Dict[str, Any]] = None  # Configuration optionnelle


@dataclass
class BatchJobInfo:
    """Informations sur un job batch"""

    name: str  # Identifiant du job
    state: str  # État du job (PENDING, RUNNING, COMPLETED, FAILED)
    create_time: Optional[str] = None
    update_time: Optional[str] = None
    total_requests: int = 0
    completed_requests: int = 0
    failed_requests: int = 0


# === Constantes pour les modèles supportant les fonctionnalités avancées ===

MODELS_WITH_CODE_EXECUTION = [
    "gemini-3-pro-preview",
    "gemini-2.5-pro",
    "gemini-3-pro-preview",
    "gemini-2.0-flash-exp",
]

MODELS_WITH_THINKING = [
    "gemini-3-pro-preview",
    "gemini-2.5-pro",
]

MODELS_WITH_CACHING = [
    "gemini-3-pro-preview",
    "gemini-2.5-pro",
    "gemini-3-pro-preview",
    "gemini-1.5-pro",
    "gemini-1.5-flash",
]

MODELS_WITH_BATCH = [
    "gemini-3-pro-preview",
    "gemini-2.5-pro",
    "gemini-3-pro-preview",
    "gemini-2.0-flash",
]

# Limites de tokens pour gemini-3-pro-preview
GEMINI_3_PRO_LIMITS = {
    "max_input_tokens": 1_048_576,
    "max_output_tokens": 65_536,
    "min_thinking_budget": 128,
    "max_thinking_budget": 32_768,
}


def supports_code_execution(model: str) -> bool:
    """Vérifie si le modèle supporte l'exécution de code"""
    return any(m in model for m in MODELS_WITH_CODE_EXECUTION)


def supports_thinking(model: str) -> bool:
    """Vérifie si le modèle supporte le mode thinking"""
    return any(m in model for m in MODELS_WITH_THINKING)


def supports_caching(model: str) -> bool:
    """Vérifie si le modèle supporte le cache de contexte"""
    return any(m in model for m in MODELS_WITH_CACHING)


def supports_batch(model: str) -> bool:
    """Vérifie si le modèle supporte le batch API"""
    return any(m in model for m in MODELS_WITH_BATCH)
