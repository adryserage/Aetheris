"""
Modèles de données pour l'analyse de Pull Requests
"""

from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import List
from typing import Optional


class PRIssueType(str, Enum):
    """Types d'issues détectées dans une PR"""

    SECURITY = "security"
    BUG = "bug"
    PERFORMANCE = "performance"
    STYLE = "style"
    DOCUMENTATION = "documentation"
    LOGIC = "logic"
    TEST = "test"
    BEST_PRACTICE = "best_practice"


class PRIssueSeverity(str, Enum):
    """Niveaux de sévérité des issues"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class PRFileStatus(str, Enum):
    """Statut d'un fichier dans la PR"""

    ADDED = "added"
    MODIFIED = "modified"
    DELETED = "deleted"
    RENAMED = "renamed"


@dataclass
class PRInfo:
    """Informations sur une Pull Request"""

    repo: str  # owner/repo
    pr_number: int
    title: str
    description: str
    author_login: str
    author_email: Optional[str]
    base_branch: str
    head_branch: str
    url: str
    state: str  # open, closed, merged
    files_count: int = 0
    additions: int = 0
    deletions: int = 0
    head_sha: Optional[str] = None


@dataclass
class PRFile:
    """Fichier modifié dans une PR"""

    path: str
    status: PRFileStatus
    additions: int
    deletions: int
    patch: Optional[str] = None  # Diff du fichier
    previous_path: Optional[str] = None  # Pour les renames
    content: Optional[str] = None  # Contenu complet si disponible


@dataclass
class PRIssue:
    """Issue détectée lors de la revue de PR"""

    id: str  # ID unique (format: "PR-{hash[:8]}")
    file_path: str
    line_number: Optional[int]
    line_end: Optional[int]  # Pour les issues multi-lignes
    issue_type: PRIssueType
    severity: PRIssueSeverity
    title: str
    description: str
    suggestion: str
    code_snippet: Optional[str] = None
    providers_found: List[str] = field(default_factory=list)  # Providers ayant trouvé l'issue


@dataclass
class PRComment:
    """Commentaire à poster sur la PR"""

    file_path: str
    line_number: int
    body: str
    side: str = "RIGHT"  # LEFT (ancien) ou RIGHT (nouveau)


@dataclass
class PRReviewResult:
    """Résultat complet de la revue de PR"""

    pr_info: PRInfo
    issues: List[PRIssue]
    summary: str
    providers_used: List[str]
    consensus_mode: bool
    total_issues_before_consensus: int
    inline_comments: List[PRComment] = field(default_factory=list)
    is_own_pr: bool = False
    risk_score: float = 0.0  # 0-10
    approval_recommendation: str = "COMMENT"  # APPROVE, REQUEST_CHANGES, COMMENT
