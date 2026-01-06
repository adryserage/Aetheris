"""
Schémas Pydantic pour les résultats d'analyse

Ces modèles sont utilisés avec la fonctionnalité Structured Outputs de Gemini
pour garantir des réponses JSON valides et typées.
"""

from enum import Enum
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field


class Severity(str, Enum):
    """Niveaux de sévérité pour les issues"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class IssueCategory(str, Enum):
    """Catégories d'issues"""

    SECURITY = "security"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    RELIABILITY = "reliability"
    STYLE = "style"
    DOCUMENTATION = "documentation"


# === Schémas pour l'analyse de sécurité ===


class SecurityIssue(BaseModel):
    """Issue de sécurité détectée"""

    type: str = Field(description="Type de vulnérabilité (XSS, SQLi, SSRF, etc.)")
    severity: Severity = Field(description="Niveau de sévérité")
    line_number: Optional[int] = Field(None, description="Numéro de ligne concernée")
    description: str = Field(description="Description détaillée de la vulnérabilité")
    recommendation: str = Field(description="Recommandation pour corriger")
    cwe_id: Optional[str] = Field(None, description="Identifiant CWE (ex: CWE-79)")
    owasp_category: Optional[str] = Field(None, description="Catégorie OWASP (ex: A01:2021)")
    code_snippet: Optional[str] = Field(None, description="Extrait de code vulnérable")


class SecurityAnalysisResult(BaseModel):
    """Résultat complet d'une analyse de sécurité"""

    issues: List[SecurityIssue] = Field(
        default_factory=list, description="Liste des issues trouvées"
    )
    risk_score: float = Field(0.0, ge=0.0, le=10.0, description="Score de risque global (0-10)")
    summary: str = Field("", description="Résumé de l'analyse")


# === Schémas pour les métriques de code ===


class CodeMetrics(BaseModel):
    """Métriques du code"""

    cyclomatic_complexity: int = Field(0, ge=0, description="Complexité cyclomatique")
    cognitive_complexity: int = Field(0, ge=0, description="Complexité cognitive")
    lines_of_code: int = Field(0, ge=0, description="Nombre de lignes de code")
    comment_lines: int = Field(0, ge=0, description="Nombre de lignes de commentaires")
    comment_ratio: float = Field(0.0, ge=0.0, le=1.0, description="Ratio commentaires/code")
    maintainability_index: float = Field(
        100.0, ge=0.0, le=100.0, description="Index de maintenabilité (0-100)"
    )
    test_coverage_estimate: Optional[float] = Field(
        None, ge=0.0, le=100.0, description="Estimation de la couverture de tests (%)"
    )
    functions_count: int = Field(0, ge=0, description="Nombre de fonctions/méthodes")
    classes_count: int = Field(0, ge=0, description="Nombre de classes")
    max_function_length: int = Field(0, ge=0, description="Longueur max d'une fonction")
    average_function_length: float = Field(
        0.0, ge=0.0, description="Longueur moyenne des fonctions"
    )


# === Schémas pour l'analyse de code ===


class CodeIssue(BaseModel):
    """Issue générale de code"""

    category: IssueCategory = Field(description="Catégorie de l'issue")
    severity: Severity = Field(description="Niveau de sévérité")
    line_number: Optional[int] = Field(None, description="Numéro de ligne")
    title: str = Field(description="Titre court de l'issue")
    description: str = Field(description="Description détaillée")
    recommendation: str = Field(description="Recommandation pour corriger")
    code_snippet: Optional[str] = Field(None, description="Extrait de code concerné")


class Dependency(BaseModel):
    """Dépendance du fichier"""

    name: str = Field(description="Nom de la dépendance/module")
    import_path: str = Field(description="Chemin d'import complet")
    is_external: bool = Field(False, description="True si c'est une dépendance externe")
    line_number: Optional[int] = Field(None, description="Ligne d'import")


class FileAnalysisResult(BaseModel):
    """Résultat complet d'analyse de fichier"""

    file_path: str = Field(description="Chemin du fichier analysé")
    language: str = Field(description="Langage de programmation détecté")
    summary: str = Field(description="Résumé de l'analyse")
    purpose: str = Field("", description="Objectif/rôle du fichier")
    issues: List[CodeIssue] = Field(default_factory=list, description="Issues détectées")
    security_issues: List[SecurityIssue] = Field(
        default_factory=list, description="Issues de sécurité"
    )
    metrics: Optional[CodeMetrics] = Field(None, description="Métriques du code")
    dependencies: List[Dependency] = Field(
        default_factory=list, description="Dépendances du fichier"
    )
    recommendations: List[str] = Field(
        default_factory=list, description="Recommandations générales"
    )
    key_functions: List[str] = Field(
        default_factory=list, description="Fonctions/méthodes principales"
    )
    key_classes: List[str] = Field(default_factory=list, description="Classes principales")


