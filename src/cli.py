#!/usr/bin/env python3
"""
Aetheris by Adryan - Interface en ligne de commande
"""

import argparse
import asyncio
import json
import os
import sys
from typing import List
from typing import Optional

from rich.console import Console
from rich.prompt import Confirm

# Configuration du logging et encodage UTF-8
from src.core.logger import log_print
from src.core.logger import setup_utf8_encoding

setup_utf8_encoding()

try:
    import google.genai as _genai  # noqa: F401 - Vérifie la disponibilité du SDK
except ImportError as e:
    print(f"❌ Dépendances manquantes: {e}")
    print("   Installez avec: pip install -r requirements.txt")
    sys.exit(1)

# Import de CodeAnalyzer depuis le module dédié
from src.core.analyzer import CodeAnalyzer

# Import de la configuration depuis le module dédié
from src.core.change_detector import ChangeDetector
from src.core.config import AnalysisConfig
from src.core.config import load_env_file
from src.core.config import TimeoutConfig
from src.core.config import TimeoutParseError
from src.core.progress import ProgressManager


def parse_changed_files(files_input: Optional[str]) -> List[str]:
    """Parse les fichiers modifiés depuis une chaîne JSON ou une liste séparée par des virgules"""
    if not files_input:
        return []

    try:
        # Essayer de parser comme JSON (depuis GitHub Actions)
        files = json.loads(files_input)
        if isinstance(files, list):
            return files
    except (json.JSONDecodeError, TypeError):
        pass

    # Sinon, traiter comme une liste séparée par des virgules
    files = [f.strip() for f in files_input.split(",") if f.strip()]
    return files


def setup_analysis_parser(subparsers):
    """Configure le parser pour la sous-commande analysis"""
    analysis_parser = subparsers.add_parser(
        "analysis",
        help="Lancer une analyse de code",
        description="Analyse de code avec plusieurs agents coopérants",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  # Analyse complète de la codebase
  aetheris analysis

  # Analyser uniquement les fichiers modifiés (depuis GitHub Actions)
  aetheris analysis --changed-files-only --files '["src/file1.py", "src/file2.py"]'

  # Analyser une liste de fichiers spécifiques
  aetheris analysis --files src/file1.py,src/file2.py

  # Analyser les fichiers d'une PR
  aetheris analysis --changed-files-only --pr-number 123
        """,
    )

    analysis_parser.add_argument(
        "--changed-files-only",
        action="store_true",
        help="Analyser uniquement les fichiers modifiés (pour PR/commits)",
    )

    analysis_parser.add_argument(
        "--files",
        type=str,
        default=None,
        help="Liste de fichiers à analyser (JSON array ou séparés par virgules). Utilisé avec --changed-files-only",
    )

    analysis_parser.add_argument(
        "--pr-number", type=int, default=None, help="Numéro de PR (optionnel, pour information)"
    )

    analysis_parser.add_argument(
        "--timeout",
        "-t",
        type=str,
        default=None,
        help=(
            "Timeout for the entire analysis. Formats: 3600 (seconds), 30m (minutes), "
            "2h (hours), 0 or no-limit (unlimited). Default: 60m"
        ),
    )

    analysis_parser.add_argument(
        "--reanalyze",
        "-r",
        action="store_true",
        help=(
            "Reanalyze only files modified since the last analysis. "
            "Detects changes via git or file timestamps and updates existing reports."
        ),
    )

    return analysis_parser


def setup_issues_parser(subparsers):
    """Configure le parser pour la sous-commande issues"""
    issues_parser = subparsers.add_parser(
        "issues",
        help="Create GitHub issues from analysis reports",
        description="Create GitHub issues from Aetheris analysis reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create issues from all analysis reports
  aetheris issues

  # Preview issues without creating them
  aetheris issues --dry-run

  # Create issues with custom labels
  aetheris issues --labels security,sprint-42

  # Assign issues to a user
  aetheris issues --assignee username

  # Create issues in a specific repository
  aetheris issues --repo owner/repo

  # Process only a specific report
  aetheris issues --from-report docs/analyses/analyzer.md
        """,
    )

    issues_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview issues without creating them",
    )

    issues_parser.add_argument(
        "--labels",
        type=str,
        default=None,
        help="Additional labels to add (comma-separated)",
    )

    issues_parser.add_argument(
        "--assignee",
        type=str,
        default=None,
        help="GitHub username to assign issues to",
    )

    issues_parser.add_argument(
        "--repo",
        type=str,
        default=None,
        help="Target repository (owner/repo format)",
    )

    issues_parser.add_argument(
        "--from-report",
        type=str,
        default=None,
        help="Process only this specific analysis report file",
    )

    return issues_parser


