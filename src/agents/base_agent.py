"""
Classe de base pour tous les agents d'analyse
"""

from src.core.config import AnalysisConfig
from src.core.ai_providers import create_ai_provider, AIProvider


class BaseAgent:
    """Classe de base pour tous les agents d'analyse avec logique commune"""

    def __init__(self, config: AnalysisConfig):
        self.config = config
        self.ai_provider: AIProvider = create_ai_provider(
            provider=config.ai_provider,
            api_key=config.ai_api_key,
            model=config.ai_model,
            timeout_seconds=config.timeout_seconds,
            max_retries=config.max_retries,
        )

    async def _call_ai_with_retry(self, prompt: str, timeout_multiplier: float = 1.0) -> str:
        """
        Appelle l'API AI avec retry et gestion des timeouts

        Args:
            prompt: Le prompt à envoyer au modèle AI
            timeout_multiplier: Multiplicateur pour le timeout (défaut: 1.0)

        Returns:
            Le texte de la réponse du modèle AI

        Raises:
            Exception: Si toutes les tentatives échouent
        """
        return await self.ai_provider.generate_content_with_retry(prompt, timeout_multiplier)

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
