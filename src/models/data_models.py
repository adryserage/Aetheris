"""
Modèles de données pour le système d'analyse de code
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class FileDependency:
    """Dépendance d'un fichier"""

    import_path: str  # Chemin importé (ex: './utils', '../types')
    resolved_path: Optional[str] = None  # Chemin résolu si trouvé
    exists: bool = False  # Si le fichier existe
    line_number: int = 0  # Ligne où l'import apparaît
    import_type: str = ""  # Type d'import (default, named, namespace, etc.)


@dataclass
class SecurityIssue:
    """Problème de sécurité détecté"""

    severity: str  # 'critical', 'high', 'medium', 'low', 'info'
    issue_type: str  # Type de vulnérabilité (XSS, SQLi, SSRF, etc.)
    description: str
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
    recommendation: str = ""
    cwe_id: Optional[str] = None  # Identifiant CWE (ex: CWE-79)
    owasp_category: Optional[str] = None  # Catégorie OWASP (ex: A01:2021)


@dataclass
class CodeMetrics:
    """Métriques de code"""

    file_path: str
    language: str
    lines_of_code: int
    cyclomatic_complexity: int
    max_nesting_depth: int
    function_count: int
    average_function_length: float
    duplicate_code_blocks: List[Tuple[int, int]] = field(
        default_factory=list
    )  # (start_line, end_line)
    maintainability_index: float = 0.0  # 0-100


@dataclass
class DependencyVulnerability:
    """Vulnérabilité dans une dépendance"""

    package_name: str
    version: str
    vulnerability_id: str
    severity: str
    description: str
    affected_versions: str
    fixed_version: Optional[str] = None
    cve_id: Optional[str] = None


@dataclass
class FileExport:
    """Export d'un fichier (fonction, classe, variable exportée)"""

    name: str  # Nom de l'export
    export_type: str  # 'default', 'named', 'function', 'class', 'variable', 'type', 'reexport'
    line_number: int
    is_default: bool = False
    alias: Optional[str] = None  # Pour "export { X as Y }"


@dataclass
class ReverseDependency:
    """Dépendance inverse - qui dépend de moi"""

    dependent_file: str  # Fichier qui m'importe
    import_path: str  # L'instruction d'import utilisée
    line_number: int  # Ligne dans le fichier dépendant
    imported_symbols: List[str] = field(default_factory=list)  # Symboles importés


@dataclass
class BugIdentifier:
    """Identifiant unique de bug pour corrélation inter-fichiers"""

    id: str  # ID unique (format: "BUG-{hash[:8]}")
    file_path: str
    line_number: Optional[int]
    bug_type: str  # 'security', 'risk', 'inconsistency', 'suggestion'
    severity: str  # 'critical', 'high', 'medium', 'low'
    description: str
    recommendation: str
    impacted_files: List[str] = field(default_factory=list)  # Fichiers affectés via dépendances
    fixed: bool = False  # Si le bug a été corrigé
    fixed_at: Optional[str] = None  # Timestamp de la correction (ISO format)
    fix_summary: Optional[str] = None  # Résumé de la correction appliquée
    failed: bool = False  # Si la correction a échoué
    failed_at: Optional[str] = None  # Timestamp de l'échec (ISO format)
    failure_reason: Optional[str] = None  # Raison de l'échec


@dataclass
class ImpactAnalysis:
    """Analyse d'impact pour un bug"""

    bug_id: str
    source_file: str
    directly_impacted: List[str] = field(default_factory=list)  # Fichiers qui importent directement
    transitively_impacted: List[str] = field(default_factory=list)  # Fichiers à N niveaux
    impact_chain: List[List[str]] = field(default_factory=list)  # Chemins source → impacté

    def to_dict(self) -> dict:
        """Convertit en dictionnaire pour la sérialisation JSON."""
        return {
            "bug_id": self.bug_id,
            "source_file": self.source_file,
            "directly_impacted": self.directly_impacted,
            "transitively_impacted": self.transitively_impacted,
            "impact_chain": self.impact_chain,
        }


@dataclass
class PerformanceIssue:
    """Performance issue detected (v2.10)"""

    severity: str  # 'critical', 'high', 'medium', 'low', 'info'
    issue_type: str  # 'O(n²)', 'N+1', 'memory_leak', 'blocking_async', 'inefficient_algo'
    description: str
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
    recommendation: str = ""
    estimated_impact: Optional[str] = None  # e.g., "10x slower for large datasets"
    complexity: Optional[str] = None  # e.g., "O(n²)", "O(n log n)"


@dataclass
class APIContractViolation:
    """API contract violation detected (v2.10)"""

    severity: str  # 'critical', 'high', 'medium', 'low', 'info'
    violation_type: str  # 'http_method', 'rest_naming', 'breaking_change', 'undocumented'
    description: str
    endpoint: Optional[str] = None
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
    recommendation: str = ""
    rest_principle: Optional[str] = None  # e.g., "GET should not have body"


@dataclass
class TypeSafetyIssue:
    """Type safety issue detected (v2.10)"""

    severity: str  # 'critical', 'high', 'medium', 'low', 'info'
    issue_type: str  # 'any_usage', 'unsafe_cast', 'type_ignore', 'null_safety'
    description: str
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
    recommendation: str = ""
    language: str = ""  # 'typescript', 'python', 'java', etc.


@dataclass
class PrivacyViolation:
    """Data privacy violation detected (v2.10)"""

    severity: str  # 'critical', 'high', 'medium', 'low', 'info'
    violation_type: str  # 'pii_logging', 'missing_encryption', 'data_retention', 'consent'
    description: str
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
    recommendation: str = ""
    pii_type: Optional[str] = None  # e.g., "email", "ssn", "phone", "credit_card"
    compliance_frameworks: List[str] = field(default_factory=list)  # e.g., ["GDPR", "HIPAA"]


@dataclass
class FileAnalysis:
    """Résultat d'analyse d'un fichier"""

    file_path: str
    language: str
    objective: str
    strengths: List[str]
    risks: List[str]
    suggestions: List[str]
    analysis_markdown: str
    success: bool
    dependencies: List[FileDependency] = field(default_factory=list)
    inconsistencies: List[str] = field(default_factory=list)
    security_issues: List[SecurityIssue] = field(default_factory=list)
    code_metrics: Optional[CodeMetrics] = None
    error: Optional[str] = None
    # Nouveaux champs pour l'analyse des relations et bugs
    exports: List[FileExport] = field(default_factory=list)
    reverse_dependencies: List[ReverseDependency] = field(default_factory=list)
    bugs: List[BugIdentifier] = field(default_factory=list)
    # v2.10: Extended agent analysis results
    performance_issues: List["PerformanceIssue"] = field(default_factory=list)
    api_violations: List["APIContractViolation"] = field(default_factory=list)
    type_safety_issues: List["TypeSafetyIssue"] = field(default_factory=list)
    privacy_violations: List["PrivacyViolation"] = field(default_factory=list)
