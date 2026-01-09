"""
Classe de base pour tous les agents d'analyse
"""

from typing import TYPE_CHECKING, Optional, Tuple, Type

from src.core.ai_providers import AIProvider, GeminiProvider, create_ai_provider
from src.core.config import AnalysisConfig

if TYPE_CHECKING:
    from pydantic import BaseModel

from src.core.error_handler import CircuitBreaker, exponential_backoff
from src.core.progress import ProgressManager


class BaseAgent:
    """Classe de base pour tous les agents d'analyse avec logique commune"""

    def __init__(self, config: AnalysisConfig, progress_manager: Optional[ProgressManager] = None):
        self.config = config
        self.progress_manager = progress_manager
        self.ai_provider: AIProvider = create_ai_provider(
            provider=config.ai_provider,
            api_key=config.ai_api_key,
            model=config.ai_model,
            timeout_seconds=config.timeout_seconds,
            max_retries=config.max_retries,
        )
        # Circuit breaker pour éviter les appels répétés en cas d'erreur
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            success_threshold=2,
            timeout_seconds=60,
        )

    async def _call_ai_with_retry(self, prompt: str, timeout_multiplier: float = 1.0) -> str:
        """
        Appelle l'API AI avec retry, backoff exponentiel et circuit breaker

        Args:
            prompt: Le prompt à envoyer au modèle AI
            timeout_multiplier: Multiplicateur pour le timeout (défaut: 1.0)

        Returns:
            Le texte de la réponse du modèle AI

        Raises:
            Exception: Si toutes les tentatives échouent
        """

        async def _call():
            return await self.ai_provider.generate_content_with_retry(prompt, timeout_multiplier)

        return await exponential_backoff(
            _call,
            max_retries=self.config.max_retries,
            initial_delay=1.0,
            max_delay=60.0,
            multiplier=2.0,
            circuit_breaker=self.circuit_breaker,
        )

    async def _call_ai_with_reasoning(self, prompt: str, timeout_multiplier: float = 1.0) -> str:
        """
        Appelle l'API AI avec reasoning si activé et disponible

        Args:
            prompt: Le prompt à envoyer au modèle AI
            timeout_multiplier: Multiplicateur pour le timeout (défaut: 1.0)

        Returns:
            Le texte de la réponse du modèle AI
        """
        if self.config.show_reasoning:
            content, reasoning = await self.ai_provider.generate_content_with_reasoning(prompt)
            if reasoning and self.progress_manager:
                self.progress_manager.print_reasoning(reasoning, self.config.ai_model)
            return content
        else:
            return await self._call_ai_with_retry(prompt, timeout_multiplier)

    # Alias pour compatibilité avec le code existant
    async def _call_gemini_with_retry(self, prompt: str, timeout_multiplier: float = 1.0) -> str:
        """
        Alias pour _call_ai_with_retry (maintenu pour compatibilité)

        Args:
            prompt: Le prompt à envoyer au modèle AI
            timeout_multiplier: Multiplicateur pour le timeout (défaut: 1.0)

        Returns:
            Le texte de la réponse du modèle AI
        """
        return await self._call_ai_with_retry(prompt, timeout_multiplier)

    async def _call_ai_structured(self, prompt: str, schema: Type["BaseModel"]) -> "BaseModel":
        """
        Appelle l'API AI avec sortie structurée (Pydantic)

        Cette méthode utilise les Structured Outputs de Gemini pour garantir
        des réponses JSON validées selon un schéma Pydantic.

        Args:
            prompt: Le prompt à envoyer au modèle AI
            schema: La classe Pydantic définissant le schéma de réponse

        Returns:
            Une instance du modèle Pydantic validée

        Note:
            Pour les providers non-Gemini, un fallback parse le JSON manuellement
        """
        if isinstance(self.ai_provider, GeminiProvider) and self.config.enable_structured_outputs:
            return await self.ai_provider.generate_structured(prompt, schema)
        else:
            # Fallback: parse JSON manuellement pour OpenAI/Claude
            response = await self._call_ai_with_retry(prompt)
            # Nettoyer la réponse si elle contient des marqueurs de code
            json_str = response.strip()
            if json_str.startswith("```json"):
                json_str = json_str[7:]
            elif json_str.startswith("```"):
                json_str = json_str[3:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]
            return schema.model_validate_json(json_str.strip())

    async def _call_ai_with_thinking(
        self, prompt: str, budget: Optional[int] = None
    ) -> Tuple[str, Optional[str]]:
        """
        Appelle l'API AI avec raisonnement visible (thinking)

        Cette méthode utilise la fonctionnalité Thinking de Gemini pour
        afficher le processus de raisonnement du modèle.

        Args:
            prompt: Le prompt à envoyer au modèle AI
            budget: Budget de tokens pour le raisonnement (min 128, défaut: config)

        Returns:
            Tuple (réponse, pensées) où pensées peut être None si non disponible

        Note:
            Nécessite un modèle supportant le thinking (gemini-2.5+, gemini-3)
        """
        if budget is None:
            budget = self.config.thinking_budget

        if isinstance(self.ai_provider, GeminiProvider) and self.config.enable_thinking:
            response, thoughts = await self.ai_provider.generate_with_thinking(prompt, budget)
            if thoughts and self.progress_manager:
                self.progress_manager.print_reasoning(thoughts, self.config.ai_model)
            return response, thoughts
        else:
            # Fallback: utiliser le mode reasoning standard
            response = await self._call_ai_with_reasoning(prompt)
            return response, None

    async def _call_ai_with_code_execution(self, prompt: str) -> dict:
        """
        Appelle l'API AI avec exécution de code Python en sandbox

        Cette méthode permet au modèle d'exécuter du code Python pour
        résoudre des problèmes mathématiques, traiter des données, etc.

        Args:
            prompt: Le prompt qui peut nécessiter une exécution de code

        Returns:
            Dict avec: text, executable_code, code_output, error

        Note:
            Uniquement disponible avec Gemini (gemini-2.0+)
        """
        if isinstance(self.ai_provider, GeminiProvider) and self.config.enable_code_execution:
            return await self.ai_provider.generate_with_code_execution(prompt)
        else:
            # Fallback: réponse texte simple
            response = await self._call_ai_with_retry(prompt)
            return {"text": response, "executable_code": None, "code_output": None, "error": None}
