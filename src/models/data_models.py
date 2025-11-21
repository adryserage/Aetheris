"""
Modèles de données pour le système d'analyse de code
"""

from typing import List, Optional, Tuple
from dataclasses import dataclass, field


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

    severity: str  # 'critical', 'high', 'medium', 'low'
    issue_type: str  # Type de vulnérabilité
    description: str
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
    recommendation: str = ""


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
