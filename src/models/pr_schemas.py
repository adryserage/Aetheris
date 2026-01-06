"""
Schémas Pydantic pour l'analyse de Pull Requests

Ces modèles sont utilisés avec la fonctionnalité Structured Outputs de Gemini
pour garantir des réponses JSON valides et typées.
"""

from enum import Enum
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field


class PRIssueSeverityEnum(str, Enum):
    """Niveaux de sévérité des issues"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class PRIssueTypeEnum(str, Enum):
    """Types d'issues détectées"""

    SECURITY = "security"
    BUG = "bug"
    PERFORMANCE = "performance"
    STYLE = "style"
    DOCUMENTATION = "documentation"
    LOGIC = "logic"
    TEST = "test"
    BEST_PRACTICE = "best_practice"


class PRIssueSchema(BaseModel):
    """Schéma pour une issue détectée dans la PR"""

    file_path: str = Field(description="Chemin du fichier contenant l'issue")
    line_number: Optional[int] = Field(
        None, description="Numéro de ligne (dans le nouveau fichier)"
    )
    line_end: Optional[int] = Field(None, description="Ligne de fin pour les issues multi-lignes")
    issue_type: PRIssueTypeEnum = Field(description="Type d'issue")
    severity: PRIssueSeverityEnum = Field(description="Niveau de sévérité")
    title: str = Field(description="Titre court de l'issue")
    description: str = Field(description="Description détaillée du problème")
    suggestion: str = Field(description="Suggestion pour corriger l'issue")
    code_snippet: Optional[str] = Field(None, description="Extrait de code concerné")


class PRAnalysisResultSchema(BaseModel):
    """Schéma pour le résultat complet de l'analyse de PR"""

    issues: List[PRIssueSchema] = Field(
        default_factory=list, description="Liste des issues trouvées"
    )
    summary: str = Field(description="Résumé global de la revue de PR")
    risk_score: float = Field(0.0, ge=0.0, le=10.0, description="Score de risque (0-10)")
    approval_recommendation: str = Field(
        default="COMMENT",
        description="Recommandation: APPROVE, REQUEST_CHANGES, ou COMMENT",
    )
    positive_points: List[str] = Field(default_factory=list, description="Points positifs du code")
    general_suggestions: List[str] = Field(
        default_factory=list, description="Suggestions générales (non liées à une ligne)"
    )
