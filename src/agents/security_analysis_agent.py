"""
Agent d'analyse de sécurité (SSA)

Utilise les Structured Outputs de Gemini pour garantir des réponses validées.
"""

import os
import re
import json
import asyncio
from typing import List, Optional

from src.agents.base_agent import BaseAgent
from src.core.config import AnalysisConfig
from src.models.data_models import SecurityIssue
from src.models.analysis_schemas import SecurityAnalysisResult, SecurityIssue as SecurityIssueSchema


class SecurityAnalysisAgent(BaseAgent):
    """Agent d'analyse de sécurité (SSA)"""

    def __init__(self, config: AnalysisConfig, doc_searcher=None, progress_manager=None):
        super().__init__(config, progress_manager)
        self.doc_searcher = doc_searcher

        # Patterns de sécurité communs
        self.security_patterns = {
            "sql_injection": [
                r'execute\s*\(\s*["\'].*\+.*["\']',
                r'query\s*\(\s*["\'].*\+.*["\']',
                r"\.format\s*\(.*SELECT",
                r'f["\'].*SELECT.*\{',
            ],
            "xss": [
                r"innerHTML\s*=",
                r"dangerouslySetInnerHTML",
                r"eval\s*\(",
                r"document\.write\s*\(",
            ],
            "hardcoded_secrets": [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'api[_-]?key\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][^"\']+["\']',
                r'private[_-]?key\s*=\s*["\'][^"\']+["\']',
            ],
            "weak_crypto": [
                r"MD5\s*\(",
                r"SHA1\s*\(",
                r"DES\s*\(",
                r"RC4\s*\(",
            ],
            "insecure_random": [
                r"Math\.random\s*\(",
                r"random\.randint",
                r"Random\(\)",
            ],
        }

    def _detect_pattern_issues(
        self, content: str, file_path: str, language: str
    ) -> List[SecurityIssue]:
        """Détecte les problèmes de sécurité via patterns"""
        issues = []

        for issue_type, patterns in self.security_patterns.items():
            for pattern in patterns:
                for i, line in enumerate(content.split("\n"), 1):
                    if re.search(pattern, line, re.IGNORECASE):
                        # Ignorer les commentaires
                        stripped = line.strip()
                        if (
                            stripped.startswith("//")
                            or stripped.startswith("#")
                            or stripped.startswith("*")
                        ):
                            continue

                        severity = (
                            "high"
                            if issue_type in ["sql_injection", "xss", "hardcoded_secrets"]
                            else "medium"
                        )
                        issues.append(
                            SecurityIssue(
                                severity=severity,
                                issue_type=issue_type,
                                description=f"Pattern suspect détecté: {issue_type}",
                                line_number=i,
                                code_snippet=line.strip()[:100],
                                recommendation=self._get_recommendation(issue_type),
                            )
                        )

        return issues

    def _get_recommendation(self, issue_type: str) -> str:
        """Retourne une recommandation pour un type d'issue"""
        recommendations = {
            "sql_injection": "Utiliser des requêtes paramétrées ou un ORM",
            "xss": "Utiliser l'échappement approprié ou des bibliothèques comme DOMPurify",
            "hardcoded_secrets": "Utiliser des variables d'environnement ou un gestionnaire de secrets",
            "weak_crypto": "Utiliser des algorithmes modernes (SHA-256, AES-256)",
            "insecure_random": "Utiliser crypto.getRandomValues() ou secrets module",
        }
        return recommendations.get(issue_type, "Réviser le code pour la sécurité")

    async def analyze_security(
        self, file_path: str, content: str, language: str
    ) -> List[SecurityIssue]:
        """Analyse la sécurité d'un fichier"""
        issues = []

        # Détection par patterns
        pattern_issues = self._detect_pattern_issues(content, file_path, language)
        issues.extend(pattern_issues)

        # Analyse avec Gemini pour les problèmes plus subtils
        if self.config.enable_security_analysis and content.strip():
            try:
                relative_path = os.path.relpath(file_path, self.config.root_dir).replace("\\", "/")

                # Recherche de documentation de sécurité si activé
                web_docs = ""
                if self.doc_searcher:
                    try:
                        web_docs = await self.doc_searcher.search_documentation(
                            language, file_path, f"security best practices {language}"
                        )
                    except:
                        pass

                prompt = f"""Tu es un expert en sécurité applicative. Analyse ce code pour détecter les vulnérabilités de sécurité.

Fichier: {relative_path}
Langage: {language}
{web_docs}

Code à analyser:
```
{content[:30000]}
```

Identifie TOUTES les vulnérabilités de sécurité potentielles, notamment:
- Injections (SQL, NoSQL, Command, LDAP)
- Cross-Site Scripting (XSS)
- Authentification faible ou manquante
- Gestion des sessions non sécurisée
- Secrets codés en dur
- Cryptographie faible
- Gestion d'erreurs exposant des informations sensibles
- CORS mal configuré
- Validation d'entrée insuffisante
- Problèmes de permissions/accès

Pour chaque vulnérabilité trouvée, fournis:
- **type**: Type de vulnérabilité (XSS, SQLi, SSRF, etc.)
- **severity**: critical, high, medium, low, ou info
- **line_number**: Numéro de ligne si applicable
- **description**: Description précise du problème
- **recommendation**: Comment corriger le problème
- **cwe_id**: Identifiant CWE si applicable (ex: CWE-79)
- **owasp_category**: Catégorie OWASP si applicable (ex: A01:2021)

Inclus également un résumé global et un score de risque (0-10)."""

                # Utiliser les Structured Outputs si disponibles (Gemini)
                if self.config.enable_structured_outputs:
                    try:
                        result = await self._call_ai_structured(prompt, SecurityAnalysisResult)
                        for issue_schema in result.issues:
                            issues.append(
                                SecurityIssue(
                                    severity=issue_schema.severity.value,
                                    issue_type=issue_schema.type,
                                    description=issue_schema.description,
                                    line_number=issue_schema.line_number,
                                    code_snippet=issue_schema.code_snippet,
                                    recommendation=issue_schema.recommendation,
                                    cwe_id=issue_schema.cwe_id,
                                    owasp_category=issue_schema.owasp_category,
                                )
                            )
                    except Exception as e:
                        # Fallback vers le parsing manuel si échec
                        pass
                else:
                    # Fallback: parsing JSON manuel pour OpenAI/Claude
                    response_text = await self._call_gemini_with_retry(prompt)
                    response_text = response_text.strip()
                    # Extraire le JSON de la réponse (peut être dans un bloc de code)
                    json_match = re.search(r'\{[^{}]*"issues"[^{}]*\}', response_text, re.DOTALL)
                    if json_match:
                        try:
                            result = json.loads(json_match.group(0))
                            for issue_data in result.get("issues", []):
                                issues.append(
                                    SecurityIssue(
                                        severity=issue_data.get("severity", "medium"),
                                        issue_type=issue_data.get("type", "unknown"),
                                        description=issue_data.get("description", ""),
                                        line_number=issue_data.get("line"),
                                        code_snippet=None,
                                        recommendation=issue_data.get("recommendation", ""),
                                    )
                                )
                        except json.JSONDecodeError:
                            pass

            except Exception as e:
                print(f"⚠️  Erreur lors de l'analyse de sécurité pour {file_path}: {e}")

        return issues
