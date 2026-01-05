"""
Modèles de données pour l'analyse de User Stories
Trace les flux frontend ↔ backend et détecte les incohérences
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class HTTPMethod(str, Enum):
    """Méthodes HTTP supportées"""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class FlowStepType(str, Enum):
    """Types d'étapes dans un flux"""

    UI_EVENT = "ui_event"  # Clic, soumission de formulaire
    STATE_UPDATE = "state_update"  # Mise à jour d'état (Redux, useState)
    API_CALL = "api_call"  # Appel HTTP vers le backend
    BACKEND_HANDLER = "backend_handler"  # Handler de route backend
    DATABASE_QUERY = "database_query"  # Requête DB
    EXTERNAL_SERVICE = "external_service"  # Appel à un service externe
    RESPONSE = "response"  # Réponse au frontend
    REDIRECT = "redirect"  # Redirection
    ERROR_HANDLER = "error_handler"  # Gestion d'erreur


class IssueType(str, Enum):
    """Types de problèmes détectés dans les flux"""

    ORPHAN_ENDPOINT = "orphan_endpoint"  # Endpoint jamais appelé
    MISSING_HANDLER = "missing_handler"  # Appel API sans endpoint
    MISSING_ERROR_HANDLING = "missing_error_handling"  # Pas de try/catch
    TYPE_MISMATCH = "type_mismatch"  # Différence types request/response
    RACE_CONDITION = "race_condition"  # Appels concurrents problématiques
    DEAD_CODE = "dead_code"  # Code jamais exécuté dans le flow
    MISSING_AUTH = "missing_auth"  # Endpoint sensible sans auth
    MISSING_VALIDATION = "missing_validation"  # Pas de validation input
    INFINITE_LOOP = "infinite_loop"  # Boucle potentielle dans le flow
    MISSING_LOADING_STATE = "missing_loading_state"  # Pas d'état loading
    UNHANDLED_PROMISE = "unhandled_promise"  # Promise sans await/catch


