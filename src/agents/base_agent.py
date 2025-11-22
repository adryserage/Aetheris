"""
Classe de base pour tous les agents d'analyse
"""

import asyncio
from typing import Optional
import google.generativeai as genai
from src.core.config import AnalysisConfig


class BaseAgent:
    """Classe de base pour tous les agents d'analyse avec logique commune"""
    
    def __init__(self, config: AnalysisConfig):
        self.config = config
        genai.configure(api_key=config.gemini_api_key)
        self.model = genai.GenerativeModel(config.gemini_model)
    
    async def _call_gemini_with_retry(self, prompt: str, timeout_multiplier: float = 1.0) -> str:
        """
        Appelle l'API Gemini avec retry et gestion des timeouts
        
        Args:
            prompt: Le prompt à envoyer à Gemini
            timeout_multiplier: Multiplicateur pour le timeout (défaut: 1.0)
        
        Returns:
            Le texte de la réponse de Gemini
        
        Raises:
            Exception: Si toutes les tentatives échouent
        """
        timeout = int(self.config.timeout_seconds * timeout_multiplier)
        
        for attempt in range(self.config.max_retries):
            try:
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        self.model.generate_content,
                        prompt
                    ),
                    timeout=timeout
                )
                return response.text
                
            except asyncio.TimeoutError:
                if attempt == self.config.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
            except Exception as e:
                if attempt == self.config.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
        
        raise Exception("Toutes les tentatives ont échoué")

