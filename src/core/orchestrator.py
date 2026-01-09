"""
Orchestrateur principal pour coordonner les agents d'analyse
Sépare la logique d'orchestration de la logique métier
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from src.core.config import AnalysisConfig
from src.core.error_handler import classify_error, exponential_backoff
from src.core.heartbeat import HeartbeatMonitor
from src.core.logger import log_print
from src.core.metrics import MetricsCollector
from src.core.progress import ProgressManager
from src.models.data_models import FileAnalysis


class WorkflowStage(Enum):
    """Étapes du workflow d'analyse"""

    INIT = "init"
    SCAN = "scan"
    DEPENDENCY_INIT = "dependency_init"
    FILE_ANALYSIS = "file_analysis"
    EXPORT_ANALYSIS = "export_analysis"  # Extraction des exports
    REVERSE_DEPENDENCY = "reverse_dependency"  # Construction du graphe inverse
    IMPACT_ANALYSIS = "impact_analysis"  # Analyse d'impact des bugs
    DEPENDENCY_ANALYSIS = "dependency_analysis"
    ARCHITECTURE_REPORT = "architecture_report"
    VULNERABILITY_ANALYSIS = "vulnerability_analysis"
    QUALITY_REPORT = "quality_report"
    USER_STORY_ANALYSIS = "user_story_analysis"  # Analyse des flux user stories
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class WorkflowContext:
    """Contexte partagé entre les étapes du workflow"""

    config: AnalysisConfig
    files: List[str] = field(default_factory=list)
    analyses: List[FileAnalysis] = field(default_factory=list)
    cycles: List[List[str]] = field(default_factory=list)
    vulnerabilities: List[Any] = field(default_factory=list)
    architecture_report: str = ""
    quality_report: str = ""
    user_story_result: Optional[Any] = None  # Résultat de l'analyse user story
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


@dataclass
class WorkflowStep:
    """Étape du workflow"""

    stage: WorkflowStage
    name: str
    handler: Callable
    dependencies: List[WorkflowStage] = field(default_factory=list)
    parallelizable: bool = False
    retryable: bool = True
    critical: bool = True  # Si False, une erreur n'arrête pas le workflow


