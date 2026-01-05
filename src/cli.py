#!/usr/bin/env python3
"""
Aetheris by Adryan - Interface en ligne de commande
"""

import os
import sys
import asyncio
import argparse
import json
from typing import List, Optional

from rich.console import Console
from rich.prompt import Confirm

# Configuration du logging et encodage UTF-8
from src.core.logger import setup_utf8_encoding, log_print

setup_utf8_encoding()

try:
    from google import genai  # Nouveau SDK google-genai
    from pathspec import PathSpec
    from ddgs import DDGS
    import requests
    import yaml
except ImportError as e:
    print(f"❌ Dépendances manquantes: {e}")
    print("   Installez avec: pip install -r requirements.txt")
    sys.exit(1)

# Import de la configuration depuis le module dédié
from src.core.config import AnalysisConfig, load_env_file

# Import de CodeAnalyzer depuis le module dédié
from src.core.analyzer import CodeAnalyzer
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

    return analysis_parser


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

    if analyze_changed_only:
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
    )

    log_print(f"📁 Répertoire racine: {config.root_dir}")
    log_print(f"📂 Répertoire de sortie: {config.output_dir}")
    log_print(f"🤖 Provider AI: {config.ai_provider.upper()}")
    log_print(f"🤖 Modèle: {config.ai_model}")

    if analyze_changed_only:
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
        description="Lance Claude Code pour corriger les bugs un par un",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  # Corriger les bugs depuis le cache existant
  aetheris fix

  # Lancer une analyse puis corriger
  aetheris fix --analyze-first

  # Corriger uniquement les bugs critiques et high
  aetheris fix --severity high

  # Mode automatique (sans confirmations)
  aetheris fix --auto
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

    return fix_parser


async def run_fix(args):
    """Exécute la correction de bugs avec Claude Code"""
    console = Console()

    console.print()
    console.rule("[bold blue]🔧 Aetheris Fix - Correction de bugs avec Claude Code")
    console.print()

    # Import des modules nécessaires
    from src.services.claude_code_integration import ClaudeCodeIntegration
    from src.models.data_models import BugIdentifier

    # Charger le fichier .env s'il existe
    env_vars = load_env_file(".env")
    root_dir = env_vars.get("ROOT_DIR") or os.getenv("ROOT_DIR", ".")
    output_dir = env_vars.get("OUTPUT_DIR") or os.getenv("OUTPUT_DIR", "docs/analyses")

    # Initialiser l'intégration Claude Code
    claude = ClaudeCodeIntegration(root_dir)

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
        console.print("[yellow]Lancez 'aetheris fix --analyze-first' pour régénérer le cache.[/yellow]")
        sys.exit(1)

    # Convertir les données en objets BugIdentifier
    bugs: List[BugIdentifier] = []
    for bug_data in bugs_data:
        bugs.append(
            BugIdentifier(
                id=bug_data["id"],
                file_path=bug_data["file_path"],
                line_number=bug_data.get("line_number"),
                bug_type=bug_data["bug_type"],
                severity=bug_data["severity"],
                description=bug_data["description"],
                recommendation=bug_data.get("recommendation", ""),
                impacted_files=bug_data.get("impacted_files", []),
            )
        )

    if not bugs:
        console.print("[green]✅ Aucun bug à corriger![/green]")
        sys.exit(0)

    # Filtrer par sévérité
    bugs = claude.filter_bugs_by_severity(bugs, args.severity)

    if not bugs:
        console.print(
            f"[yellow]⚠️  Aucun bug avec sévérité >= {args.severity}[/yellow]"
        )
        sys.exit(0)

    console.print(
        f"[cyan]🐛 {len(bugs)} bug(s) trouvé(s) avec sévérité >= {args.severity}[/cyan]"
    )
    console.print()

    # Vérifier si Claude Code est disponible pour la correction
    if not claude.is_available:
        console.print("[yellow]⚠️  Mode analyse seule - Affichage des bugs sans correction[/yellow]")
        claude.display_bugs_table(bugs)
        sys.exit(0)

    # Lancer la session de correction
    stats = claude.run_fix_session(bugs, auto_mode=args.auto)

    console.print()
    console.rule("[bold green]🎉 Session de correction terminée")

    if stats["fixed"] == stats["total"]:
        console.print("[green]✅ Tous les bugs ont été corrigés![/green]")
    elif stats["fixed"] > 0:
        console.print(
            f"[yellow]⚠️  {stats['fixed']}/{stats['total']} bug(s) corrigé(s)[/yellow]"
        )
    else:
        console.print("[red]❌ Aucun bug n'a été corrigé[/red]")


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
  aetheris fix --analyze-first         # Analyser puis corriger
  aetheris fix --severity high         # Corriger uniquement bugs critiques/high
        """,
    )

    subparsers = parser.add_subparsers(
        dest="command", help="Commandes disponibles", metavar="COMMANDE"
    )

    # Ajouter la sous-commande analysis
    setup_analysis_parser(subparsers)

    # Ajouter la sous-commande fix
    setup_fix_parser(subparsers)

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
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
