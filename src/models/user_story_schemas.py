"""
Schémas Pydantic pour l'analyse de User Stories

Ces modèles sont utilisés avec la fonctionnalité Structured Outputs de Gemini
pour garantir des réponses JSON valides et typées lors de l'analyse de flux.
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class FlowStepType(str, Enum):
    """Types d'étapes dans un flux"""

    UI_EVENT = "ui_event"
    STATE_UPDATE = "state_update"
    API_CALL = "api_call"
    BACKEND_HANDLER = "backend_handler"
    DATABASE_QUERY = "database_query"
    EXTERNAL_SERVICE = "external_service"
    RESPONSE = "response"
    REDIRECT = "redirect"
    ERROR_HANDLER = "error_handler"


class FlowIssueSeverity(str, Enum):
    """Sévérité des problèmes de flux"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class FlowIssueType(str, Enum):
    """Types de problèmes détectés"""

    ORPHAN_ENDPOINT = "orphan_endpoint"
    MISSING_HANDLER = "missing_handler"
    MISSING_ERROR_HANDLING = "missing_error_handling"
    TYPE_MISMATCH = "type_mismatch"
    RACE_CONDITION = "race_condition"
    DEAD_CODE = "dead_code"
    MISSING_AUTH = "missing_auth"
    MISSING_VALIDATION = "missing_validation"
    INFINITE_LOOP = "infinite_loop"
    MISSING_LOADING_STATE = "missing_loading_state"
    UNHANDLED_PROMISE = "unhandled_promise"


# === Schémas pour la détection d'endpoints ===


class APIEndpointSchema(BaseModel):
    """Endpoint API détecté par l'IA"""

    method: str = Field(description="Méthode HTTP (GET, POST, PUT, DELETE)")
    path: str = Field(description="Chemin de l'endpoint (/api/users, /login)")
    handler_name: Optional[str] = Field(None, description="Nom de la fonction handler")
    is_protected: bool = Field(False, description="Nécessite authentification")
    middleware: List[str] = Field(
        default_factory=list, description="Middleware appliqués (auth, validate)"
    )
    request_body_type: Optional[str] = Field(None, description="Type du body de requête")
    response_type: Optional[str] = Field(None, description="Type de la réponse")
    description: Optional[str] = Field(None, description="Description de l'endpoint")


class APICallSchema(BaseModel):
    """Appel API détecté par l'IA"""

    method: str = Field(description="Méthode HTTP utilisée")
    url_pattern: str = Field(description="Pattern d'URL (peut contenir des variables)")
    library: str = Field(description="Librairie utilisée (fetch, axios, dio)")
    has_error_handling: bool = Field(False, description="Présence de gestion d'erreur")
    has_loading_state: bool = Field(False, description="Présence d'état de chargement")
    request_data_type: Optional[str] = Field(None, description="Type des données envoyées")


# === Schémas pour l'analyse de flux ===


class FlowStepSchema(BaseModel):
    """Étape de flux générée par l'IA"""

    order: int = Field(ge=0, description="Ordre de l'étape dans le flux (0, 1, 2...)")
    step_type: FlowStepType = Field(description="Type d'étape")
    description: str = Field(description="Description humaine de ce qui se passe")
    file_hint: Optional[str] = Field(
        None, description="Indice sur le fichier concerné (composant, service)"
    )
    inputs: List[str] = Field(
        default_factory=list, description="Données en entrée de cette étape"
    )
    outputs: List[str] = Field(
        default_factory=list, description="Données en sortie de cette étape"
    )


class FlowIssueSchema(BaseModel):
    """Problème de flux détecté par l'IA"""

    severity: FlowIssueSeverity = Field(description="Sévérité du problème")
    issue_type: FlowIssueType = Field(description="Type de problème")
    title: str = Field(description="Titre court du problème")
    description: str = Field(description="Description détaillée du problème")
    affected_steps: List[int] = Field(
        default_factory=list, description="Indices des étapes affectées"
    )
    recommendation: str = Field(description="Comment corriger ce problème")
    code_example: Optional[str] = Field(
        None, description="Exemple de code pour corriger"
    )
    auto_fixable: bool = Field(
        False, description="Peut être corrigé automatiquement"
    )


