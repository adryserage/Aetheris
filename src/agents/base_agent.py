"""
Classe de base pour tous les agents d'analyse
"""

from typing import Optional
from src.core.config import AnalysisConfig
from src.core.ai_providers import create_ai_provider, AIProvider
from src.core.progress import ProgressManager
from src.core.error_handler import exponential_backoff, CircuitBreaker


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
