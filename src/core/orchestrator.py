"""
Orchestrateur principal pour coordonner les agents d'analyse
Sépare la logique d'orchestration de la logique métier
"""

import asyncio
from enum import Enum
from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime

from src.core.config import AnalysisConfig
from src.core.logger import log_print
from src.core.progress import ProgressManager
from src.models.data_models import FileAnalysis


class WorkflowStage(Enum):
    """Étapes du workflow d'analyse"""
    INIT = "init"
    SCAN = "scan"
    DEPENDENCY_INIT = "dependency_init"
    FILE_ANALYSIS = "file_analysis"
    DEPENDENCY_ANALYSIS = "dependency_analysis"
    ARCHITECTURE_REPORT = "architecture_report"
    VULNERABILITY_ANALYSIS = "vulnerability_analysis"
    QUALITY_REPORT = "quality_report"
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
    ):
        self.config = config
        self.progress_manager = progress_manager or ProgressManager(enabled=False)
        self.context = WorkflowContext(config=config)
        self.steps: List[WorkflowStep] = []
        self.hooks: Dict[WorkflowStage, List[Callable]] = {}
        self.current_stage: Optional[WorkflowStage] = None

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
                log_print(f"⚠️  Impossible de résoudre l'ordre d'exécution. Étapes restantes: {remaining_stages}")
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

        try:
            # Exécuter les hooks avant
            await self._execute_hooks(step.stage, self.context)

            # Exécuter l'étape
            if asyncio.iscoroutinefunction(step.handler):
                result = await step.handler(self.context)
            else:
                result = step.handler(self.context)

            # Exécuter les hooks après
            await self._execute_hooks(step.stage, self.context)

            return True
        except Exception as e:
            error_msg = f"Erreur dans l'étape {step.name}: {str(e)}"
            log_print(f"❌ {error_msg}")
            self.context.errors.append(error_msg)

            if step.critical:
                if step.retryable:
                    log_print(f"🔄 Tentative de retry pour {step.name}...")
                    try:
                        if asyncio.iscoroutinefunction(step.handler):
                            await step.handler(self.context)
                        else:
                            step.handler(self.context)
                        return True
                    except Exception as retry_error:
                        log_print(f"❌ Retry échoué: {retry_error}")
                        return False
                else:
                    return False
            else:
                # Étape non critique, continuer
                log_print(f"⚠️  Étape non critique échouée, continuation...")
                return True

    async def execute(self) -> WorkflowContext:
        """Exécute le workflow complet"""
        self.context.start_time = datetime.now()
        self.context.metadata["workflow_id"] = f"wf_{datetime.now().timestamp()}"

        try:
            execution_order = self._get_execution_order()

            # Grouper les étapes parallélisables
            sequential_groups = []
            current_parallel = []

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

            self.current_stage = WorkflowStage.COMPLETE
            self.context.end_time = datetime.now()

            if self.context.start_time and self.context.end_time:
                duration = (self.context.end_time - self.context.start_time).total_seconds()
                self.context.metadata["duration_seconds"] = duration
                log_print(f"✅ Workflow terminé en {duration:.2f}s")

        except Exception as e:
            self.current_stage = WorkflowStage.ERROR
            self.context.errors.append(f"Erreur fatale: {str(e)}")
            self.context.end_time = datetime.now()
            log_print(f"❌ Erreur fatale dans le workflow: {e}")

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