async def run_analysis(args):
    """Exécute l'analyse de code"""
    log_print("=" * 60)
    log_print("🚀 Aetheris by Adryan - Démarrage de l'analyse de code")
    log_print("=" * 60)
    log_print()

    # Charger le fichier .env s'il existe
    env_vars = load_env_file(".env")

    # Déterminer le provider AI (défaut: gemini)
    ai_provider = (env_vars.get("AI_PROVIDER") or os.getenv("AI_PROVIDER", "gemini")).lower()

    # Récupérer la clé API selon le provider
    api_key_env_vars = {
        "gemini": "GEMINI_API_KEY",
        "openai": "OPENAI_API_KEY",
        "claude": "ANTHROPIC_API_KEY",
    }

    api_key_name = api_key_env_vars.get(ai_provider, "GEMINI_API_KEY")
    ai_api_key = env_vars.get(api_key_name) or os.getenv(api_key_name)

    if not ai_api_key:
        log_print(f"❌ Variable d'environnement {api_key_name} non définie")
        log_print(f"   Provider sélectionné: {ai_provider}")
        log_print("   Options:")
        log_print(f"   1. Créez un fichier .env avec: {api_key_name}=votre_cle")
        log_print(f"   2. Ou définissez-la avec: export {api_key_name}=votre_cle (Linux/Mac)")
        log_print(f"   3. Ou définissez-la avec: $env:{api_key_name}='votre_cle' (PowerShell)")
        log_print("   4. Ou configurez-la dans GitHub Secrets (pour GitHub Actions)")
        sys.exit(1)

    # Afficher la clé API masquée pour debug
    masked_key = ai_api_key[:8] + "..." + ai_api_key[-4:] if len(ai_api_key) > 12 else "***"
    log_print(f"🔑 Clé API: {masked_key} (longueur: {len(ai_api_key)})")

    # Valider la clé API avec un test simple
    if ai_provider == "gemini":
        log_print("🔄 Validation de la clé API Gemini...")
        try:
            from google import genai

            test_client = genai.Client(api_key=ai_api_key)
            # Test avec un modèle simple
            test_response = test_client.models.generate_content(
                model="gemini-2.0-flash", contents="Say 'OK' if you can hear me."
            )
            log_print(f"✅ Clé API validée: {test_response.text[:50]}...")
        except Exception as e:
            log_print(f"❌ Erreur de validation de la clé API: {e}")
            log_print(
                "   Vérifiez que votre clé API est valide sur: https://aistudio.google.com/apikey"
            )
            sys.exit(1)

    # Récupérer le modèle (défaut selon provider)
    from src.core.config import get_default_model

    default_model = get_default_model(ai_provider)
    ai_model = env_vars.get("AI_MODEL") or os.getenv("AI_MODEL", default_model)

    # Appliquer les variables du .env à l'environnement pour les autres configs
    for key, value in env_vars.items():
        if key not in os.environ:
            os.environ[key] = value

    # Parser les fichiers modifiés depuis les arguments ou l'environnement GitHub Actions
    changed_files: List[str] = []
    analyze_changed_only = args.changed_files_only
    reanalyze_mode = getattr(args, "reanalyze", False)

    # Handle --reanalyze flag (v2.6.1)
    if reanalyze_mode:
        log_print("🔄 Mode reanalyze: détection des fichiers modifiés depuis la dernière analyse...")
        detector = ChangeDetector(
            metrics_dir=os.getenv("OUTPUT_DIR", "docs/analyses") + "/../metrics",
            root_dir=os.getenv("ROOT_DIR", "."),
        )
        # Use proper metrics directory path
        detector.metrics_dir = "docs/metrics"

        last_analysis = detector.get_last_analysis_info()
        if last_analysis:
            log_print(f"📅 Dernière analyse: {last_analysis.timestamp.strftime('%Y-%m-%d %H:%M')}")
            log_print(f"📁 Fichier métriques: {last_analysis.metrics_file}")

            changed_files, detection_method = detector.get_changed_files(last_analysis)
            log_print(f"🔍 Méthode de détection: {detection_method}")

            if changed_files:
                log_print(f"📝 {len(changed_files)} fichier(s) modifié(s) détecté(s)")
                analyze_changed_only = True
            else:
                log_print("✅ Aucun fichier modifié depuis la dernière analyse")
                log_print("   Utilisez 'aetheris analysis' sans --reanalyze pour une analyse complète")
                sys.exit(0)

            # Check for deleted files
            deleted_files = detector.get_deleted_files(last_analysis)
            if deleted_files:
                log_print(f"🗑️  {len(deleted_files)} fichier(s) supprimé(s) depuis la dernière analyse")
        else:
            log_print("⚠️  Aucune analyse précédente trouvée, lancement d'une analyse complète...")
            # Continue with full analysis

    elif analyze_changed_only:
        # Priorité: argument --files, puis variable d'environnement CHANGED_FILES
        files_input = args.files or os.getenv("CHANGED_FILES")
        changed_files = parse_changed_files(files_input)

        if not changed_files:
            log_print("⚠️  Mode --changed-files-only activé mais aucun fichier spécifié")
            log_print("   Utilisez --files ou définissez CHANGED_FILES dans l'environnement")
            sys.exit(1)

    # Obtenir le numéro de PR depuis les arguments ou l'environnement GitHub
    pr_number = args.pr_number
    if not pr_number:
        pr_number_str = os.getenv("PR_NUMBER")
        if pr_number_str:
            try:
                pr_number = int(pr_number_str)
            except ValueError:
                pass

    # Parse timeout configuration (v2.6.1)
    timeout_config = None
    timeout_arg = getattr(args, "timeout", None)
    if timeout_arg:
        try:
            timeout_config = TimeoutConfig.parse(timeout_arg)
            log_print(f"⏱️  Timeout: {timeout_config.format_human()}")
        except TimeoutParseError as e:
            log_print(f"❌ {e}")
            sys.exit(1)

    config = AnalysisConfig(
        ai_provider=ai_provider,
        ai_api_key=ai_api_key,
        ai_model=ai_model,
        batch_size=int(os.getenv("BATCH_SIZE", "10")),
        max_retries=int(os.getenv("MAX_RETRIES", "3")),
        timeout_seconds=int(os.getenv("TIMEOUT_SECONDS", "60")),
        output_dir=os.getenv("OUTPUT_DIR", "docs/analyses"),
        architecture_report_path=os.getenv("ARCHITECTURE_REPORT", "docs/architecture_overview.md"),
        root_dir=os.getenv("ROOT_DIR", "."),
        enable_web_search=os.getenv("ENABLE_WEB_SEARCH", "true").lower() == "true",
        max_web_results=int(os.getenv("MAX_WEB_RESULTS", "3")),
        enable_security_analysis=os.getenv("ENABLE_SECURITY_ANALYSIS", "true").lower() == "true",
        enable_metrics_analysis=os.getenv("ENABLE_METRICS_ANALYSIS", "true").lower() == "true",
        enable_dependency_vulnerability=os.getenv("ENABLE_DEPENDENCY_VULNERABILITY", "true").lower()
        == "true",
        enable_code_generation=os.getenv("ENABLE_CODE_GENERATION", "true").lower() == "true",
        analyze_changed_files_only=analyze_changed_only,
        changed_files=changed_files,
        pr_number=pr_number,
        show_reasoning=os.getenv("SHOW_REASONING", "false").lower() == "true",
        # Gemini Advanced Features (v2.2.0)
        enable_structured_outputs=os.getenv("ENABLE_STRUCTURED_OUTPUTS", "true").lower() == "true",
        enable_thinking=os.getenv("ENABLE_THINKING", "false").lower() == "true",
        thinking_budget=int(os.getenv("THINKING_BUDGET", "1024")),
        enable_code_execution=os.getenv("ENABLE_CODE_EXECUTION", "false").lower() == "true",
        enable_function_calling=os.getenv("ENABLE_FUNCTION_CALLING", "false").lower() == "true",
        enable_context_caching=os.getenv("ENABLE_CONTEXT_CACHING", "true").lower() == "true",
        cache_ttl_seconds=int(os.getenv("CONTEXT_CACHE_TTL_SECONDS", "3600")),
        enable_batch_mode=os.getenv("ENABLE_BATCH_MODE", "false").lower() == "true",
        enable_google_search=os.getenv("ENABLE_GOOGLE_SEARCH", "false").lower() == "true",
        # Timeout configuration (v2.6.1)
        timeout_config=timeout_config,
    )

    log_print(f"📁 Répertoire racine: {config.root_dir}")
    log_print(f"📂 Répertoire de sortie: {config.output_dir}")
    log_print(f"🤖 Provider AI: {config.ai_provider.upper()}")
    log_print(f"🤖 Modèle: {config.ai_model}")

    if reanalyze_mode and changed_files:
        log_print(
            f"🔍 Mode: Reanalyse des fichiers modifiés ({len(changed_files)} fichier(s))"
        )
    elif analyze_changed_only:
        log_print(
            f"🔍 Mode: Analyse des fichiers modifiés uniquement ({len(changed_files)} fichier(s))"
        )
        if pr_number:
            log_print(f"📋 PR #{pr_number}")
    else:
        log_print("🔍 Mode: Analyse complète de la codebase")

    log_print()

    # Créer ProgressManager si on est dans un terminal interactif
    progress_manager = ProgressManager(enabled=True)

    analyzer = CodeAnalyzer(config, progress_manager=progress_manager)
    await analyzer.run()

    log_print()
    log_print("=" * 60)
    log_print("✅ Analyse terminée avec succès!")
    log_print("=" * 60)


