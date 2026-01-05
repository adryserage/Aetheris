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
                model="gemini-2.0-flash",
                contents="Say 'OK' if you can hear me."
            )
            log_print(f"✅ Clé API validée: {test_response.text[:50]}...")
        except Exception as e:
            log_print(f"❌ Erreur de validation de la clé API: {e}")
            log_print("   Vérifiez que votre clé API est valide sur: https://aistudio.google.com/apikey")
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
  # Tester la connexion à Claude Code
  aetheris fix --test

  # Corriger les bugs depuis le cache existant (mode arrière-plan)
  aetheris fix

  # Mode automatique (sans confirmations)
  aetheris fix --auto

  # Ouvrir Claude Code dans une fenêtre terminal
  aetheris fix --terminal

  # Corriger uniquement les bugs critiques et high
  aetheris fix --severity high

  # Lancer une analyse puis corriger
  aetheris fix --analyze-first
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
    # Par défaut mode direct (arrière-plan), --terminal pour ouvrir une fenêtre
    direct_mode = not getattr(args, "terminal", False)
    stats = claude.run_fix_session(bugs, auto_mode=args.auto, direct_mode=direct_mode)

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
        console.print(f"[cyan]📝 Mode: Description textuelle[/cyan]")
        console.print(f"[dim]{args.text[:100]}...[/dim]" if len(args.text) > 100 else f"[dim]{args.text}[/dim]")
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
            d for d in dirnames
            if not d.startswith(".") and d not in ["node_modules", "__pycache__", "dist", "build", ".git"]
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

    console.print(f"[bold]📈 Statistiques:[/bold]")
    console.print(f"  • Flux analysés: {result.total_flows}")
    console.print(f"  • Étapes totales: {result.total_steps}")
    console.print(f"  • Appels API: {result.total_api_calls}")
    console.print(f"  • Endpoints: {result.total_endpoints}")
    console.print()

    console.print(f"[bold]🐛 Issues par sévérité:[/bold]")
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
        console.print(f"[yellow]⚠️  {len(result.orphan_endpoints)} endpoint(s) orphelin(s) détecté(s)[/yellow]")
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


def get_version():
    """Retourne la version depuis pyproject.toml"""
    try:
        import importlib.metadata
        return importlib.metadata.version("adryserage-aetheris")
    except Exception:
        return "2.3.0"  # Fallback


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
        """,
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {get_version()}"
    )

    subparsers = parser.add_subparsers(
        dest="command", help="Commandes disponibles", metavar="COMMANDE"
    )

    # Ajouter la sous-commande analysis
    setup_analysis_parser(subparsers)

    # Ajouter la sous-commande fix
    setup_fix_parser(subparsers)

    # Ajouter la sous-commande user-story
    setup_user_story_parser(subparsers)

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
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
