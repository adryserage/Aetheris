"""
Data Privacy Analysis Agent (v2.10)

Detects PII logging, missing encryption, compliance violations,
and data privacy anti-patterns. Supports GDPR, HIPAA, PCI-DSS, and CCPA frameworks.
"""

import re
from typing import List, Optional, Set

from src.agents.base_agent import BaseAgent
from src.core.config import AnalysisConfig
from src.core.progress import ProgressManager
from src.models.data_models import PrivacyViolation


class DataPrivacyAgent(BaseAgent):
    """Agent for detecting data privacy violations"""

    # Compliance frameworks and their requirements
    COMPLIANCE_FRAMEWORKS = {
        "gdpr": {
            "name": "GDPR (General Data Protection Regulation)",
            "pii_types": ["email", "name", "phone", "address", "ip_address", "location"],
            "requirements": ["consent", "right_to_erasure", "data_minimization", "encryption"],
        },
        "hipaa": {
            "name": "HIPAA (Health Insurance Portability and Accountability Act)",
            "pii_types": ["ssn", "medical_record", "health_data", "insurance_id"],
            "requirements": ["encryption", "audit_logs", "access_control"],
        },
        "pci_dss": {
            "name": "PCI-DSS (Payment Card Industry Data Security Standard)",
            "pii_types": ["credit_card", "cvv", "expiry_date", "cardholder_name"],
            "requirements": ["encryption", "masking", "tokenization"],
        },
        "ccpa": {
            "name": "CCPA (California Consumer Privacy Act)",
            "pii_types": ["email", "name", "phone", "address", "ssn", "financial_data"],
            "requirements": ["disclosure", "opt_out", "data_deletion"],
        },
    }

    def __init__(self, config: AnalysisConfig, progress_manager: Optional[ProgressManager] = None):
        super().__init__(config, progress_manager)

        # PII detection patterns
        self.pii_patterns = {
            "email": [
                r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
                r"email\s*[:=]\s*[\"'][^\"']+@[^\"']+[\"']",
            ],
            "phone": [
                r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
                r"\+\d{1,3}[-.\s]?\d{3,14}",
            ],
            "ssn": [
                r"\b\d{3}-\d{2}-\d{4}\b",
                r"(?i)ssn\s*[:=]\s*[\"']?\d+",
            ],
            "credit_card": [
                r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b",
                r"(?i)card[-_]?(?:number|num)\s*[:=]",
            ],
            "ip_address": [
                r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
            ],
            "api_key": [
                r"(?i)(?:api[-_]?key|secret[-_]?key|auth[-_]?token)\s*[:=]\s*[\"'][^\"']{16,}[\"']",
            ],
            "password": [
                r"(?i)password\s*[:=]\s*[\"'][^\"']+[\"']",
            ],
        }

        # Privacy violation patterns
        self.violation_patterns = {
            "pii_logging": [
                r"(?:console\.log|print|logger?\.\w+|Log\.\w+)\s*\([^)]*(?:email|ssn|password|phone|card)",
                r"(?:console\.log|print|logger?\.\w+)\s*\([^)]*user\.",
                r"log\.\w+\([^)]*(?:req|request)\.body",
            ],
            "missing_encryption": [
                r"(?i)(?:password|secret|key)\s*[:=]\s*[\"'][^\"']+[\"']",
                r"plain[-_]?text\s*[:=]",
                r"localStorage\.setItem\s*\([^)]*(?:token|password|secret)",
            ],
            "insecure_storage": [
                r"(?i)cookie\s*\([^)]*(?:httpOnly|secure)\s*:\s*false",
                r"sessionStorage\.setItem\s*\([^)]*(?:token|password)",
                r"localStorage\.setItem\s*\([^)]*auth",
            ],
            "data_retention": [
                r"(?:deleteOld|cleanup|purge)\s*[:=]\s*false",
                r"retention\s*[:=]\s*(?:null|undefined|none)",
            ],
            "missing_consent": [
                r"analytics\.track\s*\(",
                r"gtag\s*\(\s*[\"']event[\"']",
                r"mixpanel\.track\s*\(",
            ],
        }

    def _get_applicable_frameworks(
        self, pii_type: str, configured_frameworks: List[str]
    ) -> List[str]:
        """Get compliance frameworks that apply to this PII type"""
        applicable = []
        for framework_id, framework in self.COMPLIANCE_FRAMEWORKS.items():
            if configured_frameworks and framework_id not in configured_frameworks:
                continue
            if pii_type in framework["pii_types"]:
                applicable.append(framework["name"])
        return applicable

    def _detect_pattern_issues(
        self, content: str, file_path: str, compliance_frameworks: List[str]
    ) -> List[PrivacyViolation]:
        """Detect privacy violations via patterns"""
        issues = []
        lines = content.split("\n")

        # Check for PII in logging/output
        for violation_type, patterns in self.violation_patterns.items():
            for pattern in patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE):
                    line_number = content[: match.start()].count("\n") + 1
                    snippet = match.group(0)[:100]

                    # Determine PII type if present
                    pii_type = self._extract_pii_type(snippet)

                    issues.append(
                        PrivacyViolation(
                            severity=self._get_severity(violation_type),
                            violation_type=violation_type,
                            description=self._get_description(violation_type),
                            line_number=line_number,
                            code_snippet=snippet,
                            recommendation=self._get_recommendation(violation_type),
                            pii_type=pii_type,
                            compliance_frameworks=self._get_applicable_frameworks(
                                pii_type or "", compliance_frameworks
                            ),
                        )
                    )

        # Check for hardcoded PII patterns
        for pii_type, patterns in self.pii_patterns.items():
            for pattern in patterns:
                for match in re.finditer(pattern, content):
                    line_number = content[: match.start()].count("\n") + 1
                    line_content = lines[line_number - 1] if line_number <= len(lines) else ""

                    # Skip if in comments
                    stripped = line_content.strip()
                    if stripped.startswith(("//", "#", "*", "/*")):
                        continue

                    # Skip if appears to be in test/mock data
                    if "test" in file_path.lower() or "mock" in file_path.lower():
                        continue

                    issues.append(
                        PrivacyViolation(
                            severity="high" if pii_type in ["ssn", "credit_card"] else "medium",
                            violation_type="hardcoded_pii",
                            description=f"Hardcoded {pii_type.replace('_', ' ')} detected",
                            line_number=line_number,
                            code_snippet=match.group(0)[:50] + "...",
                            recommendation=self._get_pii_recommendation(pii_type),
                            pii_type=pii_type,
                            compliance_frameworks=self._get_applicable_frameworks(
                                pii_type, compliance_frameworks
                            ),
                        )
                    )

        return issues

    def _extract_pii_type(self, text: str) -> Optional[str]:
        """Extract PII type from code snippet"""
        text_lower = text.lower()
        for pii_type in ["email", "ssn", "password", "phone", "card", "token"]:
            if pii_type in text_lower:
                return pii_type
        return None

    def _get_severity(self, violation_type: str) -> str:
        """Get severity for violation type"""
        severity_map = {
            "pii_logging": "critical",
            "missing_encryption": "high",
            "insecure_storage": "high",
            "data_retention": "medium",
            "missing_consent": "medium",
            "hardcoded_pii": "high",
        }
        return severity_map.get(violation_type, "medium")

    def _get_description(self, violation_type: str) -> str:
        """Get description for violation type"""
        descriptions = {
            "pii_logging": "PII data being logged - may expose sensitive information in logs",
            "missing_encryption": "Sensitive data stored without encryption",
            "insecure_storage": "Sensitive data stored in insecure location (localStorage, cookies)",
            "data_retention": "Missing or disabled data retention policy",
            "missing_consent": "Analytics/tracking without apparent consent mechanism",
        }
        return descriptions.get(violation_type, f"Privacy violation: {violation_type}")

    def _get_recommendation(self, violation_type: str) -> str:
        """Get recommendation for violation type"""
        recommendations = {
            "pii_logging": (
                "Never log PII. Use masking (e.g., email: user@***.com) or "
                "remove PII from log statements entirely."
            ),
            "missing_encryption": (
                "Encrypt sensitive data at rest using AES-256 or similar. "
                "Use environment variables for secrets."
            ),
            "insecure_storage": (
                "Use secure, httpOnly cookies for tokens. "
                "Never store passwords or sensitive data in localStorage."
            ),
            "data_retention": (
                "Implement data retention policy. Automatically delete old data. "
                "GDPR requires data minimization."
            ),
            "missing_consent": (
                "Implement consent management (cookie banner, opt-in). "
                "Comply with GDPR/CCPA consent requirements."
            ),
        }
        return recommendations.get(violation_type, "Review data privacy practices")

    def _get_pii_recommendation(self, pii_type: str) -> str:
        """Get recommendation for PII type"""
        recommendations = {
            "email": "Store emails encrypted. Hash if only for verification.",
            "phone": "Store phone numbers encrypted. Use for 2FA securely.",
            "ssn": "NEVER store SSN in code. Use tokenization service.",
            "credit_card": "Use PCI-compliant payment processor. Never store card numbers.",
            "ip_address": "Anonymize IP addresses for GDPR compliance.",
            "api_key": "Use environment variables or secret manager. Never commit secrets.",
            "password": "Use environment variables. Never hardcode passwords.",
        }
        return recommendations.get(pii_type, "Encrypt or remove sensitive data")

    async def analyze_data_privacy(
        self,
        file_path: str,
        content: str,
        compliance_frameworks: Optional[List[str]] = None,
    ) -> List[PrivacyViolation]:
        """Analyze a file for data privacy violations"""
        issues = []

        # Use configured compliance frameworks or all
        frameworks = compliance_frameworks or list(self.COMPLIANCE_FRAMEWORKS.keys())

        # Pattern-based detection
        pattern_issues = self._detect_pattern_issues(content, file_path, frameworks)
        issues.extend(pattern_issues)

        # AI-based detection for more complex issues
        if self.config.enable_privacy_analysis and content.strip():
            try:
                framework_names = ", ".join(
                    self.COMPLIANCE_FRAMEWORKS[f]["name"]
                    for f in frameworks
                    if f in self.COMPLIANCE_FRAMEWORKS
                )

                prompt = f"""You are a data privacy and compliance expert. Analyze this code for privacy violations.

File: {file_path}
Compliance Frameworks: {framework_names}

Code:
```
{content[:25000]}
```

Identify privacy violations including:
- PII (Personally Identifiable Information) being logged or exposed
- Sensitive data stored without encryption
- Missing consent mechanisms for data collection
- Data retention policy violations
- Insecure data transmission
- Hardcoded credentials or API keys
- Violations of specific compliance frameworks (GDPR, HIPAA, PCI-DSS, CCPA)

For each issue, provide:
- type: Category (pii_logging, missing_encryption, consent, retention, transmission, credentials)
- severity: critical, high, medium, or low
- pii_type: Type of PII if applicable (email, ssn, phone, credit_card, etc.)
- line_number: Line number if applicable
- description: Clear description of the issue
- recommendation: How to fix it
- compliance: Which compliance framework(s) this violates

Respond in JSON format:
{{
    "issues": [
        {{
            "type": "...",
            "severity": "...",
            "pii_type": "...",
            "line_number": ...,
            "description": "...",
            "recommendation": "...",
            "compliance": ["GDPR", "..."]
        }}
    ]
}}"""

                response = await self._call_ai_with_retry(prompt)

                # Parse JSON response
                import json

                json_match = re.search(r"\{[\s\S]*\}", response)
                if json_match:
                    try:
                        result = json.loads(json_match.group(0))
                        for issue_data in result.get("issues", []):
                            line_num = issue_data.get("line_number")
                            if not any(
                                i.line_number == line_num
                                and i.violation_type == issue_data.get("type")
                                for i in issues
                            ):
                                issues.append(
                                    PrivacyViolation(
                                        severity=issue_data.get("severity", "medium"),
                                        violation_type=issue_data.get("type", "unknown"),
                                        description=issue_data.get("description", ""),
                                        line_number=line_num,
                                        code_snippet=None,
                                        recommendation=issue_data.get("recommendation", ""),
                                        pii_type=issue_data.get("pii_type"),
                                        compliance_frameworks=issue_data.get("compliance", []),
                                    )
                                )
                    except json.JSONDecodeError:
                        pass

            except Exception as e:
                print(f"⚠️  Error in AI privacy analysis for {file_path}: {e}")

        return issues