def setup_fix_parser(subparsers):
    """Configure le parser pour la sous-commande fix"""
    fix_parser = subparsers.add_parser(
        "fix",
        help="Corriger les bugs détectés avec Claude Code",
        description="Lance Claude Code pour corriger les bugs (séquentiel ou parallèle)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  # Tester la connexion à Claude Code
  aetheris fix --test

  # Corriger les bugs depuis le cache existant (mode séquentiel)
  aetheris fix

  # Mode automatique (sans confirmations)
  aetheris fix --auto

  # Mode parallèle: 10 corrections simultanées (RECOMMANDÉ pour beaucoup de bugs)
  aetheris fix --auto --batch-size 10

  # Mode parallèle avec timeout personnalisé (5 min par bug)
  aetheris fix --auto -b 10 --timeout 300

  # Ouvrir Claude Code dans une fenêtre terminal (mode séquentiel uniquement)
  aetheris fix --terminal

  # Corriger uniquement les bugs critiques et high
  aetheris fix --severity high

  # Lancer une analyse puis corriger en parallèle
  aetheris fix --analyze-first --batch-size 10
        """,
    )

    fix_parser.add_argument(
        "--analyze-first",
        action="store_true",
        help="Lancer une analyse avant de corriger",
    )

    fix_parser.add_argument(
        "--severity",
        choices=["critical", "high", "medium", "low"],
        default="medium",
        help="Sévérité minimale des bugs à corriger (défaut: medium)",
    )

    fix_parser.add_argument(
        "--auto",
        action="store_true",
        help="Mode automatique sans confirmations entre les bugs",
    )

    fix_parser.add_argument(
        "--terminal",
        action="store_true",
        help="Ouvrir Claude Code dans une nouvelle fenêtre terminal (au lieu du mode arrière-plan)",
    )

    fix_parser.add_argument(
        "--test",
        action="store_true",
        help="Tester la connexion à Claude Code sans corriger de bugs",
    )

    fix_parser.add_argument(
        "--batch-size",
        "-b",
        type=int,
        default=1,
        help="Nombre de corrections en parallèle (défaut: 1, max recommandé: 10)",
    )

    fix_parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Timeout par bug en secondes (défaut: 300)",
    )

    fix_parser.add_argument(
        "--retry-failed",
        action="store_true",
        help="Relancer uniquement les bugs qui ont échoué précédemment",
    )

    return fix_parser


async def run_issues(args):
    """Create GitHub issues from analysis reports."""
    from src.services.issue_creator import IssueCreator, IssueOptions

    console = Console()
    console.print()
    console.rule("[bold blue]🎫 Aetheris Issues - Create GitHub Issues from Analysis")
    console.print()

    # Parse custom labels
    custom_labels = []
    if args.labels:
        custom_labels = [label.strip() for label in args.labels.split(",") if label.strip()]

    # Create options
    options = IssueOptions(
        dry_run=args.dry_run,
        labels=custom_labels,
        assignee=args.assignee,
        repo=args.repo,
        from_report=args.from_report,
    )

    # Run issue creator
    creator = IssueCreator(repo=args.repo)
    await creator.run(options)


async def run_fix(args):
    """Exécute la correction de bugs avec Claude Code"""
    console = Console()

    console.print()
    console.rule("[bold blue]🔧 Aetheris Fix - Correction de bugs avec Claude Code")
    console.print()

    # Import des modules nécessaires
    from src.models.data_models import BugIdentifier
    from src.services.claude_code_integration import ClaudeCodeIntegration

    # Charger le fichier .env s'il existe
    env_vars = load_env_file(".env")
    root_dir = env_vars.get("ROOT_DIR") or os.getenv("ROOT_DIR", ".")
    output_dir = env_vars.get("OUTPUT_DIR") or os.getenv("OUTPUT_DIR", "docs/analyses")

    # Initialiser l'intégration Claude Code
    claude = ClaudeCodeIntegration(root_dir)

    # Mode test: vérifier la connexion à Claude Code
    if getattr(args, "test", False):
        console.print("[cyan]🔍 Test de Claude Code...[/cyan]")
        console.print()

        if not claude.is_available:
            console.print("[red]❌ Claude Code n'est pas installé ou introuvable[/red]")
            console.print()
            console.print("[yellow]Pour installer Claude Code:[/yellow]")
            console.print("  npm install -g @anthropic-ai/claude-code")
            sys.exit(1)

        console.print(f"[green]✅ Claude Code trouvé: {claude.claude_path}[/green]")

        test_ok, test_msg = claude.test_claude_code()
        if test_ok:
            console.print(f"[green]✅ {test_msg}[/green]")
            console.print()

            # Test avec un prompt simple
            console.print("[cyan]🧪 Test d'exécution avec un prompt simple...[/cyan]")
            exec_ok, exec_msg = claude.test_claude_code_execution(timeout=60)

            if exec_ok:
                console.print("[green]✅ Test réussi![/green]")
                console.print(f"[dim]{exec_msg}[/dim]")
            else:
                console.print(f"[red]❌ Échec du test: {exec_msg}[/red]")
                sys.exit(1)
        else:
            console.print(f"[red]❌ {test_msg}[/red]")
            sys.exit(1)

        sys.exit(0)

    # Vérifier si Claude Code est disponible
    if not claude.is_available:
        console.print("[red]❌ Claude Code n'est pas installé ou introuvable[/red]")
        console.print()
        console.print("[yellow]Pour installer Claude Code:[/yellow]")
        console.print("  npm install -g @anthropic-ai/claude-code")
        console.print()

        if not Confirm.ask("Voulez-vous continuer avec l'analyse seule?"):
            console.print("[yellow]Opération annulée.[/yellow]")
            sys.exit(1)

        # Continuer en mode analyse seule
        console.print("[yellow]Mode analyse seule activé (sans correction).[/yellow]")
        args.analyze_first = True

    # Chemin du cache des bugs
    bugs_cache_path = os.path.join(output_dir, ".bugs_cache.json")

    # Si --analyze-first ou pas de cache, lancer l'analyse
    if args.analyze_first or not os.path.exists(bugs_cache_path):
        console.print("[cyan]🔍 Lancement de l'analyse...[/cyan]")
        console.print()

        # Créer un args mock pour l'analyse
        class AnalysisArgs:
            changed_files_only = False
            files = None
            pr_number = None

        await run_analysis(AnalysisArgs())

        # Vérifier si le cache a été créé
        if not os.path.exists(bugs_cache_path):
            console.print("[yellow]⚠️  Aucun bug détecté ou cache non créé.[/yellow]")
            sys.exit(0)

    # Charger les bugs depuis le cache
    try:
        with open(bugs_cache_path, "r", encoding="utf-8") as f:
            bugs_data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        console.print(f"[red]❌ Erreur lors de la lecture du cache: {e}[/red]")
        console.print(
            "[yellow]Lancez 'aetheris fix --analyze-first' pour régénérer le cache.[/yellow]"
        )
        sys.exit(1)

    # Convertir les données en objets BugIdentifier
    all_bugs: List[BugIdentifier] = []
    fixed_count = 0
    failed_count = 0
    for bug_data in bugs_data:
        bug = BugIdentifier(
            id=bug_data["id"],
            file_path=bug_data["file_path"],
            line_number=bug_data.get("line_number"),
            bug_type=bug_data["bug_type"],
            severity=bug_data["severity"],
            description=bug_data["description"],
            recommendation=bug_data.get("recommendation", ""),
            impacted_files=bug_data.get("impacted_files", []),
            fixed=bug_data.get("fixed", False),
            fixed_at=bug_data.get("fixed_at"),
            fix_summary=bug_data.get("fix_summary"),
            failed=bug_data.get("failed", False),
            failed_at=bug_data.get("failed_at"),
            failure_reason=bug_data.get("failure_reason"),
        )
        all_bugs.append(bug)
        if bug.fixed:
            fixed_count += 1
        elif bug.failed:
            failed_count += 1

    # Filtrer selon le mode
    retry_failed = getattr(args, "retry_failed", False)

    if retry_failed:
        # Mode retry-failed: uniquement les bugs échoués
        bugs = [b for b in all_bugs if b.failed and not b.fixed]
        if fixed_count > 0:
            console.print(f"[dim]ℹ️  {fixed_count} bug(s) déjà corrigé(s) (ignorés)[/dim]")
        if failed_count > 0:
            console.print(f"[cyan]🔄 {failed_count} bug(s) échoué(s) à relancer[/cyan]")
    else:
        # Mode normal: tous les bugs non corrigés
        bugs = [b for b in all_bugs if not b.fixed]
        if fixed_count > 0:
            console.print(f"[dim]ℹ️  {fixed_count} bug(s) déjà corrigé(s) (ignorés)[/dim]")
        if failed_count > 0:
            console.print(
                f"[yellow]⚠️  {failed_count} bug(s) échoué(s) précédemment "
                f"(utilisez --retry-failed pour les relancer uniquement)[/yellow]"
            )

    if not bugs:
        if retry_failed:
            console.print("[green]✅ Aucun bug échoué à relancer![/green]")
        else:
            console.print("[green]✅ Aucun bug à corriger![/green]")
        sys.exit(0)

    # Filtrer par sévérité
    bugs = claude.filter_bugs_by_severity(bugs, args.severity)

    if not bugs:
        console.print(f"[yellow]⚠️  Aucun bug avec sévérité >= {args.severity}[/yellow]")
        sys.exit(0)

    console.print(f"[cyan]🐛 {len(bugs)} bug(s) trouvé(s) avec sévérité >= {args.severity}[/cyan]")
    console.print()

    # Vérifier si Claude Code est disponible pour la correction
    if not claude.is_available:
        console.print("[yellow]⚠️  Mode analyse seule - Affichage des bugs sans correction[/yellow]")
        claude.display_bugs_table(bugs)
        sys.exit(0)

    # Callback pour sauvegarder le cache après chaque correction ou échec
    def save_bug_status(updated_bug: BugIdentifier):
        """Sauvegarde le cache des bugs avec le statut mis à jour (fixé ou échoué)"""
        # Mettre à jour le bug dans all_bugs
        for i, b in enumerate(all_bugs):
            if b.id == updated_bug.id:
                all_bugs[i] = updated_bug
                break

        # Sauvegarder tout le cache
        cache_data = []
        for b in all_bugs:
            bug_dict = {
                "id": b.id,
                "file_path": b.file_path,
                "line_number": b.line_number,
                "bug_type": b.bug_type,
                "severity": b.severity,
                "description": b.description,
                "recommendation": b.recommendation,
                "impacted_files": b.impacted_files,
                "fixed": b.fixed,
                "fixed_at": b.fixed_at,
                "fix_summary": b.fix_summary,
                "failed": getattr(b, "failed", False),
                "failed_at": getattr(b, "failed_at", None),
                "failure_reason": getattr(b, "failure_reason", None),
            }
            cache_data.append(bug_dict)

        with open(bugs_cache_path, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)

    # Lancer la session de correction
    batch_size = getattr(args, "batch_size", 1)
    timeout = getattr(args, "timeout", 300)

    if batch_size > 1:
        # Mode parallèle avec batching
        console.print(
            f"[cyan]⚡ Mode parallèle activé: {batch_size} corrections simultanées[/cyan]"
        )
        console.print()
        stats = await claude.run_fix_session_parallel(
            bugs,
            batch_size=batch_size,
            timeout=timeout,
            on_bug_status=save_bug_status,
        )
    else:
        # Mode séquentiel classique
        # Par défaut mode direct (arrière-plan), --terminal pour ouvrir une fenêtre
        direct_mode = not getattr(args, "terminal", False)
        stats = claude.run_fix_session(
            bugs,
            auto_mode=args.auto,
            direct_mode=direct_mode,
            on_bug_status=save_bug_status,
        )

    console.print()
    console.rule("[bold green]🎉 Session de correction terminée")

    if stats["fixed"] == stats["total"]:
        console.print("[green]✅ Tous les bugs ont été corrigés![/green]")
    elif stats["fixed"] > 0:
        console.print(f"[yellow]⚠️  {stats['fixed']}/{stats['total']} bug(s) corrigé(s)[/yellow]")
    else:
        console.print("[red]❌ Aucun bug n'a été corrigé[/red]")


def setup_user_story_parser(subparsers):
    """Configure le parser pour la sous-commande user-story"""
    us_parser = subparsers.add_parser(
        "user-story",
        help="Analyser les flux de user stories",
        description="Analyse les flux frontend ↔ backend et détecte les incohérences",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  # Analyser depuis une description textuelle
  aetheris user-story --text "Quand l'utilisateur clique sur Login..."

  # Analyser depuis un fichier markdown
  aetheris user-story --file user-stories.md

  # Analyser depuis un point d'entrée code
  aetheris user-story --entry src/components/LoginButton.tsx

  # Auto-détecter tous les flux
  aetheris user-story --auto

  # Options de sortie
  aetheris user-story --auto --output-format json
  aetheris user-story --auto --diagram mermaid
        """,
    )

    # Mode d'entrée (mutuellement exclusif)
    input_group = us_parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--text",
        type=str,
        help="User story en description textuelle",
    )
    input_group.add_argument(
        "--file",
        type=str,
        help="Chemin vers un fichier markdown avec les user stories",
    )
    input_group.add_argument(
        "--entry",
        type=str,
        help="Fichier de code comme point d'entrée (ex: LoginButton.tsx)",
    )
    input_group.add_argument(
        "--auto",
        action="store_true",
        help="Auto-détecter tous les flux utilisateur",
    )

    # Options de sortie
    us_parser.add_argument(
        "--output-format",
        choices=["markdown", "json", "both"],
        default="both",
        help="Format de sortie (défaut: both)",
    )
    us_parser.add_argument(
        "--diagram",
        choices=["mermaid", "plantuml", "both", "none"],
        default="mermaid",
        help="Format de diagramme (défaut: mermaid)",
    )
    us_parser.add_argument(
        "--output-file",
        type=str,
        help="Fichier de sortie (défaut: docs/user-stories/analysis.md)",
    )
    us_parser.add_argument(
        "--severity",
        choices=["critical", "high", "medium", "low", "info"],
        default="low",
        help="Sévérité minimale pour les issues (défaut: low = tout afficher)",
    )

    return us_parser


