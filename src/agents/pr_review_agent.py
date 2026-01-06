"""
Agent de revue de Pull Request

Analyse les PRs avec plusieurs providers AI et produit un consensus sur les issues détectées.
"""

import asyncio
import hashlib
from typing import Dict, List, Optional, Tuple

from src.agents.base_agent import BaseAgent
from src.core.ai_providers import AIProvider, create_ai_provider
from src.core.config import AnalysisConfig
from src.core.progress import ProgressManager
from src.models.pr_models import (
    PRComment,
    PRFile,
    PRInfo,
    PRIssue,
    PRIssueSeverity,
    PRIssueType,
    PRReviewResult,
)
from src.models.pr_schemas import PRAnalysisResultSchema, PRIssueSchema


class PRReviewAgent(BaseAgent):
    """
    Agent pour la revue de Pull Requests avec analyse multi-providers.

    Supporte le mode consensus où seules les issues trouvées par TOUS les providers
    sont retenues, réduisant ainsi les faux positifs.
    """

    def __init__(
        self,
        config: AnalysisConfig,
        providers: List[str],
        api_keys: Dict[str, str],
        consensus_mode: bool = True,
        progress_manager: Optional[ProgressManager] = None,
    ):
        """
        Initialise l'agent de revue de PR.

        Args:
            config: Configuration d'analyse
            providers: Liste des providers AI à utiliser
            api_keys: Dictionnaire provider -> api_key
            consensus_mode: Si True, ne retient que les issues trouvées par tous
            progress_manager: Gestionnaire de progression (optionnel)
        """
        super().__init__(config, progress_manager)
        self.providers_list = providers
        self.api_keys = api_keys
        self.consensus_mode = consensus_mode
        self.ai_providers: Dict[str, AIProvider] = {}

        self._init_providers()

    def _init_providers(self) -> None:
        """Initialise les providers AI configurés."""
        default_models = {
            "gemini": "gemini-2.0-flash",
            "openai": "gpt-4o",
            "claude": "claude-3-5-sonnet-20241022",
        }

        for provider_name in self.providers_list:
            if provider_name not in self.api_keys:
                continue

            model = self.config.ai_model or default_models.get(provider_name, "")
            # Si le modèle configuré n'est pas compatible, utiliser le default
            if self.config.ai_provider != provider_name:
                model = default_models.get(provider_name, model)

            self.ai_providers[provider_name] = create_ai_provider(
                provider=provider_name,
                api_key=self.api_keys[provider_name],
                model=model,
                timeout_seconds=self.config.timeout_seconds,
                max_retries=self.config.max_retries,
            )

    async def analyze_pr_diff(
        self,
        pr_info: PRInfo,
        diff_content: str,
        files_changed: List[PRFile],
    ) -> PRReviewResult:
        """
        Analyse le diff d'une PR avec tous les providers configurés.

        Args:
            pr_info: Informations sur la PR
            diff_content: Contenu du diff complet
            files_changed: Liste des fichiers modifiés

        Returns:
            PRReviewResult avec les issues détectées
        """
        if self.progress_manager:
            self.progress_manager.update_status(
                f"Analyse de la PR #{pr_info.pr_number} avec {len(self.ai_providers)} provider(s)..."
            )

        # Analyser avec chaque provider en parallèle
        tasks = []
        for provider_name, provider in self.ai_providers.items():
            tasks.append(
                self._analyze_with_provider(
                    provider_name=provider_name,
                    provider=provider,
                    pr_info=pr_info,
                    diff_content=diff_content,
                    files_changed=files_changed,
                )
            )

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Collecter les résultats par provider
        provider_issues: Dict[str, List[PRIssue]] = {}
        total_before_consensus = 0

        for i, (provider_name, _) in enumerate(self.ai_providers.items()):
            result = results[i]
            if isinstance(result, Exception):
                if self.progress_manager:
                    self.progress_manager.print_warning(
                        f"Erreur avec {provider_name}: {str(result)}"
                    )
                provider_issues[provider_name] = []
            else:
                provider_issues[provider_name] = result
                total_before_consensus += len(result)

        # Appliquer le consensus si activé
        if self.consensus_mode and len(provider_issues) > 1:
            final_issues = self._compute_consensus(provider_issues)
        else:
            # Sans consensus, fusionner toutes les issues
            final_issues = []
            seen_ids = set()
            for issues in provider_issues.values():
                for issue in issues:
                    if issue.id not in seen_ids:
                        final_issues.append(issue)
                        seen_ids.add(issue.id)

        # Générer le résumé
        summary = await self._generate_summary(pr_info, final_issues, diff_content)

        # Générer les commentaires inline
        inline_comments = self._generate_inline_comments(final_issues)

        # Calculer le score de risque et la recommandation
        risk_score, recommendation = self._calculate_risk_and_recommendation(final_issues)

        return PRReviewResult(
            pr_info=pr_info,
            issues=final_issues,
            summary=summary,
            providers_used=list(self.ai_providers.keys()),
            consensus_mode=self.consensus_mode,
            total_issues_before_consensus=total_before_consensus,
            inline_comments=inline_comments,
            risk_score=risk_score,
            approval_recommendation=recommendation,
        )

    async def _analyze_with_provider(
        self,
        provider_name: str,
        provider: AIProvider,
        pr_info: PRInfo,
        diff_content: str,
        files_changed: List[PRFile],
    ) -> List[PRIssue]:
        """
        Exécute l'analyse avec un provider spécifique.

        Args:
            provider_name: Nom du provider
            provider: Instance du provider AI
            pr_info: Informations sur la PR
            diff_content: Contenu du diff
            files_changed: Fichiers modifiés

        Returns:
            Liste des issues détectées
        """
        if self.progress_manager:
            self.progress_manager.update_status(f"Analyse avec {provider_name}...")

        prompt = self._build_review_prompt(pr_info, diff_content, files_changed)

        try:
            # Utiliser structured outputs si disponible
            response = await provider.generate_content_with_retry(prompt)

            # Parser la réponse
            issues = self._parse_ai_response(response, provider_name)

            if self.progress_manager:
                self.progress_manager.print_success(
                    f"{provider_name}: {len(issues)} issue(s) trouvée(s)"
                )

            return issues

        except Exception as e:
            if self.progress_manager:
                self.progress_manager.print_error(f"Erreur {provider_name}: {str(e)}")
            raise

    def _build_review_prompt(
        self,
        pr_info: PRInfo,
        diff_content: str,
        files_changed: List[PRFile],
    ) -> str:
        """
        Construit le prompt pour la revue de PR.

        Args:
            pr_info: Informations sur la PR
            diff_content: Contenu du diff
            files_changed: Fichiers modifiés

        Returns:
            Prompt formaté pour l'AI
        """
        files_summary = "\n".join(
            [f"- {f.path} (+{f.additions}/-{f.deletions}) [{f.status.value}]" for f in files_changed]
        )

        # Limiter la taille du diff si trop grand
        max_diff_chars = 50000
        if len(diff_content) > max_diff_chars:
            diff_content = diff_content[:max_diff_chars] + "\n\n... [diff tronqué] ..."

        return f"""Tu es un expert en revue de code. Analyse cette Pull Request et identifie les problèmes potentiels.

## Informations PR
- **Titre**: {pr_info.title}
- **Description**: {pr_info.description or "Aucune description"}
- **Branche**: {pr_info.head_branch} -> {pr_info.base_branch}
- **Fichiers modifiés**: {pr_info.files_count} (+{pr_info.additions}/-{pr_info.deletions})

## Fichiers modifiés
{files_summary}

## Diff
```diff
{diff_content}
```

## Instructions
Analyse le code et identifie:
1. **Bugs potentiels** - Erreurs logiques, edge cases non gérés
2. **Problèmes de sécurité** - Vulnérabilités, injection, exposition de données
3. **Performance** - Opérations coûteuses, optimisations manquées
4. **Bonnes pratiques** - Patterns recommandés, standards de code
5. **Logique** - Erreurs de raisonnement, conditions incorrectes
6. **Tests** - Cas de test manquants

## Format de réponse
Réponds en JSON avec ce format exact:
```json
{{
  "issues": [
    {{
      "file_path": "chemin/du/fichier.py",
      "line_number": 42,
      "line_end": null,
      "issue_type": "bug|security|performance|style|documentation|logic|test|best_practice",
      "severity": "critical|high|medium|low|info",
      "title": "Titre court de l'issue",
      "description": "Description détaillée du problème",
      "suggestion": "Comment corriger le problème",
      "code_snippet": "code concerné"
    }}
  ],
  "summary": "Résumé global de la revue",
  "risk_score": 5.0,
  "approval_recommendation": "COMMENT",
  "positive_points": ["Point positif 1", "Point positif 2"],
  "general_suggestions": ["Suggestion générale"]
}}
```

IMPORTANT:
- Sois précis sur les numéros de ligne (utilise les lignes du nouveau fichier, côté +)
- Ne signale que les vrais problèmes, pas les préférences de style mineures
- Fournis des suggestions actionables
- Le score de risque va de 0 (aucun risque) à 10 (critique)
"""

    def _parse_ai_response(self, response: str, provider_name: str) -> List[PRIssue]:
        """
        Parse la réponse JSON de l'AI.

        Args:
            response: Réponse brute de l'AI
            provider_name: Nom du provider

        Returns:
            Liste des issues parsées
        """
        import json

        # Nettoyer la réponse
        json_str = response.strip()
        if "```json" in json_str:
            start = json_str.find("```json") + 7
            end = json_str.find("```", start)
            json_str = json_str[start:end].strip()
        elif "```" in json_str:
            start = json_str.find("```") + 3
            end = json_str.find("```", start)
            json_str = json_str[start:end].strip()

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            # Essayer de trouver un objet JSON dans la réponse
            import re
            match = re.search(r'\{[\s\S]*\}', response)
            if match:
                try:
                    data = json.loads(match.group())
                except json.JSONDecodeError:
                    return []
            else:
                return []

        issues = []
        for issue_data in data.get("issues", []):
            try:
                # Générer un ID unique
                issue_id = self._generate_issue_id(
                    issue_data.get("file_path", ""),
                    issue_data.get("line_number"),
                    issue_data.get("title", ""),
                )

                # Parser le type d'issue
                issue_type_str = issue_data.get("issue_type", "logic").lower()
                try:
                    issue_type = PRIssueType(issue_type_str)
                except ValueError:
                    issue_type = PRIssueType.LOGIC

                # Parser la sévérité
                severity_str = issue_data.get("severity", "medium").lower()
                try:
                    severity = PRIssueSeverity(severity_str)
                except ValueError:
                    severity = PRIssueSeverity.MEDIUM

                issue = PRIssue(
                    id=issue_id,
                    file_path=issue_data.get("file_path", ""),
                    line_number=issue_data.get("line_number"),
                    line_end=issue_data.get("line_end"),
                    issue_type=issue_type,
                    severity=severity,
                    title=issue_data.get("title", "Issue détectée"),
                    description=issue_data.get("description", ""),
                    suggestion=issue_data.get("suggestion", ""),
                    code_snippet=issue_data.get("code_snippet"),
                    providers_found=[provider_name],
                )
                issues.append(issue)

            except Exception:
                continue

        return issues

    def _generate_issue_id(
        self,
        file_path: str,
        line_number: Optional[int],
        title: str,
    ) -> str:
        """Génère un ID unique pour une issue."""
        content = f"{file_path}:{line_number or 0}:{title}"
        hash_val = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"PR-{hash_val}"

    def _compute_consensus(
        self,
        results: Dict[str, List[PRIssue]],
    ) -> List[PRIssue]:
        """
        Calcule le consensus entre les résultats de plusieurs providers.

        Ne retient que les issues trouvées par TOUS les providers.

        Args:
            results: Dictionnaire provider -> liste d'issues

        Returns:
            Liste des issues en consensus
        """
        if len(results) <= 1:
            return list(results.values())[0] if results else []

        providers = list(results.keys())
        base_issues = results[providers[0]]
        consensus_issues = []

        for base_issue in base_issues:
            found_in_all = True
            matching_providers = [providers[0]]

            for other_provider in providers[1:]:
                found_match = False
                for other_issue in results[other_provider]:
                    if self._issues_match(base_issue, other_issue):
                        found_match = True
                        matching_providers.append(other_provider)
                        break

                if not found_match:
                    found_in_all = False
                    break

            if found_in_all:
                # Mettre à jour les providers ayant trouvé l'issue
                base_issue.providers_found = matching_providers
                consensus_issues.append(base_issue)

        return consensus_issues

    def _issues_match(self, a: PRIssue, b: PRIssue) -> bool:
        """
        Vérifie si deux issues font référence au même problème.

        Args:
            a: Première issue
            b: Deuxième issue

        Returns:
            True si les issues correspondent
        """
        # Même fichier
        if a.file_path != b.file_path:
            return False

        # Même type d'issue
        if a.issue_type != b.issue_type:
            return False

        # Proximité des lignes (dans un rayon de 3 lignes)
        if a.line_number and b.line_number:
            if abs(a.line_number - b.line_number) > 3:
                return False

        # Similarité du titre (optionnel, pour plus de précision)
        # On pourrait utiliser un calcul de similarité ici

        return True

    async def _generate_summary(
        self,
        pr_info: PRInfo,
        issues: List[PRIssue],
        diff_content: str,
    ) -> str:
        """
        Génère un résumé de la revue.

        Args:
            pr_info: Informations sur la PR
            issues: Issues détectées
            diff_content: Diff de la PR

        Returns:
            Résumé formaté en markdown
        """
        # Compter par sévérité
        severity_counts = {}
        for issue in issues:
            sev = issue.severity.value
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

        # Compter par type
        type_counts = {}
        for issue in issues:
            t = issue.issue_type.value
            type_counts[t] = type_counts.get(t, 0) + 1

        severity_str = ", ".join([f"{k}: {v}" for k, v in severity_counts.items()]) or "Aucune"
        type_str = ", ".join([f"{k}: {v}" for k, v in type_counts.items()]) or "Aucun"

        mode = "consensus" if self.consensus_mode else "union"
        providers_str = ", ".join(self.providers_list)

        summary = f"""## Résumé de la revue de PR

**PR #{pr_info.pr_number}**: {pr_info.title}

### Statistiques
- **Issues trouvées**: {len(issues)}
- **Par sévérité**: {severity_str}
- **Par type**: {type_str}
- **Mode d'analyse**: {mode}
- **Providers utilisés**: {providers_str}

### Fichiers analysés
- **Fichiers modifiés**: {pr_info.files_count}
- **Lignes ajoutées**: +{pr_info.additions}
- **Lignes supprimées**: -{pr_info.deletions}
"""

        if issues:
            summary += "\n### Issues détaillées\n\n"
            for issue in sorted(issues, key=lambda x: (
                ["critical", "high", "medium", "low", "info"].index(x.severity.value),
                x.file_path,
            )):
                emoji = {
                    "critical": "🔴",
                    "high": "🟠",
                    "medium": "🟡",
                    "low": "🔵",
                    "info": "ℹ️",
                }.get(issue.severity.value, "⚪")

                summary += f"- {emoji} **[{issue.severity.value.upper()}]** {issue.title}\n"
                summary += f"  - Fichier: `{issue.file_path}`"
                if issue.line_number:
                    summary += f" (ligne {issue.line_number})"
                summary += f"\n  - {issue.description}\n"
                summary += f"  - 💡 {issue.suggestion}\n\n"

        return summary

    def _generate_inline_comments(self, issues: List[PRIssue]) -> List[PRComment]:
        """
        Génère les commentaires inline à partir des issues.

        Args:
            issues: Liste des issues

        Returns:
            Liste des commentaires à poster
        """
        comments = []

        for issue in issues:
            if not issue.line_number:
                continue

            emoji = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🔵",
                "info": "ℹ️",
            }.get(issue.severity.value, "⚪")

            type_emoji = {
                "security": "🔒",
                "bug": "🐛",
                "performance": "⚡",
                "style": "🎨",
                "documentation": "📝",
                "logic": "🧠",
                "test": "🧪",
                "best_practice": "✨",
            }.get(issue.issue_type.value, "💬")

            body = f"""{emoji} **{issue.severity.value.upper()}** | {type_emoji} {issue.issue_type.value}

### {issue.title}

{issue.description}

**Suggestion**: {issue.suggestion}
"""

            if len(issue.providers_found) > 1:
                body += f"\n---\n*Trouvé par: {', '.join(issue.providers_found)}*"

            comments.append(
                PRComment(
                    file_path=issue.file_path,
                    line_number=issue.line_number,
                    body=body,
                    side="RIGHT",
                )
            )

        return comments

    def _calculate_risk_and_recommendation(
        self,
        issues: List[PRIssue],
    ) -> Tuple[float, str]:
        """
        Calcule le score de risque et la recommandation.

        Args:
            issues: Liste des issues

        Returns:
            Tuple (score de risque 0-10, recommandation)
        """
        if not issues:
            return 0.0, "APPROVE"

        # Poids par sévérité
        severity_weights = {
            PRIssueSeverity.CRITICAL: 10.0,
            PRIssueSeverity.HIGH: 6.0,
            PRIssueSeverity.MEDIUM: 3.0,
            PRIssueSeverity.LOW: 1.0,
            PRIssueSeverity.INFO: 0.5,
        }

        # Calcul du score
        total_weight = sum(severity_weights.get(issue.severity, 1.0) for issue in issues)
        risk_score = min(10.0, total_weight / max(1, len(issues)) * 2)

        # Recommandation basée sur les issues critiques/high
        critical_count = sum(1 for i in issues if i.severity == PRIssueSeverity.CRITICAL)
        high_count = sum(1 for i in issues if i.severity == PRIssueSeverity.HIGH)

        if critical_count > 0:
            recommendation = "REQUEST_CHANGES"
        elif high_count >= 2:
            recommendation = "REQUEST_CHANGES"
        elif high_count == 1 or len(issues) > 5:
            recommendation = "COMMENT"
        else:
            recommendation = "COMMENT"

        return round(risk_score, 1), recommendation

    def generate_summary_comment(self, result: PRReviewResult) -> str:
        """
        Génère le commentaire de résumé à poster sur la PR.

        Args:
            result: Résultat de la revue

        Returns:
            Commentaire formaté en markdown
        """
        emoji_map = {
            "APPROVE": "✅",
            "REQUEST_CHANGES": "🔴",
            "COMMENT": "💬",
        }

        emoji = emoji_map.get(result.approval_recommendation, "💬")

        header = f"""## {emoji} Revue Aetheris

**Score de risque**: {result.risk_score}/10
**Recommandation**: {result.approval_recommendation}
**Issues trouvées**: {len(result.issues)}
"""

        if result.consensus_mode:
            header += f"\n*Mode consensus actif - {result.total_issues_before_consensus} issues détectées, {len(result.issues)} en consensus*\n"

        header += f"\n*Analysé par: {', '.join(result.providers_used)}*\n\n---\n"

        return header + result.summary