class IssueSeverity(str, Enum):
    """Sévérité des problèmes"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class APIEndpoint:
    """Représente un endpoint API défini dans le backend"""

    file_path: str  # Fichier où l'endpoint est défini
    line_number: int  # Ligne de la définition
    method: str  # GET, POST, PUT, DELETE
    path: str  # /api/users, /login, etc.
    handler_name: Optional[str] = None  # Nom de la fonction handler
    framework: str = ""  # express, fastapi, flask, nextjs
    middleware: List[str] = field(default_factory=list)  # Auth, validation, etc.
    is_protected: bool = False  # Nécessite authentification
    request_body_type: Optional[str] = None  # Type/interface du body
    response_type: Optional[str] = None  # Type de la réponse
    description: Optional[str] = None  # JSDoc ou docstring


@dataclass
class APICall:
    """Représente un appel API fait depuis le frontend"""

    file_path: str  # Fichier où l'appel est fait
    line_number: int  # Ligne de l'appel
    method: str  # GET, POST, PUT, DELETE
    url_pattern: str  # URL avec potentielles variables
    resolved_url: Optional[str] = None  # URL résolue si possible
    library: str = ""  # fetch, axios, dio, requests, etc.
    has_error_handling: bool = False  # try/catch ou .catch()
    has_loading_state: bool = False  # useState loading ou équivalent
    request_data: Optional[str] = None  # Données envoyées
    matched_endpoint: Optional[str] = None  # Endpoint correspondant si trouvé


@dataclass
class FlowStep:
    """Une étape dans un flux de user story"""

    order: int  # Ordre dans le flux (0, 1, 2...)
    step_type: str  # FlowStepType value
    file_path: str  # Fichier concerné
    line_number: int  # Ligne du code
    description: str  # Description humaine de l'étape
    code_snippet: Optional[str] = None  # Extrait de code
    inputs: List[str] = field(default_factory=list)  # Données en entrée
    outputs: List[str] = field(default_factory=list)  # Données en sortie
    duration_estimate: Optional[str] = None  # Estimation (sync, async, slow)


@dataclass
class DataTransformation:
    """Transformation de données entre les couches"""

    source_file: str  # Fichier source
    source_type: str  # Type/interface source
    target_file: str  # Fichier cible
    target_type: str  # Type/interface cible
    transformation_type: str  # mapping, serialization, validation
    is_complete: bool = True  # Tous les champs mappés?
    missing_fields: List[str] = field(default_factory=list)  # Champs manquants
    type_mismatches: List[str] = field(default_factory=list)  # Incompatibilités


@dataclass
class FlowIssue:
    """Problème détecté dans un flux"""

    id: str  # ID unique (US-ISSUE-{hash})
    severity: str  # IssueSeverity value
    issue_type: str  # IssueType value
    title: str  # Titre court
    description: str  # Description détaillée
    affected_files: List[str] = field(default_factory=list)  # Fichiers concernés
    affected_steps: List[int] = field(default_factory=list)  # Indices des étapes
    recommendation: str = ""  # Comment corriger
    code_example: Optional[str] = None  # Exemple de correction
    auto_fixable: bool = False  # Peut être corrigé automatiquement


@dataclass
class UserStory:
    """Représente une user story à analyser"""

    id: str  # ID unique
    title: str  # Titre de la story
    description: str  # Description complète
    actor: str = "user"  # Acteur (user, admin, system)
    action: str = ""  # Action principale
    expected_outcome: str = ""  # Résultat attendu
    entry_point_file: Optional[str] = None  # Fichier de départ si connu
    entry_point_component: Optional[str] = None  # Composant de départ


@dataclass
class UserStoryFlow:
    """Flux complet pour une user story"""

    id: str  # ID unique du flow
    story: UserStory  # User story associée
    title: str  # Titre du flow
    entry_point: str  # Fichier de départ
    steps: List[FlowStep] = field(default_factory=list)  # Étapes du flow
    api_calls: List[APICall] = field(default_factory=list)  # Appels API détectés
    api_endpoints: List[APIEndpoint] = field(default_factory=list)  # Endpoints utilisés
    data_transformations: List[DataTransformation] = field(default_factory=list)
    issues: List[FlowIssue] = field(default_factory=list)  # Problèmes dans ce flow
    is_complete: bool = False  # Le flow atteint-il l'objectif?
    missing_steps: List[str] = field(default_factory=list)  # Étapes manquantes


@dataclass
class UserStoryAnalysisResult:
    """Résultat complet de l'analyse de user stories"""

    analysis_id: str  # ID unique de l'analyse
    timestamp: str  # Date/heure de l'analyse
    project_root: str  # Racine du projet analysé

    # Résultats
    flows: List[UserStoryFlow] = field(default_factory=list)  # Tous les flows
    all_issues: List[FlowIssue] = field(default_factory=list)  # Tous les problèmes

    # Endpoints
    all_endpoints: List[APIEndpoint] = field(default_factory=list)  # Tous les endpoints
    orphan_endpoints: List[APIEndpoint] = field(default_factory=list)  # Non appelés
    missing_handlers: List[APICall] = field(default_factory=list)  # Appels sans handler

    # Code mort
    dead_code_paths: List[str] = field(default_factory=list)  # Fichiers morts

    # Statistiques
    total_flows: int = 0
    total_steps: int = 0
    total_api_calls: int = 0
    total_endpoints: int = 0

    # Issues par sévérité
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0

    # Sorties
    summary: str = ""  # Résumé textuel
    mermaid_diagram: str = ""  # Diagramme Mermaid
    json_report: Dict[str, Any] = field(default_factory=dict)  # Rapport JSON

    def update_statistics(self) -> None:
        """Met à jour les statistiques à partir des données"""
        self.total_flows = len(self.flows)
        self.total_steps = sum(len(f.steps) for f in self.flows)
        self.total_api_calls = sum(len(f.api_calls) for f in self.flows)
        self.total_endpoints = len(self.all_endpoints)

        self.critical_count = sum(
            1 for i in self.all_issues if i.severity == IssueSeverity.CRITICAL.value
        )
        self.high_count = sum(1 for i in self.all_issues if i.severity == IssueSeverity.HIGH.value)
        self.medium_count = sum(
            1 for i in self.all_issues if i.severity == IssueSeverity.MEDIUM.value
        )
        self.low_count = sum(1 for i in self.all_issues if i.severity == IssueSeverity.LOW.value)