async def run_user_story(args):
    """Exécute l'analyse de user stories"""
    console = Console()

    console.print()
    console.rule("[bold blue]📖 Aetheris User Story Analysis")
    console.print()

    # Charger le fichier .env
    env_vars = load_env_file(".env")

    # Déterminer le provider AI
    ai_provider = (env_vars.get("AI_PROVIDER") or os.getenv("AI_PROVIDER", "gemini")).lower()

    # Récupérer la clé API
    api_key_env_vars = {
        "gemini": "GEMINI_API_KEY",
        "openai": "OPENAI_API_KEY",
        "claude": "ANTHROPIC_API_KEY",
    }
    api_key_name = api_key_env_vars.get(ai_provider, "GEMINI_API_KEY")
    ai_api_key = env_vars.get(api_key_name) or os.getenv(api_key_name)

    if not ai_api_key:
        console.print(f"[red]❌ Variable d'environnement {api_key_name} non définie[/red]")
        sys.exit(1)

    # Configuration
    from src.core.config import get_default_model

    default_model = get_default_model(ai_provider)
    ai_model = env_vars.get("AI_MODEL") or os.getenv("AI_MODEL", default_model)

    root_dir = env_vars.get("ROOT_DIR") or os.getenv("ROOT_DIR", ".")
    output_dir = env_vars.get("USER_STORY_OUTPUT_DIR") or os.getenv(
        "USER_STORY_OUTPUT_DIR", "docs/user-stories"
    )

    config = AnalysisConfig(
        ai_provider=ai_provider,
        ai_api_key=ai_api_key,
        ai_model=ai_model,
        root_dir=root_dir,
        user_story_output_dir=output_dir,
        user_story_min_severity=args.severity,
        user_story_diagram_format=args.diagram if args.diagram != "none" else "mermaid",
        enable_structured_outputs=True,
    )

    console.print(f"[cyan]🤖 Provider: {ai_provider.upper()} ({ai_model})[/cyan]")
    console.print(f"[cyan]📁 Répertoire: {root_dir}[/cyan]")
    console.print()

    # Déterminer le mode d'entrée
    if args.text:
        input_mode = "text"
        input_value = args.text
        console.print("[cyan]📝 Mode: Description textuelle[/cyan]")
        console.print(
            f"[dim]{args.text[:100]}...[/dim]"
            if len(args.text) > 100
            else f"[dim]{args.text}[/dim]"
        )
    elif args.file:
        input_mode = "file"
        input_value = args.file
        console.print(f"[cyan]📄 Mode: Fichier markdown ({args.file})[/cyan]")
    elif args.entry:
        input_mode = "entry"
        input_value = args.entry
        console.print(f"[cyan]🎯 Mode: Point d'entrée code ({args.entry})[/cyan]")
    else:
        input_mode = "auto"
        input_value = ""
        console.print("[cyan]🔍 Mode: Auto-détection des flux[/cyan]")

    console.print()

    # Lister les fichiers du projet
    from pathspec import PathSpec

    all_files: List[str] = []
    gitignore_path = os.path.join(root_dir, ".gitignore")
    gitignore_spec = None

    if os.path.exists(gitignore_path):
        try:
            with open(gitignore_path, "r", encoding="utf-8") as f:
                gitignore_spec = PathSpec.from_lines("gitwildmatch", f)
        except Exception:
            pass

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Filtrer les dossiers
        dirnames[:] = [
            d
            for d in dirnames
            if not d.startswith(".")
            and d not in ["node_modules", "__pycache__", "dist", "build", ".git"]
        ]

        for filename in filenames:
            filepath = os.path.relpath(os.path.join(dirpath, filename), root_dir)

            # Appliquer gitignore
            if gitignore_spec and gitignore_spec.match_file(filepath):
                continue

            all_files.append(filepath)

    console.print(f"[dim]📊 {len(all_files)} fichiers dans le projet[/dim]")
    console.print()

    # Créer le ProgressManager
    progress_manager = ProgressManager(enabled=True)

    # Importer et créer l'agent
    from src.agents.user_story_analysis_agent import UserStoryAnalysisAgent
    from src.services.diagram_generator import DiagramGenerator

    agent = UserStoryAnalysisAgent(
        config=config,
        root_dir=root_dir,
        all_files=all_files,
        progress_manager=progress_manager,
    )

    # Lancer l'analyse
    console.print("[cyan]🔄 Analyse en cours...[/cyan]")
    console.print()

    result = await agent.analyze_all_flows(input_mode, input_value)

    # Afficher les résultats
    console.print()
    console.rule("[bold green]📊 Résultats de l'analyse")
    console.print()

    console.print("[bold]📈 Statistiques:[/bold]")
    console.print(f"  • Flux analysés: {result.total_flows}")
    console.print(f"  • Étapes totales: {result.total_steps}")
    console.print(f"  • Appels API: {result.total_api_calls}")
    console.print(f"  • Endpoints: {result.total_endpoints}")
    console.print()

    console.print("[bold]🐛 Issues par sévérité:[/bold]")
    if result.critical_count > 0:
        console.print(f"  • [red]Critical: {result.critical_count}[/red]")
    if result.high_count > 0:
        console.print(f"  • [yellow]High: {result.high_count}[/yellow]")
    if result.medium_count > 0:
        console.print(f"  • [blue]Medium: {result.medium_count}[/blue]")
    if result.low_count > 0:
        console.print(f"  • [dim]Low: {result.low_count}[/dim]")

    if result.orphan_endpoints:
        console.print()
        console.print(
            f"[yellow]⚠️  {len(result.orphan_endpoints)} endpoint(s) orphelin(s) détecté(s)[/yellow]"
        )
        for ep in result.orphan_endpoints[:5]:
            console.print(f"  • {ep.method} {ep.path} ({ep.file_path})")
        if len(result.orphan_endpoints) > 5:
            console.print(f"  ... et {len(result.orphan_endpoints) - 5} autres")

    if result.missing_handlers:
        console.print()
        console.print(f"[red]❌ {len(result.missing_handlers)} appel(s) API sans handler[/red]")
        for call in result.missing_handlers[:5]:
            console.print(f"  • {call.method} {call.url_pattern} ({call.file_path})")

    # Générer les diagrammes
    if args.diagram != "none":
        console.print()
        console.print("[cyan]📊 Génération des diagrammes...[/cyan]")

        diagram_gen = DiagramGenerator(output_dir)
        files_created = diagram_gen.save_diagrams(result, args.diagram)

        console.print(f"[green]✅ {len(files_created)} fichier(s) créé(s):[/green]")
        for f in files_created[:5]:
            console.print(f"  • {f}")

    # Sauvegarder le rapport JSON si demandé
    if args.output_format in ["json", "both"]:
        os.makedirs(output_dir, exist_ok=True)
        json_path = os.path.join(output_dir, "analysis-result.json")

        report = {
            "analysis_id": result.analysis_id,
            "timestamp": result.timestamp,
            "summary": {
                "total_flows": result.total_flows,
                "total_steps": result.total_steps,
                "total_api_calls": result.total_api_calls,
                "total_endpoints": result.total_endpoints,
                "issues": {
                    "critical": result.critical_count,
                    "high": result.high_count,
                    "medium": result.medium_count,
                    "low": result.low_count,
                },
            },
            "flows": [
                {
                    "id": flow.id,
                    "title": flow.title,
                    "entry_point": flow.entry_point,
                    "steps_count": len(flow.steps),
                    "issues_count": len(flow.issues),
                }
                for flow in result.flows
            ],
            "orphan_endpoints": [
                {"method": ep.method, "path": ep.path, "file": ep.file_path}
                for ep in result.orphan_endpoints
            ],
            "issues": [
                {
                    "id": issue.id,
                    "severity": issue.severity,
                    "type": issue.issue_type,
                    "title": issue.title,
                    "description": issue.description,
                }
                for issue in result.all_issues
            ],
        }

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        console.print(f"[green]📄 Rapport JSON: {json_path}[/green]")

    console.print()
    console.rule("[bold green]✅ Analyse terminée")