class DataTransformationSchema(BaseModel):
    """Transformation de données entre couches"""

    source_type: str = Field(description="Type source (interface, class)")
    target_type: str = Field(description="Type cible")
    transformation_type: str = Field(
        description="Type de transformation (mapping, serialization, validation)"
    )
    is_complete: bool = Field(True, description="Tous les champs sont mappés")
    missing_fields: List[str] = Field(
        default_factory=list, description="Champs non mappés"
    )
    type_mismatches: List[str] = Field(
        default_factory=list, description="Incompatibilités de types"
    )


# === Schémas pour le parsing de user stories ===


class UserStorySchema(BaseModel):
    """User story parsée par l'IA"""

    title: str = Field(description="Titre de la user story")
    actor: str = Field("user", description="Acteur (user, admin, system)")
    action: str = Field(description="Action principale à effectuer")
    expected_outcome: str = Field(description="Résultat attendu")
    preconditions: List[str] = Field(
        default_factory=list, description="Préconditions nécessaires"
    )
    entry_component: Optional[str] = Field(
        None, description="Composant de départ suggéré"
    )


class UserStoryParseResult(BaseModel):
    """Résultat du parsing d'une user story textuelle"""

    stories: List[UserStorySchema] = Field(
        default_factory=list, description="User stories identifiées"
    )
    ambiguities: List[str] = Field(
        default_factory=list, description="Points ambigus à clarifier"
    )
    suggested_flows: List[str] = Field(
        default_factory=list, description="Flux suggérés à analyser"
    )


# === Schémas pour l'analyse complète ===


class FlowAnalysisSchema(BaseModel):
    """Analyse complète d'un flux par l'IA"""

    title: str = Field(description="Titre du flux analysé")
    steps: List[FlowStepSchema] = Field(
        default_factory=list, description="Étapes du flux"
    )
    issues: List[FlowIssueSchema] = Field(
        default_factory=list, description="Problèmes détectés"
    )
    is_complete: bool = Field(
        True, description="Le flux atteint-il son objectif?"
    )
    missing_steps: List[str] = Field(
        default_factory=list, description="Étapes manquantes pour compléter le flux"
    )
    data_flow: List[DataTransformationSchema] = Field(
        default_factory=list, description="Transformations de données"
    )
    summary: str = Field(description="Résumé de l'analyse du flux")


class ConsistencyCheckSchema(BaseModel):
    """Vérification de cohérence d'un flux"""

    is_consistent: bool = Field(description="Le flux est-il cohérent?")
    logical_issues: List[str] = Field(
        default_factory=list, description="Incohérences logiques détectées"
    )
    missing_error_handling: List[str] = Field(
        default_factory=list, description="Points sans gestion d'erreur"
    )
    race_condition_risks: List[str] = Field(
        default_factory=list, description="Risques de race condition"
    )
    security_gaps: List[str] = Field(
        default_factory=list, description="Failles de sécurité potentielles"
    )
    performance_concerns: List[str] = Field(
        default_factory=list, description="Problèmes de performance potentiels"
    )


class UserStoryAnalysisSchema(BaseModel):
    """Résultat complet d'analyse pour structured output"""

    flows: List[FlowAnalysisSchema] = Field(
        default_factory=list, description="Analyses de flux"
    )
    orphan_endpoints: List[APIEndpointSchema] = Field(
        default_factory=list, description="Endpoints jamais appelés"
    )
    missing_handlers: List[APICallSchema] = Field(
        default_factory=list, description="Appels API sans handler"
    )
    consistency: ConsistencyCheckSchema = Field(
        description="Résultat de la vérification de cohérence"
    )
    summary: str = Field(description="Résumé global de l'analyse")
    recommendations: List[str] = Field(
        default_factory=list, description="Recommandations prioritaires"
    )
    score: float = Field(
        ge=0.0, le=10.0, description="Score de qualité du flux (0-10)"
    )
