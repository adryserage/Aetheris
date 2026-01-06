"""
Collecteur de métriques pour le système d'analyse
Collecte les performances, taux de succès, coûts API, etc.
"""

import json
import os
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional


@dataclass
class StepMetrics:
    """Métriques pour une étape du workflow"""

    step_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    success: bool = False
    error: Optional[str] = None
    files_processed: int = 0
    files_cached: int = 0
    api_calls: int = 0
    estimated_tokens: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentMetrics:
    """Métriques pour un agent"""

    agent_name: str
    calls: int = 0
    successes: int = 0
    failures: int = 0
    total_duration_seconds: float = 0.0
    average_duration_seconds: float = 0.0
    estimated_tokens: int = 0


@dataclass
class SessionMetrics:
    """Métriques pour une session d'analyse complète"""

    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_duration_seconds: float = 0.0
    files_analyzed: int = 0
    files_cached: int = 0
    files_failed: int = 0
    steps: List[StepMetrics] = field(default_factory=list)
    agents: Dict[str, AgentMetrics] = field(default_factory=dict)
    total_api_calls: int = 0
    total_estimated_tokens: int = 0
    cache_hit_rate: float = 0.0
    success_rate: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class MetricsCollector:
    """Collecteur de métriques pour le système d'analyse"""

    def __init__(self, output_dir: str = "docs/metrics", enabled: bool = True):
        """
        Initialise le collecteur de métriques

        Args:
            output_dir: Répertoire de sortie pour les métriques
            enabled: Activer ou désactiver la collecte
        """
        self.enabled = enabled
        self.output_dir = output_dir
        self.current_session: Optional[SessionMetrics] = None
        self.current_step: Optional[StepMetrics] = None
        self.agent_metrics: Dict[str, AgentMetrics] = {}

        if enabled:
            os.makedirs(output_dir, exist_ok=True)

    def start_session(self, session_id: Optional[str] = None) -> str:
        """
        Démarre une nouvelle session de métriques

        Args:
            session_id: ID de session (généré si None)

        Returns:
            ID de la session
        """
        if not self.enabled:
            return ""

        if session_id is None:
            session_id = f"session_{datetime.now().timestamp()}"

        self.current_session = SessionMetrics(
            session_id=session_id,
            start_time=datetime.now(),
        )

        return session_id

    def start_step(self, step_name: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Démarre le suivi d'une étape

        Args:
            step_name: Nom de l'étape
            metadata: Métadonnées optionnelles
        """
        if not self.enabled or not self.current_session:
            return

        self.current_step = StepMetrics(
            step_name=step_name,
            start_time=datetime.now(),
            metadata=metadata or {},
        )

    def end_step(
        self,
        success: bool = True,
        error: Optional[str] = None,
        files_processed: int = 0,
        files_cached: int = 0,
        api_calls: int = 0,
        estimated_tokens: int = 0,
    ):
        """
        Termine le suivi d'une étape

        Args:
            success: Si l'étape a réussi
            error: Message d'erreur si échec
            files_processed: Nombre de fichiers traités
            files_cached: Nombre de fichiers récupérés du cache
            api_calls: Nombre d'appels API
            estimated_tokens: Nombre estimé de tokens utilisés
        """
        if not self.enabled or not self.current_session or not self.current_step:
            return

        self.current_step.end_time = datetime.now()
        self.current_step.duration_seconds = (
            self.current_step.end_time - self.current_step.start_time
        ).total_seconds()
        self.current_step.success = success
        self.current_step.error = error
        self.current_step.files_processed = files_processed
        self.current_step.files_cached = files_cached
        self.current_step.api_calls = api_calls
        self.current_step.estimated_tokens = estimated_tokens

        if self.current_session:
            self.current_session.steps.append(self.current_step)

        self.current_step = None

    def record_agent_call(
        self,
        agent_name: str,
        success: bool,
        duration_seconds: float,
        estimated_tokens: int = 0,
    ):
        """
        Enregistre un appel d'agent

        Args:
            agent_name: Nom de l'agent
            success: Si l'appel a réussi
            duration_seconds: Durée de l'appel
            estimated_tokens: Nombre estimé de tokens
        """
        if not self.enabled:
            return

        if agent_name not in self.agent_metrics:
            self.agent_metrics[agent_name] = AgentMetrics(agent_name=agent_name)

        metrics = self.agent_metrics[agent_name]
        metrics.calls += 1
        if success:
            metrics.successes += 1
        else:
            metrics.failures += 1
        metrics.total_duration_seconds += duration_seconds
        metrics.average_duration_seconds = metrics.total_duration_seconds / metrics.calls
        metrics.estimated_tokens += estimated_tokens

        if self.current_session:
            self.current_session.agents[agent_name] = metrics

    def end_session(self, metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Termine la session et sauvegarde les métriques

        Args:
            metadata: Métadonnées optionnelles

        Returns:
            Chemin du fichier de métriques sauvegardé
        """
        if not self.enabled or not self.current_session:
            return None

        self.current_session.end_time = datetime.now()
        self.current_session.total_duration_seconds = (
            self.current_session.end_time - self.current_session.start_time
        ).total_seconds()

        # Calculer les statistiques agrégées
        total_files = sum(step.files_processed for step in self.current_session.steps)
        total_cached = sum(step.files_cached for step in self.current_session.steps)
        total_failed = sum(1 for step in self.current_session.steps if not step.success)

        self.current_session.files_analyzed = total_files
        self.current_session.files_cached = total_cached
        self.current_session.files_failed = total_failed
        self.current_session.total_api_calls = sum(
            step.api_calls for step in self.current_session.steps
        )
        self.current_session.total_estimated_tokens = sum(
            step.estimated_tokens for step in self.current_session.steps
        )

        if total_files > 0:
            self.current_session.cache_hit_rate = total_cached / (total_files + total_cached)
            self.current_session.success_rate = (
                (total_files - total_failed) / total_files if total_files > 0 else 0.0
            )

        if metadata:
            self.current_session.metadata.update(metadata)

        # Sauvegarder les métriques
        return self._save_metrics()

    def _save_metrics(self) -> str:
        """Sauvegarde les métriques dans un fichier JSON"""
        if not self.current_session:
            return ""

        # Convertir en dict pour JSON
        metrics_dict = {
            "session_id": self.current_session.session_id,
            "start_time": self.current_session.start_time.isoformat(),
            "end_time": (
                self.current_session.end_time.isoformat() if self.current_session.end_time else None
            ),
            "total_duration_seconds": self.current_session.total_duration_seconds,
            "files_analyzed": self.current_session.files_analyzed,
            "files_cached": self.current_session.files_cached,
            "files_failed": self.current_session.files_failed,
            "total_api_calls": self.current_session.total_api_calls,
            "total_estimated_tokens": self.current_session.total_estimated_tokens,
            "cache_hit_rate": self.current_session.cache_hit_rate,
            "success_rate": self.current_session.success_rate,
            "steps": [
                {
                    "step_name": step.step_name,
                    "start_time": step.start_time.isoformat(),
                    "end_time": (step.end_time.isoformat() if step.end_time else None),
                    "duration_seconds": step.duration_seconds,
                    "success": step.success,
                    "error": step.error,
                    "files_processed": step.files_processed,
                    "files_cached": step.files_cached,
                    "api_calls": step.api_calls,
                    "estimated_tokens": step.estimated_tokens,
                    "metadata": step.metadata,
                }
                for step in self.current_session.steps
            ],
            "agents": {
                name: {
                    "calls": agent.calls,
                    "successes": agent.successes,
                    "failures": agent.failures,
                    "total_duration_seconds": agent.total_duration_seconds,
                    "average_duration_seconds": agent.average_duration_seconds,
                    "estimated_tokens": agent.estimated_tokens,
                }
                for name, agent in self.current_session.agents.items()
            },
            "metadata": self.current_session.metadata,
        }

        # Nom du fichier basé sur le timestamp
        timestamp = self.current_session.start_time.strftime("%Y%m%d_%H%M%S")
        filename = f"metrics_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(metrics_dict, f, indent=2, ensure_ascii=False)

        return filepath