def setup_pr_generator_parser(subparsers):
    """Configure le parser pour la sous-commande pr-gen (generate PRs from bugs)"""
    pr_gen_parser = subparsers.add_parser(
        "pr-gen",
        aliases=["generate-prs"],
        help="Generate PRs with AI-fixed code from analysis reports",
        description="Generate GitHub Pull Requests with AI-generated fixes for bugs found in analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview PRs without creating them
  aetheris pr-gen --dry-run

  # Generate all PRs from analysis reports
  aetheris pr-gen

  # Generate PRs with issue linking
  aetheris pr-gen --link-issues

  # Target specific base branch
  aetheris pr-gen --base-branch develop

  # Process only a specific report
  aetheris pr-gen --from-report docs/analyses/analyzer.md

  # Process a single bug by index
  aetheris pr-gen --bug-index 0

  # Link to a specific issue
  aetheris pr-gen --issue-number 42
        """,
    )

    pr_gen_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview PRs and fixes without creating them",
    )

    pr_gen_parser.add_argument(
        "--base-branch",
        type=str,
        default=None,
        help="Target base branch for PRs (defaults to repo default branch)",
    )

    pr_gen_parser.add_argument(
        "--from-report",
        type=str,
        default=None,
        help="Process only this specific analysis report file",
    )

    pr_gen_parser.add_argument(
        "--bug-index",
        type=int,
        default=None,
        help="Process only the bug at this index (0-based)",
    )

    pr_gen_parser.add_argument(
        "--link-issues",
        action="store_true",
        help="Automatically link PRs to matching GitHub issues",
    )

    pr_gen_parser.add_argument(
        "--issue-number",
        type=int,
        default=None,
        help="Explicitly link all PRs to this issue number",
    )

    return pr_gen_parser


async def run_pr_generator(args):
    """Generate PRs with AI-fixed code from analysis reports."""
    from src.services.pr_generator import PRGenerator, PROptions

    console = Console()
    console.print()
    console.rule("[bold blue]🚀 Aetheris PR Generator - Create PRs with AI Fixes")
    console.print()

    # Create options
    options = PROptions(
        dry_run=args.dry_run,
        base_branch=args.base_branch,
        from_report=args.from_report,
        bug_index=args.bug_index,
        link_issues=args.link_issues,
        issue_number=args.issue_number,
    )

    # Run PR generator
    generator = PRGenerator()
    await generator.run(options)


def setup_pr_parser(subparsers):
    """Configure le parser pour la sous-commande pr (review-pr)"""
    pr_parser = subparsers.add_parser(
        "pr",
        aliases=["review-pr"],
        help="Analyser une Pull Request GitHub",
        description="Analyse une PR avec plusieurs providers AI et poste des commentaires",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  # Analyser une PR par URL
  aetheris pr --url https://github.com/owner/repo/pull/123

  # Analyser une PR par repo et numéro
  aetheris pr --repo owner/repo --pr 123

  # Multi-provider avec consensus
  aetheris pr --url https://... --providers gemini,claude

  # Désactiver le mode consensus (voir tous les issues)
  aetheris pr --url https://... --providers gemini,claude --no-consensus

  # Mode dry-run (analyse sans poster de commentaires)
  aetheris pr --url https://... --dry-run

  # Sauvegarder le rapport dans un fichier
  aetheris pr --url https://... --output review.md
        """,
    )

    # Source de la PR (mutuellement exclusif)
    source_group = pr_parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--url",
        type=str,
        help="URL complète de la PR (ex: https://github.com/owner/repo/pull/123)",
    )
    source_group.add_argument(
        "--repo",
        type=str,
        help="Repository au format owner/repo (requiert --pr)",
    )

    pr_parser.add_argument(
        "--pr",
        type=int,
        help="Numéro de PR (requis avec --repo)",
    )

    # AI providers
    pr_parser.add_argument(
        "--providers",
        type=str,
        default="gemini",
        help="Providers AI séparés par virgules (ex: gemini,claude,openai). Défaut: gemini",
    )

    # Consensus mode
    pr_parser.add_argument(
        "--consensus",
        action="store_true",
        default=True,
        help="Mode consensus: reporter uniquement les issues trouvés par TOUS les providers (défaut)",
    )
    pr_parser.add_argument(
        "--no-consensus",
        action="store_true",
        help="Désactiver le mode consensus (reporter tous les issues)",
    )

    # Output options
    pr_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Analyser sans poster de commentaires sur la PR",
    )
    pr_parser.add_argument(
        "--severity",
        choices=["critical", "high", "medium", "low", "info"],
        default="low",
        help="Sévérité minimale des issues à reporter (défaut: low = tout)",
    )
    pr_parser.add_argument(
        "--no-inline",
        action="store_true",
        help="Ne pas poster de commentaires inline, seulement le résumé",
    )
    pr_parser.add_argument(
        "--output",
        type=str,
        help="Sauvegarder le rapport dans un fichier (markdown)",
    )
    pr_parser.add_argument(
        "--auto-fix",
        action="store_true",
        help="Si c'est votre PR, proposer de corriger les issues avec Claude Code",
    )

    return pr_parser


