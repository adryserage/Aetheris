"""
UserStoryAnalysisAgent

Agent IA pour l'analyse des flux de user stories.
Trace les flux frontend ↔ backend et détecte les incohérences logiques.
"""

import os
import uuid
from datetime import datetime
from typing import List, Optional, Tuple, TYPE_CHECKING

from .base_agent import BaseAgent
from ..core.config import AnalysisConfig
from ..core.progress import ProgressManager
from ..models.user_story_models import (
    UserStory,
    UserStoryFlow,
    UserStoryAnalysisResult,
    FlowStep,
    FlowIssue,
    APICall,
    APIEndpoint,
    IssueSeverity,
    IssueType,
    FlowStepType,
)
from ..models.user_story_schemas import (
    FlowAnalysisSchema,
    ConsistencyCheckSchema,
    UserStoryAnalysisSchema,
)
from ..services.flow_tracer import FlowTracer, FlowTracerResult
from ..services.user_story_parser import UserStoryParser

if TYPE_CHECKING:
    from ..models.data_models import FileAnalysis


class UserStoryAnalysisAgent(BaseAgent):
    """
    Agent pour l'analyse des user stories

    Analyse les flux utilisateur en traçant les appels API,
    les handlers backend, et en détectant les incohérences.
    """

    def __init__(
        self,
        config: AnalysisConfig,
        root_dir: str,
        all_files: List[str],
        progress_manager: Optional[ProgressManager] = None,
    ):
        super().__init__(config, progress_manager)
        self.root_dir = root_dir
        self.all_files = all_files
        self.flow_tracer = FlowTracer(root_dir, all_files)
        self.user_story_parser = UserStoryParser(root_dir, all_files)
        self._file_cache: dict = {}

    def _read_file(self, file_path: str) -> Optional[str]:
        """Lit un fichier et le met en cache"""
        if file_path in self._file_cache:
            return self._file_cache[file_path]

        try:
            full_path = os.path.join(self.root_dir, file_path)
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                self._file_cache[file_path] = content
                return content
        except Exception:
            return None

    async def analyze_user_story(
        self,
        user_story: UserStory,
        file_analyses: Optional[List["FileAnalysis"]] = None,
    ) -> UserStoryFlow:
        """
        Analyse une user story complète

        Args:
            user_story: La user story à analyser
            file_analyses: Analyses de fichiers existantes (optionnel)

        Returns:
            UserStoryFlow avec les étapes et problèmes détectés
        """
        # Créer le flow
        flow = UserStoryFlow(
            id=f"FLOW-{uuid.uuid4().hex[:8].upper()}",
            story=user_story,
            title=user_story.title,
            entry_point=user_story.entry_point_file or "",
        )

        # Détecter le point d'entrée si non fourni
        if not flow.entry_point:
            entry = self.user_story_parser.detect_entry_point(user_story)
            if entry:
                flow.entry_point = entry

        # Tracer les appels API depuis le point d'entrée
        if flow.entry_point:
            api_calls = self.flow_tracer.detect_api_calls_in_file(flow.entry_point)
            flow.api_calls = api_calls

            # Pour chaque appel, trouver l'endpoint correspondant
            tracer_result = self.flow_tracer.trace_all_files()
            for call in api_calls:
                for endpoint in tracer_result.api_endpoints:
                    if self._call_matches_endpoint(call, endpoint):
                        call.matched_endpoint = endpoint.path
                        if endpoint not in flow.api_endpoints:
                            flow.api_endpoints.append(endpoint)

        # Analyser le flux avec l'IA
        flow = await self._analyze_flow_with_ai(flow, file_analyses)

        # Détecter les problèmes
        flow.issues = await self._detect_flow_issues(flow)

        return flow

    def _call_matches_endpoint(self, call: APICall, endpoint: APIEndpoint) -> bool:
        """Vérifie si un appel correspond à un endpoint"""
        # Normaliser les URLs
        call_url = call.url_pattern.lower()
        endpoint_path = endpoint.path.lower()

        # Supprimer les préfixes communs
        for prefix in ["http://", "https://", "localhost", "127.0.0.1"]:
            if prefix in call_url:
                call_url = call_url.split(prefix)[-1]
                if "/" in call_url:
                    call_url = "/" + "/".join(call_url.split("/")[1:])

        # Correspondance basique
        if call_url == endpoint_path:
            return True

        # Correspondance avec paramètres
        if endpoint_path.count("/") == call_url.count("/"):
            ep_parts = endpoint_path.split("/")
            call_parts = call_url.split("/")
            matches = True
            for ep, cp in zip(ep_parts, call_parts):
                if ep.startswith(":") or ep.startswith("{"):
                    continue
                if "${" in cp or cp.startswith(":"):
                    continue
                if ep != cp:
                    matches = False
                    break
            if matches:
                return True

        return False

    async def _analyze_flow_with_ai(
        self,
        flow: UserStoryFlow,
        file_analyses: Optional[List["FileAnalysis"]] = None,
    ) -> UserStoryFlow:
        """Analyse le flux avec l'IA pour générer les étapes"""
        # Construire le contexte
        context_parts = []

        # Ajouter le contenu du fichier d'entrée
        if flow.entry_point:
            content = self._read_file(flow.entry_point)
            if content:
                context_parts.append(f"## Entry Point: {flow.entry_point}\n```\n{content[:2000]}\n```")

        # Ajouter les infos sur les appels API
        if flow.api_calls:
            api_info = "## API Calls Detected:\n"
            for call in flow.api_calls:
                api_info += f"- {call.method} {call.url_pattern} (line {call.line_number})\n"
            context_parts.append(api_info)

        # Ajouter les endpoints
        if flow.api_endpoints:
            endpoint_info = "## Backend Endpoints:\n"
            for ep in flow.api_endpoints:
                endpoint_info += f"- {ep.method} {ep.path} in {ep.file_path}:{ep.line_number}\n"
                # Ajouter le contenu du handler
                ep_content = self._read_file(ep.file_path)
                if ep_content:
                    endpoint_info += f"```\n{ep_content[:1500]}\n```\n"
            context_parts.append(endpoint_info)

        prompt = f"""Analyse ce flux utilisateur et génère les étapes détaillées.

User Story: {flow.story.title}
Description: {flow.story.description}
Action: {flow.story.action}
Expected Outcome: {flow.story.expected_outcome}

{chr(10).join(context_parts)}

Génère une analyse structurée du flux avec:
1. Les étapes du flux (UI event -> API call -> Backend handler -> Response)
2. Les problèmes potentiels (missing error handling, race conditions, etc.)
3. Les incohérences logiques
4. Les recommandations

Réponds en JSON valide selon ce schéma:
{{
    "title": "string",
    "steps": [{{
        "order": 0,
        "step_type": "ui_event|api_call|backend_handler|response|...",
        "description": "string",
        "file_hint": "optional string",
        "inputs": ["string"],
        "outputs": ["string"]
    }}],
    "issues": [{{
        "severity": "critical|high|medium|low|info",
        "issue_type": "orphan_endpoint|missing_handler|missing_error_handling|...",
        "title": "string",
        "description": "string",
        "affected_steps": [0],
        "recommendation": "string",
        "code_example": "optional string",
        "auto_fixable": false
    }}],
    "is_complete": true,
    "missing_steps": [],
    "summary": "string"
}}
"""

        try:
            result = await self._call_ai_structured(prompt, FlowAnalysisSchema)

            # Convertir les étapes
            for i, step_schema in enumerate(result.steps):
                step = FlowStep(
                    order=step_schema.order,
                    step_type=step_schema.step_type.value if hasattr(step_schema.step_type, 'value') else step_schema.step_type,
                    file_path=step_schema.file_hint or flow.entry_point or "",
                    line_number=0,
                    description=step_schema.description,
                    inputs=step_schema.inputs,
                    outputs=step_schema.outputs,
                )
                flow.steps.append(step)

            # Convertir les issues
            for issue_schema in result.issues:
                issue = FlowIssue(
                    id=f"US-ISSUE-{uuid.uuid4().hex[:8].upper()}",
                    severity=issue_schema.severity.value if hasattr(issue_schema.severity, 'value') else issue_schema.severity,
                    issue_type=issue_schema.issue_type.value if hasattr(issue_schema.issue_type, 'value') else issue_schema.issue_type,
                    title=issue_schema.title,
                    description=issue_schema.description,
                    affected_steps=issue_schema.affected_steps,
                    recommendation=issue_schema.recommendation,
                    code_example=issue_schema.code_example,
                    auto_fixable=issue_schema.auto_fixable,
                )
                flow.issues.append(issue)

            flow.is_complete = result.is_complete
            flow.missing_steps = result.missing_steps

        except Exception as e:
            # Fallback: créer des étapes basiques
            if flow.entry_point:
                flow.steps.append(FlowStep(
                    order=0,
                    step_type=FlowStepType.UI_EVENT.value,
                    file_path=flow.entry_point,
                    line_number=0,
                    description=f"User initiates: {flow.story.action}",
                ))

            for i, call in enumerate(flow.api_calls):
                flow.steps.append(FlowStep(
                    order=i + 1,
                    step_type=FlowStepType.API_CALL.value,
                    file_path=call.file_path,
                    line_number=call.line_number,
                    description=f"{call.method} {call.url_pattern}",
                ))

        return flow

    async def _detect_flow_issues(self, flow: UserStoryFlow) -> List[FlowIssue]:
        """Détecte les problèmes dans un flux"""
        issues = list(flow.issues)  # Commencer avec les issues de l'IA

        # Vérifier la gestion d'erreurs manquante
        for call in flow.api_calls:
            if not call.has_error_handling:
                issue = FlowIssue(
                    id=f"US-ISSUE-{uuid.uuid4().hex[:8].upper()}",
                    severity=IssueSeverity.MEDIUM.value,
                    issue_type=IssueType.MISSING_ERROR_HANDLING.value,
                    title="Missing error handling",
                    description=f"API call at {call.file_path}:{call.line_number} has no error handling",
                    affected_files=[call.file_path],
                    recommendation="Add try/catch or .catch() to handle API errors gracefully",
                )
                issues.append(issue)

        # Vérifier les états de chargement manquants
        for call in flow.api_calls:
            if not call.has_loading_state:
                issue = FlowIssue(
                    id=f"US-ISSUE-{uuid.uuid4().hex[:8].upper()}",
                    severity=IssueSeverity.LOW.value,
                    issue_type=IssueType.MISSING_LOADING_STATE.value,
                    title="Missing loading state",
                    description=f"API call at {call.file_path}:{call.line_number} has no loading indicator",
                    affected_files=[call.file_path],
                    recommendation="Add loading state to improve user experience",
                )
                issues.append(issue)

        # Vérifier les appels sans handler
        for call in flow.api_calls:
            if not call.matched_endpoint:
                issue = FlowIssue(
                    id=f"US-ISSUE-{uuid.uuid4().hex[:8].upper()}",
                    severity=IssueSeverity.HIGH.value,
                    issue_type=IssueType.MISSING_HANDLER.value,
                    title="No matching backend handler",
                    description=f"API call {call.method} {call.url_pattern} has no corresponding backend endpoint",
                    affected_files=[call.file_path],
                    recommendation="Implement the backend endpoint or fix the URL pattern",
                )
                issues.append(issue)

        # Vérifier les endpoints non protégés
        for endpoint in flow.api_endpoints:
            if not endpoint.is_protected and self._should_be_protected(endpoint):
                issue = FlowIssue(
                    id=f"US-ISSUE-{uuid.uuid4().hex[:8].upper()}",
                    severity=IssueSeverity.HIGH.value,
                    issue_type=IssueType.MISSING_AUTH.value,
                    title="Endpoint missing authentication",
                    description=f"Endpoint {endpoint.method} {endpoint.path} should be protected",
                    affected_files=[endpoint.file_path],
                    recommendation="Add authentication middleware to protect this endpoint",
                )
                issues.append(issue)

        return issues

    def _should_be_protected(self, endpoint: APIEndpoint) -> bool:
        """Détermine si un endpoint devrait être protégé"""
        # Endpoints qui devraient être protégés
        sensitive_patterns = [
            "/user", "/profile", "/account", "/settings",
            "/admin", "/dashboard", "/order", "/payment",
            "/cart", "/checkout", "/private", "/api/me"
        ]

        # Méthodes sensibles
        sensitive_methods = ["POST", "PUT", "PATCH", "DELETE"]

        path_lower = endpoint.path.lower()
        for pattern in sensitive_patterns:
            if pattern in path_lower:
                return True

        if endpoint.method in sensitive_methods:
            # Les méthodes de modification devraient généralement être protégées
            # sauf pour login/register
            public_paths = ["/login", "/register", "/signup", "/signin", "/auth", "/public"]
            if not any(pub in path_lower for pub in public_paths):
                return True

        return False

    async def analyze_all_flows(
        self,
        input_mode: str,
        input_value: str,
        file_analyses: Optional[List["FileAnalysis"]] = None,
    ) -> UserStoryAnalysisResult:
        """
        Analyse tous les flux selon le mode d'entrée

        Args:
            input_mode: 'text', 'file', 'entry', 'auto'
            input_value: La valeur correspondante
            file_analyses: Analyses de fichiers existantes

        Returns:
            UserStoryAnalysisResult complet
        """
        result = UserStoryAnalysisResult(
            analysis_id=f"USA-{uuid.uuid4().hex[:8].upper()}",
            timestamp=datetime.now().isoformat(),
            project_root=self.root_dir,
        )

        # Parser les user stories selon le mode
        user_stories: List[UserStory] = []

        if input_mode == "text":
            user_stories = self.user_story_parser.parse_text(input_value)
        elif input_mode == "file":
            user_stories = self.user_story_parser.parse_markdown(input_value)
        elif input_mode == "entry":
            user_stories = self.user_story_parser.parse_from_code_entry(input_value)
        elif input_mode == "auto":
            user_stories = self.user_story_parser.auto_detect_flows()

        # Analyser chaque user story
        for story in user_stories:
            if self.progress_manager:
                self.progress_manager.update_current_file(f"Analyzing: {story.title[:50]}")

            flow = await self.analyze_user_story(story, file_analyses)
            result.flows.append(flow)
            result.all_issues.extend(flow.issues)

        # Tracer tous les endpoints
        tracer_result = self.flow_tracer.trace_all_files()
        result.all_endpoints = tracer_result.api_endpoints
        result.orphan_endpoints = tracer_result.orphan_endpoints
        result.missing_handlers = tracer_result.unmatched_calls

        # Mettre à jour les statistiques
        result.update_statistics()

        return result

    async def check_consistency(
        self,
        flow: UserStoryFlow,
    ) -> List[FlowIssue]:
        """
        Vérifie la cohérence logique d'un flux

        Args:
            flow: Le flux à vérifier

        Returns:
            Liste des problèmes de cohérence
        """
        issues: List[FlowIssue] = []

        # Construire le contexte du flux
        flow_description = f"""
Flow: {flow.title}
Entry: {flow.entry_point}
Steps:
"""
        for step in flow.steps:
            flow_description += f"  {step.order}. [{step.step_type}] {step.description}\n"

        flow_description += "\nAPI Calls:\n"
        for call in flow.api_calls:
            flow_description += f"  - {call.method} {call.url_pattern}\n"

        flow_description += "\nEndpoints:\n"
        for ep in flow.api_endpoints:
            flow_description += f"  - {ep.method} {ep.path} (protected: {ep.is_protected})\n"

        prompt = f"""Analyse la cohérence logique de ce flux utilisateur et détecte les problèmes potentiels.

{flow_description}

Vérifie:
1. Les incohérences logiques (ex: action impossible dans ce contexte)
2. Les gestions d'erreurs manquantes
3. Les risques de race conditions
4. Les failles de sécurité
5. Les problèmes de performance

Réponds en JSON:
{{
    "is_consistent": true/false,
    "logical_issues": ["string"],
    "missing_error_handling": ["string"],
    "race_condition_risks": ["string"],
    "security_gaps": ["string"],
    "performance_concerns": ["string"]
}}
"""

        try:
            result = await self._call_ai_structured(prompt, ConsistencyCheckSchema)

            # Créer des issues pour chaque problème
            for issue_text in result.logical_issues:
                issues.append(FlowIssue(
                    id=f"US-ISSUE-{uuid.uuid4().hex[:8].upper()}",
                    severity=IssueSeverity.HIGH.value,
                    issue_type="logical_inconsistency",
                    title="Logical inconsistency",
                    description=issue_text,
                    recommendation="Review the flow logic",
                ))

            for issue_text in result.race_condition_risks:
                issues.append(FlowIssue(
                    id=f"US-ISSUE-{uuid.uuid4().hex[:8].upper()}",
                    severity=IssueSeverity.MEDIUM.value,
                    issue_type=IssueType.RACE_CONDITION.value,
                    title="Race condition risk",
                    description=issue_text,
                    recommendation="Add proper synchronization or sequencing",
                ))

            for issue_text in result.security_gaps:
                issues.append(FlowIssue(
                    id=f"US-ISSUE-{uuid.uuid4().hex[:8].upper()}",
                    severity=IssueSeverity.CRITICAL.value,
                    issue_type=IssueType.MISSING_AUTH.value,
                    title="Security gap",
                    description=issue_text,
                    recommendation="Address the security concern",
                ))

        except Exception:
            pass  # L'IA n'a pas pu analyser, continuer sans

        return issues