class AnalysisOrchestrator:
    """Orchestrateur pour coordonner les agents d'analyse"""

    def __init__(
        self,
        config: AnalysisConfig,
        progress_manager: Optional[ProgressManager] = None,
        metrics_collector: Optional[MetricsCollector] = None,
    ):
        self.config = config
        self.progress_manager = progress_manager or ProgressManager(enabled=False)
        self.metrics_collector = metrics_collector
        self.context = WorkflowContext(config=config)
        self.steps: List[WorkflowStep] = []
        self.hooks: Dict[WorkflowStage, List[Callable]] = {}
        self.current_stage: Optional[WorkflowStage] = None

        # Heartbeat monitor for long-running operations (v2.6.1)
        self.heartbeat_monitor = HeartbeatMonitor(interval_seconds=config.heartbeat_interval)

    def register_step(
        self,
        stage: WorkflowStage,
        name: str,
        handler: Callable,
        dependencies: Optional[List[WorkflowStage]] = None,
        parallelizable: bool = False,
        retryable: bool = True,
        critical: bool = True,
    ):
        """Enregistre une étape du workflow"""
        step = WorkflowStep(
            stage=stage,
            name=name,
            handler=handler,
            dependencies=dependencies or [],
            parallelizable=parallelizable,
            retryable=retryable,
            critical=critical,
        )
        self.steps.append(step)

    def register_hook(self, stage: WorkflowStage, hook: Callable):
        """Enregistre un hook pour une étape donnée"""
        if stage not in self.hooks:
            self.hooks[stage] = []
        self.hooks[stage].append(hook)

    async def _execute_hooks(self, stage: WorkflowStage, context: WorkflowContext):
        """Exécute les hooks pour une étape donnée"""
        if stage in self.hooks:
            for hook in self.hooks[stage]:
                try:
                    await hook(context) if asyncio.iscoroutinefunction(hook) else hook(context)
                except Exception as e:
                    log_print(f"⚠️  Erreur dans le hook {stage.value}: {e}")

    def _get_execution_order(self) -> List[WorkflowStep]:
        """Détermine l'ordre d'exécution des étapes en respectant les dépendances"""
        # Topological sort simple
        executed = set()
        order = []
        remaining = {step.stage: step for step in self.steps}

        while remaining:
            # Trouver les étapes sans dépendances non exécutées
            ready = [
                step
                for step in remaining.values()
                if all(dep in executed for dep in step.dependencies)
            ]

            if not ready:
                # Cycle détecté ou dépendance manquante
                remaining_stages = [s.stage.value for s in remaining.values()]
                log_print(
                    f"⚠️  Impossible de résoudre l'ordre d'exécution. Étapes restantes: {remaining_stages}"
                )
                # Forcer l'exécution des étapes restantes
                ready = list(remaining.values())

            for step in ready:
                order.append(step)
                executed.add(step.stage)
                del remaining[step.stage]

        return order

    async def _execute_step(self, step: WorkflowStep) -> bool:
        """Exécute une étape du workflow"""
        self.current_stage = step.stage
        log_print(f"🔄 Étape: {step.name} ({step.stage.value})")

        # Démarrer le suivi des métriques
        if self.metrics_collector:
            self.metrics_collector.start_step(step.name)

        try:
            # Exécuter les hooks avant
            await self._execute_hooks(step.stage, self.context)

            # Exécuter l'étape
            if asyncio.iscoroutinefunction(step.handler):
                await step.handler(self.context)
            else:
                step.handler(self.context)

            # Exécuter les hooks après
            await self._execute_hooks(step.stage, self.context)

            # Enregistrer le succès
            if self.metrics_collector:
                self.metrics_collector.end_step(success=True)

            return True
        except Exception as e:
            error_msg = f"Erreur dans l'étape {step.name}: {str(e)}"
            log_print(f"❌ {error_msg}")
            self.context.errors.append(error_msg)

            # Enregistrer l'échec dans les métriques
            if self.metrics_collector:
                self.metrics_collector.end_step(success=False, error=error_msg)

            if step.critical:
                if step.retryable:
                    error_type = classify_error(e)
                    log_print(
                        f"🔄 Tentative de retry pour {step.name} (type: {error_type.value})..."
                    )

                    try:
                        # Utiliser backoff exponentiel pour le retry
                        async def _retry_handler():
                            if asyncio.iscoroutinefunction(step.handler):
                                return await step.handler(self.context)
                            else:
                                return step.handler(self.context)

                        await exponential_backoff(
                            _retry_handler,
                            max_retries=1,  # Un seul retry supplémentaire
                            initial_delay=2.0,
                            max_delay=30.0,
                            multiplier=2.0,
                        )
                        return True
                    except Exception as retry_error:
                        error_type_retry = classify_error(retry_error)
                        log_print(f"❌ Retry échoué ({error_type_retry.value}): {retry_error}")
                        return False
                else:
                    return False
            else:
                # Étape non critique, continuer
                log_print("⚠️  Étape non critique échouée, continuation...")
                return True

    async def _execute_workflow_steps(self) -> None:
        """Execute all workflow steps in order (internal method)."""
        execution_order = self._get_execution_order()

        # Grouper les étapes parallélisables
        sequential_groups: List[List[WorkflowStep]] = []
        current_parallel: List[WorkflowStep] = []

        for step in execution_order:
            if step.parallelizable and current_parallel:
                current_parallel.append(step)
            else:
                if current_parallel:
                    sequential_groups.append(current_parallel)
                if step.parallelizable:
                    current_parallel = [step]
                else:
                    sequential_groups.append([step])
                    current_parallel = []

        if current_parallel:
            sequential_groups.append(current_parallel)

        # Exécuter les groupes
        for group in sequential_groups:
            if len(group) == 1:
                # Exécution séquentielle
                success = await self._execute_step(group[0])
                if not success and group[0].critical:
                    self.context.metadata["failed_at"] = group[0].stage.value
                    break
            else:
                # Exécution parallèle
                tasks = [self._execute_step(step) for step in group]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                # Vérifier si des étapes critiques ont échoué
                for step, result in zip(group, results):
                    if isinstance(result, Exception) or (not result and step.critical):
                        log_print(f"❌ Étape critique {step.name} a échoué")
                        self.context.metadata["failed_at"] = step.stage.value
                        break

    async def execute(self) -> WorkflowContext:
        """Exécute le workflow complet avec timeout et heartbeat (v2.6.1)"""
        self.context.start_time = datetime.now()
        workflow_id = f"wf_{datetime.now().timestamp()}"
        self.context.metadata["workflow_id"] = workflow_id

        # Get timeout configuration
        timeout_config = self.config.timeout_config
        timeout_seconds = (
            timeout_config.value if timeout_config and timeout_config.enabled else None
        )

        # Log timeout info
        if timeout_seconds and timeout_config is not None:
            log_print(f"⏱️  Timeout global: {timeout_config.format_human()}")
        else:
            log_print("⏱️  Timeout: illimité")

        # Démarrer la session de métriques
        if self.metrics_collector:
            self.metrics_collector.start_session(workflow_id)

        # Start heartbeat monitor (v2.6.1)
        await self.heartbeat_monitor.start()

        try:
            # Execute workflow with optional timeout (v2.6.1)
            if timeout_seconds:
                try:
                    await asyncio.wait_for(self._execute_workflow_steps(), timeout=timeout_seconds)
                except asyncio.TimeoutError:
                    self.current_stage = WorkflowStage.ERROR
                    elapsed = self.heartbeat_monitor.elapsed_seconds
                    # timeout_config is guaranteed to be not None when timeout_seconds is set
                    timeout_str = (
                        timeout_config.format_human() if timeout_config else f"{timeout_seconds}s"
                    )
                    error_msg = (
                        f"Analyse interrompue: timeout de {timeout_str} "
                        f"atteint après {elapsed:.0f}s"
                    )
                    self.context.errors.append(error_msg)
                    self.context.metadata["timeout_reached"] = True
                    self.context.metadata["timeout_value"] = timeout_seconds
                    log_print(f"\n⏰ {error_msg}")
                    log_print(
                        "💡 Utilisez --timeout pour augmenter le délai ou --timeout 0 pour illimité"
                    )
            else:
                # No timeout (unlimited)
                await self._execute_workflow_steps()

            # Mark complete if no timeout occurred
            if self.current_stage != WorkflowStage.ERROR:
                self.current_stage = WorkflowStage.COMPLETE

            self.context.end_time = datetime.now()

            if self.context.start_time and self.context.end_time:
                duration = (self.context.end_time - self.context.start_time).total_seconds()
                self.context.metadata["duration_seconds"] = duration
                if self.current_stage == WorkflowStage.COMPLETE:
                    log_print(f"\n🎉 Workflow terminé avec succès en {duration:.2f}s")
                    log_print("📁 Les rapports ont été générés dans le dossier de sortie.")

            # Terminer la session de métriques
            if self.metrics_collector:
                metrics_file = self.metrics_collector.end_session(self.context.metadata)
                if metrics_file:
                    log_print(f"📊 Métriques sauvegardées: {metrics_file}")

        except Exception as e:
            self.current_stage = WorkflowStage.ERROR
            self.context.errors.append(f"Erreur fatale: {str(e)}")
            self.context.end_time = datetime.now()
            log_print(f"❌ Erreur fatale dans le workflow: {e}")

        finally:
            # Stop heartbeat monitor (v2.6.1)
            await self.heartbeat_monitor.stop()

        return self.context

    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut actuel du workflow"""
        return {
            "current_stage": self.current_stage.value if self.current_stage else None,
            "files_count": len(self.context.files),
            "analyses_count": len(self.context.analyses),
            "errors_count": len(self.context.errors),
            "start_time": self.context.start_time.isoformat() if self.context.start_time else None,
            "end_time": self.context.end_time.isoformat() if self.context.end_time else None,
        }