async def run_pr(args):
    """Exécute l'analyse de Pull Request"""
    console = Console()

    console.print()
    console.rule("[bold blue]Aetheris PR Review")
    console.print()

    # Valider les arguments
    if args.repo and not args.pr:
        console.print("[red]Erreur: --pr est requis avec --repo[/red]")
        sys.exit(1)

    # Charger l'environnement
    env_vars = load_env_file(".env")

    # Parser les providers
    providers = [p.strip().lower() for p in args.providers.split(",")]

    # Mapping des clés API
    api_key_env_vars = {
        "gemini": "GEMINI_API_KEY",
        "openai": "OPENAI_API_KEY",
        "claude": "ANTHROPIC_API_KEY",
    }

    # Valider les clés API pour chaque provider
    api_keys = {}
    for provider in providers:
        key_name = api_key_env_vars.get(provider)
        if key_name:
            key = env_vars.get(key_name) or os.getenv(key_name)
            if not key:
                console.print(
                    f"[red]Erreur: {key_name} non trouvée pour le provider {provider}[/red]"
                )
                console.print("[dim]Définissez la variable dans .env ou l'environnement[/dim]")
                sys.exit(1)
            api_keys[provider] = key

    if not api_keys:
        console.print("[red]Erreur: Aucun provider valide configuré[/red]")
        sys.exit(1)

    # Initialiser le service GitHub
    from src.services.github_service import GitHubService
    from src.services.github_service import GitHubServiceError

    gh_service = GitHubService()

    if not gh_service.is_available:
        console.print("[red]Erreur: gh CLI n'est pas disponible ou non authentifié[/red]")
        console.print("[dim]Installez gh: https://cli.github.com/[/dim]")
        console.print("[dim]Authentifiez-vous: gh auth login[/dim]")
        sys.exit(1)

    # Parser l'URL ou utiliser repo/pr
    try:
        if args.url:
            repo, pr_number = gh_service.parse_pr_url(args.url)
        else:
            repo = args.repo
            pr_number = args.pr
    except GitHubServiceError as e:
        console.print(f"[red]Erreur: {e}[/red]")
        sys.exit(1)

    console.print(f"[cyan]Repository:[/cyan] {repo}")
    console.print(f"[cyan]PR #:[/cyan] {pr_number}")
    console.print(f"[cyan]Providers:[/cyan] {', '.join(providers)}")
    consensus_mode = not args.no_consensus
    console.print(f"[cyan]Mode consensus:[/cyan] {'Oui' if consensus_mode else 'Non'}")
    console.print()

    # Récupérer les infos de la PR
    console.print("[cyan]Récupération des informations de la PR...[/cyan]")
    try:
        pr_info = await gh_service.fetch_pr_info(repo, pr_number)
    except GitHubServiceError as e:
        console.print(f"[red]Erreur lors de la récupération de la PR: {e}[/red]")
        sys.exit(1)

    # Vérifier la propriété
    is_own_pr = gh_service.is_own_pr(pr_info)
    if is_own_pr:
        console.print("[green]C'est VOTRE PR[/green]")
    else:
        console.print(f"[yellow]PR par:[/yellow] {pr_info.author_login}")

    console.print(f"[dim]Titre: {pr_info.title}[/dim]")
    console.print(f"[dim]Branche: {pr_info.head_branch} -> {pr_info.base_branch}[/dim]")
    console.print()

    # Récupérer le diff et les fichiers
    console.print("[cyan]Récupération du diff...[/cyan]")
    try:
        diff_content = await gh_service.fetch_pr_diff(repo, pr_number)
        files_changed = await gh_service.fetch_pr_files(repo, pr_number)
    except GitHubServiceError as e:
        console.print(f"[red]Erreur lors de la récupération du diff: {e}[/red]")
        sys.exit(1)

    console.print(
        f"[dim]{len(files_changed)} fichiers modifiés, +{pr_info.additions}/-{pr_info.deletions}[/dim]"
    )
    console.print()

    # Créer la config et lancer l'analyse
    config = AnalysisConfig(
        ai_api_key=list(api_keys.values())[0],
        ai_provider=providers[0],
        root_dir=os.getcwd(),
        timeout_seconds=120,
        max_retries=3,
    )

    progress_manager = ProgressManager(enabled=True)

    from src.agents.pr_review_agent import PRReviewAgent

    agent = PRReviewAgent(
        config=config,
        providers=providers,
        api_keys=api_keys,
        consensus_mode=consensus_mode,
        progress_manager=progress_manager,
    )

    # Lancer l'analyse
    console.print("[cyan]Analyse en cours...[/cyan]")
    console.print()

    result = await agent.analyze_pr_diff(pr_info, diff_content, files_changed)
    result.is_own_pr = is_own_pr

    # Afficher les résultats
    console.print()
    console.rule("[bold]Résultats de l'analyse")
    console.print()

    # Filtrer par sévérité
    severity_order = ["critical", "high", "medium", "low", "info"]
    min_severity_idx = severity_order.index(args.severity)
    filtered_issues = [
        issue
        for issue in result.issues
        if severity_order.index(issue.severity.value) <= min_severity_idx
    ]

    console.print(f"[bold]Score de risque:[/bold] {result.risk_score}/10")
    console.print(f"[bold]Recommandation:[/bold] {result.approval_recommendation}")
    console.print(
        f"[bold]Issues trouvées:[/bold] {len(result.issues)} ({len(filtered_issues)} après filtre)"
    )

    if result.consensus_mode and len(providers) > 1:
        console.print(
            f"[dim]Mode consensus: {result.total_issues_before_consensus} issues détectées, {len(result.issues)} en consensus[/dim]"
        )

    console.print()

    # Afficher les issues
    if filtered_issues:
        from rich.table import Table

        table = Table(title="Issues détectées")
        table.add_column("Sév.", style="bold")
        table.add_column("Type")
        table.add_column("Fichier")
        table.add_column("Ligne")
        table.add_column("Titre")

        emoji_map = {
            "critical": "[red]CRIT[/red]",
            "high": "[orange1]HIGH[/orange1]",
            "medium": "[yellow]MED[/yellow]",
            "low": "[blue]LOW[/blue]",
            "info": "[dim]INFO[/dim]",
        }

        for issue in filtered_issues:
            table.add_row(
                emoji_map.get(issue.severity.value, issue.severity.value),
                issue.issue_type.value,
                issue.file_path[:30] + "..." if len(issue.file_path) > 30 else issue.file_path,
                str(issue.line_number) if issue.line_number else "-",
                issue.title[:40] + "..." if len(issue.title) > 40 else issue.title,
            )

        console.print(table)
        console.print()

    # Sauvegarder le rapport si demandé
    if args.output:
        summary_comment = agent.generate_summary_comment(result)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(summary_comment)
        console.print(f"[green]Rapport sauvegardé: {args.output}[/green]")
        console.print()

    # Gérer le posting des commentaires ou la correction
    if not args.dry_run and filtered_issues:
        if is_own_pr and args.auto_fix:
            # Proposer de corriger
            if Confirm.ask("Voulez-vous corriger ces issues avec Claude Code ?"):
                console.print("[yellow]Fonctionnalité de correction à implémenter...[/yellow]")
                # TODO: Intégration avec ClaudeCodeIntegration
        else:
            # Proposer de poster les commentaires
            if Confirm.ask(f"Poster {len(filtered_issues)} commentaires sur la PR ?"):
                console.print("[cyan]Publication des commentaires...[/cyan]")

                # Poster le résumé
                summary_comment = agent.generate_summary_comment(result)
                success = await gh_service.post_review_comment(
                    repo=repo,
                    pr_number=pr_number,
                    body=summary_comment,
                    event="COMMENT",
                )

                if success:
                    console.print("[green]Commentaire de résumé posté avec succès[/green]")
                else:
                    console.print("[red]Erreur lors de la publication du résumé[/red]")

                # Poster les commentaires inline si activé
                if not args.no_inline and pr_info.head_sha:
                    inline_count = 0
                    for comment in result.inline_comments:
                        # Filtrer par sévérité aussi
                        issue = next(
                            (
                                i
                                for i in filtered_issues
                                if i.file_path == comment.file_path
                                and i.line_number == comment.line_number
                            ),
                            None,
                        )
                        if issue:
                            success = await gh_service.post_inline_comment(
                                repo=repo,
                                pr_number=pr_number,
                                commit_id=pr_info.head_sha,
                                file_path=comment.file_path,
                                line_number=comment.line_number,
                                body=comment.body,
                            )
                            if success:
                                inline_count += 1

                    console.print(f"[green]{inline_count} commentaires inline postés[/green]")

    elif args.dry_run:
        console.print("[dim]Mode dry-run: aucun commentaire posté[/dim]")

    console.print()
    console.rule("[bold green]Analyse terminée")