# === Schémas pour l'analyse d'architecture ===


class ArchitecturePattern(BaseModel):
    """Pattern d'architecture détecté"""

    name: str = Field(description="Nom du pattern (MVC, Repository, etc.)")
    confidence: float = Field(ge=0.0, le=1.0, description="Niveau de confiance (0-1)")
    evidence: List[str] = Field(default_factory=list, description="Preuves du pattern")


class LayerAnalysis(BaseModel):
    """Analyse d'une couche architecturale"""

    name: str = Field(description="Nom de la couche (presentation, business, data)")
    files: List[str] = Field(default_factory=list, description="Fichiers de cette couche")
    responsibilities: List[str] = Field(
        default_factory=list, description="Responsabilités de la couche"
    )
    issues: List[str] = Field(default_factory=list, description="Problèmes identifiés")


class ArchitectureAnalysisResult(BaseModel):
    """Résultat d'analyse d'architecture"""

    patterns: List[ArchitecturePattern] = Field(
        default_factory=list, description="Patterns détectés"
    )
    layers: List[LayerAnalysis] = Field(default_factory=list, description="Couches identifiées")
    coupling_score: float = Field(
        0.0, ge=0.0, le=10.0, description="Score de couplage (0=faible, 10=fort)"
    )
    cohesion_score: float = Field(
        0.0, ge=0.0, le=10.0, description="Score de cohésion (0=faible, 10=fort)"
    )
    summary: str = Field("", description="Résumé de l'architecture")
    recommendations: List[str] = Field(default_factory=list, description="Recommandations")


# === Schémas pour l'analyse de qualité ===


class QualityDimension(BaseModel):
    """Dimension de qualité évaluée"""

    name: str = Field(description="Nom de la dimension (Reliability, Security, etc.)")
    score: float = Field(ge=0.0, le=10.0, description="Score (0-10)")
    grade: str = Field(description="Note (A, B, C, D, F)")
    issues_count: int = Field(0, ge=0, description="Nombre d'issues liées")
    key_findings: List[str] = Field(default_factory=list, description="Constats principaux")


class QualityAssuranceResult(BaseModel):
    """Résultat d'analyse de qualité"""

    overall_score: float = Field(ge=0.0, le=10.0, description="Score global (0-10)")
    overall_grade: str = Field(description="Note globale (A, B, C, D, F)")
    dimensions: List[QualityDimension] = Field(
        default_factory=list, description="Dimensions évaluées"
    )
    technical_debt_hours: float = Field(
        0.0, ge=0.0, description="Estimation dette technique (heures)"
    )
    summary: str = Field("", description="Résumé de la qualité")
    top_priorities: List[str] = Field(default_factory=list, description="Priorités d'amélioration")


# === Schémas pour les vulnérabilités de dépendances ===


class VulnerabilityInfo(BaseModel):
    """Information sur une vulnérabilité"""

    id: str = Field(description="Identifiant (CVE, GHSA, etc.)")
    severity: Severity = Field(description="Niveau de sévérité")
    package: str = Field(description="Package affecté")
    version: str = Field(description="Version affectée")
    fixed_version: Optional[str] = Field(None, description="Version corrigée")
    description: str = Field(description="Description de la vulnérabilité")
    cvss_score: Optional[float] = Field(None, ge=0.0, le=10.0, description="Score CVSS")
    references: List[str] = Field(default_factory=list, description="Liens de référence")


class DependencyVulnerabilityResult(BaseModel):
    """Résultat d'analyse des vulnérabilités de dépendances"""

    vulnerabilities: List[VulnerabilityInfo] = Field(
        default_factory=list, description="Vulnérabilités trouvées"
    )
    total_packages: int = Field(0, ge=0, description="Nombre total de packages")
    vulnerable_packages: int = Field(0, ge=0, description="Packages vulnérables")
    summary: str = Field("", description="Résumé de l'analyse")
