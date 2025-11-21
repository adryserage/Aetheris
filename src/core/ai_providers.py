"""
Abstraction pour les fournisseurs AI (OpenAI, Claude, Gemini)
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Optional, Tuple


class AIProvider(ABC):
    """Classe abstraite pour les fournisseurs AI"""

    def __init__(self, api_key: str, model: str, timeout_seconds: int = 60, max_retries: int = 3):
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

    @abstractmethod
    async def generate_content(self, prompt: str) -> str:
        """
        Génère du contenu à partir d'un prompt

        Args:
            prompt: Le prompt à envoyer au modèle

        Returns:
            Le texte généré

        Raises:
            Exception: Si la génération échoue
        """
        pass

    async def generate_content_with_reasoning(self, prompt: str) -> Tuple[str, Optional[str]]:
        """
        Génère du contenu avec reasoning si disponible

        Args:
            prompt: Le prompt à envoyer au modèle

        Returns:
            Tuple (contenu, reasoning) où reasoning est None si non disponible

        Raises:
            Exception: Si la génération échoue
        """
        # Par défaut, retourner le contenu sans reasoning
        content = await self.generate_content(prompt)
        return content, None

    async def generate_content_with_retry(
        self, prompt: str, timeout_multiplier: float = 1.0
    ) -> str:
        """
        Génère du contenu avec retry et gestion des timeouts

        Args:
            prompt: Le prompt à envoyer au modèle
            timeout_multiplier: Multiplicateur pour le timeout (défaut: 1.0)

        Returns:
            Le texte généré

        Raises:
            Exception: Si toutes les tentatives échouent
        """
        timeout = int(self.timeout_seconds * timeout_multiplier)

        for attempt in range(self.max_retries):
            try:
                response = await asyncio.wait_for(self.generate_content(prompt), timeout=timeout)
                return response

            except asyncio.TimeoutError:
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(2**attempt)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(2**attempt)

        raise Exception("Toutes les tentatives ont échoué")


class GeminiProvider(AIProvider):
    """Provider pour Google Gemini"""

    def __init__(self, api_key: str, model: str, timeout_seconds: int = 60, max_retries: int = 3):
        super().__init__(api_key, model, timeout_seconds, max_retries)
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(model)

    async def generate_content(self, prompt: str) -> str:
        """Génère du contenu avec Gemini"""
        response = await asyncio.to_thread(self._model.generate_content, prompt)
        return response.text


class OpenAIProvider(AIProvider):
    """Provider pour OpenAI"""

    def __init__(self, api_key: str, model: str, timeout_seconds: int = 60, max_retries: int = 3):
        super().__init__(api_key, model, timeout_seconds, max_retries)
        try:
            from openai import OpenAI

            self._client = OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError(
                "Le package 'openai' est requis pour utiliser OpenAI. "
                "Installez-le avec: pip install openai"
            )

    async def generate_content(self, prompt: str) -> str:
        """Génère du contenu avec OpenAI"""
        response = await asyncio.to_thread(
            self._client.chat.completions.create,
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            timeout=self.timeout_seconds,
        )
        return response.choices[0].message.content

    async def generate_content_with_reasoning(self, prompt: str) -> Tuple[str, Optional[str]]:
        """Génère du contenu avec reasoning pour les modèles o1"""
        # Les modèles o1 (o1-preview, o1-mini) ont un reasoning
        if self.model.startswith("o1"):
            response = await asyncio.to_thread(
                self._client.chat.completions.create,
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                timeout=self.timeout_seconds,
            )
            content = response.choices[0].message.content
            # Le reasoning est dans response.choices[0].message.reasoning si disponible
            reasoning = getattr(response.choices[0].message, "reasoning", None)
            return content, reasoning
        else:
            # Pour les autres modèles, pas de reasoning
            content = await self.generate_content(prompt)
            return content, None


class ClaudeProvider(AIProvider):
    """Provider pour Anthropic Claude"""

    def __init__(self, api_key: str, model: str, timeout_seconds: int = 60, max_retries: int = 3):
        super().__init__(api_key, model, timeout_seconds, max_retries)
        try:
            from anthropic import Anthropic

            self._client = Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError(
                "Le package 'anthropic' est requis pour utiliser Claude. "
                "Installez-le avec: pip install anthropic"
            )

    async def generate_content(self, prompt: str) -> str:
        """Génère du contenu avec Claude"""
        response = await asyncio.to_thread(
            self._client.messages.create,
            model=self.model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
            timeout=self.timeout_seconds,
        )
        return response.content[0].text

    async def generate_content_with_reasoning(self, prompt: str) -> Tuple[str, Optional[str]]:
        """Génère du contenu avec reasoning pour Claude (si disponible)"""
        # Claude peut avoir un reasoning dans certains modèles, mais l'API actuelle ne l'expose pas directement
        # On retourne None pour le reasoning pour l'instant
        content = await self.generate_content(prompt)
        return content, None


def create_ai_provider(
    provider: str, api_key: str, model: str, timeout_seconds: int = 60, max_retries: int = 3
) -> AIProvider:
    """
    Crée une instance de provider AI selon le type spécifié

    Args:
        provider: Type de provider ("gemini", "openai", "claude")
        api_key: Clé API du provider
        model: Nom du modèle à utiliser
        timeout_seconds: Timeout en secondes
        max_retries: Nombre maximum de tentatives

    Returns:
        Instance de AIProvider

    Raises:
        ValueError: Si le provider n'est pas reconnu
        ImportError: Si les dépendances nécessaires ne sont pas installées
    """
    provider = provider.lower()

    if provider == "gemini":
        return GeminiProvider(api_key, model, timeout_seconds, max_retries)
    elif provider == "openai":
        return OpenAIProvider(api_key, model, timeout_seconds, max_retries)
    elif provider == "claude":
        return ClaudeProvider(api_key, model, timeout_seconds, max_retries)
    else:
        raise ValueError(
            f"Provider '{provider}' non reconnu. "
            "Valeurs supportées: 'gemini', 'openai', 'claude'"
        )