def get_version():
    """Retourne la version depuis pyproject.toml"""
    try:
        import importlib.metadata

        return importlib.metadata.version("adryserage-aetheris")
    except Exception:
        return "2.3.4"  # Fallback


def create_parser():
    """Crée le parser principal avec sous-commandes"""
    parser = argparse.ArgumentParser(
        prog="aetheris",
        description="Aetheris by Adryan - Système d'analyse de code multi-agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Pour plus d'informations sur une commande spécifique:
  aetheris <commande> --help

Exemples:
  aetheris analysis                    # Analyse complète
  aetheris fix                         # Corriger les bugs avec Claude Code
  aetheris fix --test                  # Tester la connexion à Claude Code
  aetheris fix --analyze-first         # Analyser puis corriger
  aetheris fix --severity high         # Corriger uniquement bugs critiques/high
  aetheris pr --url https://...        # Analyser une PR GitHub
  aetheris pr --repo owner/repo --pr 1 # Analyser par repo et numéro
  aetheris pr --providers gemini,claude # Multi-provider avec consensus
        """,
    )

    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {get_version()}")

    subparsers = parser.add_subparsers(
        dest="command", help="Commandes disponibles", metavar="COMMANDE"
    )

    # Ajouter la sous-commande analysis
    setup_analysis_parser(subparsers)

    # Ajouter la sous-commande fix
    setup_fix_parser(subparsers)

    # Ajouter la sous-commande user-story
    setup_user_story_parser(subparsers)

    # Ajouter la sous-commande pr (review-pr)
    setup_pr_parser(subparsers)

    # Ajouter la sous-commande pr-gen (generate PRs from bugs)
    setup_pr_generator_parser(subparsers)

    # Ajouter la sous-commande issues
    setup_issues_parser(subparsers)

    return parser


def main():
    """Point d'entrée principal de la CLI"""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "analysis":
        asyncio.run(run_analysis(args))
    elif args.command == "fix":
        asyncio.run(run_fix(args))
    elif args.command == "user-story":
        asyncio.run(run_user_story(args))
    elif args.command in ["pr", "review-pr"]:
        asyncio.run(run_pr(args))
    elif args.command in ["pr-gen", "generate-prs"]:
        asyncio.run(run_pr_generator(args))
    elif args.command == "issues":
        asyncio.run(run_issues(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
