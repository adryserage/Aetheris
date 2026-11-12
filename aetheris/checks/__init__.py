"""Deterministic checks, grouped by the agent that owns them."""

from aetheris.checks.api_contract import api_patterns, orphan_endpoints
from aetheris.checks.architecture import circular_imports
from aetheris.checks.base import RULE_IDS, Check, CheckContext
from aetheris.checks.data_privacy import pii_patterns
from aetheris.checks.dependency import manifest_parse, osv_lookup
from aetheris.checks.metrics import duplicate_blocks, file_metrics, metric_thresholds
from aetheris.checks.performance import performance_patterns
from aetheris.checks.secrets import secret_scan
from aetheris.checks.security import security_patterns
from aetheris.checks.type_safety import type_patterns
from aetheris.domain import AgentId

CHECKS: dict[AgentId, dict[str, Check]] = {
    "security": {"secret_scan": secret_scan, "security_patterns": security_patterns},
    "dependency": {"manifest_parse": manifest_parse, "osv_lookup": osv_lookup},
    "metrics": {"file_metrics": file_metrics},
    "code_quality": {"metric_thresholds": metric_thresholds, "duplicate_blocks": duplicate_blocks},
    "architecture": {"circular_imports": circular_imports},
    "type_safety": {"type_patterns": type_patterns},
    "performance": {"performance_patterns": performance_patterns},
    "api_contract": {"api_patterns": api_patterns, "orphan_endpoints": orphan_endpoints},
    "data_privacy": {"pii_patterns": pii_patterns},
    "qa_synthesis": {},
}

CHECK_NAMES: dict[AgentId, tuple[str, ...]] = {a: tuple(c) for a, c in CHECKS.items()}

__all__ = ["CHECKS", "CHECK_NAMES", "RULE_IDS", "Check", "CheckContext"]
