"""
Gestion d'erreurs améliorée avec circuit breaker et backoff exponentiel
"""

import asyncio
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
from typing import Any
from typing import Callable
from typing import Optional


class ErrorType(Enum):
    """Types d'erreurs"""

    TEMPORARY = "temporary"  # Erreur temporaire (rate limit, timeout)
    PERMANENT = "permanent"  # Erreur permanente (invalid API key, 404)
    CRITICAL = "critical"  # Erreur critique (système down)


class CircuitState(Enum):
    """États du circuit breaker"""

    CLOSED = "closed"  # Normal, toutes les requêtes passent
    OPEN = "open"  # Circuit ouvert, rejette toutes les requêtes
    HALF_OPEN = "half_open"  # Teste si le service est revenu


@dataclass
class CircuitBreaker:
    """Circuit breaker pour éviter les appels répétés en cas d'erreur"""

    failure_threshold: int = 5  # Nombre d'échecs avant ouverture
    success_threshold: int = 2  # Nombre de succès pour fermer
    timeout_seconds: int = 60  # Temps avant tentative de réouverture
    failures: int = field(default=0)
    successes: int = field(default=0)
    state: CircuitState = field(default=CircuitState.CLOSED)
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None

    def record_success(self):
        """Enregistre un succès"""
        self.successes += 1
        self.last_success_time = datetime.now()

        if self.state == CircuitState.HALF_OPEN:
            if self.successes >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.failures = 0
                self.successes = 0

    def record_failure(self):
        """Enregistre un échec"""
        self.failures += 1
        self.last_failure_time = datetime.now()
        self.successes = 0

        if self.failures >= self.failure_threshold:
            self.state = CircuitState.OPEN

    def can_execute(self) -> bool:
        """Vérifie si une requête peut être exécutée"""
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            # Vérifier si on peut passer en HALF_OPEN
            if self.last_failure_time:
                elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                if elapsed >= self.timeout_seconds:
                    self.state = CircuitState.HALF_OPEN
                    self.failures = 0
                    return True
            return False

        # HALF_OPEN : permettre quelques tentatives
        return True

    def reset(self):
        """Réinitialise le circuit breaker"""
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.successes = 0
        self.last_failure_time = None
        self.last_success_time = None


def classify_error(error: Exception) -> ErrorType:
    """
    Classifie une erreur selon son type

    Args:
        error: L'exception à classifier

    Returns:
        Le type d'erreur
    """
    error_str = str(error).lower()
    type(error).__name__

    # Erreurs temporaires
    if any(
        keyword in error_str
        for keyword in [
            "timeout",
            "rate limit",
            "too many requests",
            "service unavailable",
            "temporary",
            "retry",
        ]
    ):
        return ErrorType.TEMPORARY

    # Erreurs permanentes
    if any(
        keyword in error_str
        for keyword in [
            "not found",
            "404",
            "invalid",
            "unauthorized",
            "forbidden",
            "authentication",
        ]
    ):
        return ErrorType.PERMANENT

    # Erreurs critiques
    if any(
        keyword in error_str
        for keyword in [
            "connection",
            "network",
            "dns",
            "refused",
        ]
    ):
        return ErrorType.CRITICAL

    # Par défaut, considérer comme temporaire
    return ErrorType.TEMPORARY


async def exponential_backoff(
    func: Callable,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    multiplier: float = 2.0,
    circuit_breaker: Optional[CircuitBreaker] = None,
) -> Any:
    """
    Exécute une fonction avec backoff exponentiel et circuit breaker

    Args:
        func: Fonction à exécuter (peut être async)
        max_retries: Nombre maximum de tentatives
        initial_delay: Délai initial en secondes
        max_delay: Délai maximum en secondes
        multiplier: Multiplicateur pour le délai
        circuit_breaker: Circuit breaker optionnel

    Returns:
        Résultat de la fonction

    Raises:
        Exception: Si toutes les tentatives échouent
    """
    delay = initial_delay
    last_error = None

    for attempt in range(max_retries + 1):
        # Vérifier le circuit breaker
        if circuit_breaker and not circuit_breaker.can_execute():
            raise Exception(
                f"Circuit breaker is OPEN. Last failure: {circuit_breaker.last_failure_time}"
            )

        try:
            # Exécuter la fonction
            if asyncio.iscoroutinefunction(func):
                result = await func()
            else:
                result = func()

            # Enregistrer le succès
            if circuit_breaker:
                circuit_breaker.record_success()

            return result

        except Exception as e:
            last_error = e
            error_type = classify_error(e)

            # Enregistrer l'échec
            if circuit_breaker:
                circuit_breaker.record_failure()

            # Ne pas retry pour les erreurs permanentes
            if error_type == ErrorType.PERMANENT:
                raise e

            # Dernière tentative, lever l'erreur
            if attempt == max_retries:
                raise e

            # Attendre avant de retry
            await asyncio.sleep(min(delay, max_delay))
            delay *= multiplier

    # Ne devrait jamais arriver ici
    raise last_error if last_error else Exception("Unknown error")
