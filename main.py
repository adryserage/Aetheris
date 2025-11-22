#!/usr/bin/env python3
"""
Aetheris by Adryan - Système d'analyse de code avec plusieurs agents coopérants :
- Code Analysis Expert (CAE) : analyse chaque fichier individuellement
- Architect Analysis Agent (AAA) : produit une vue d'ensemble de l'architecture
- Security Analysis Agent (SSA) : détecte les vulnérabilités de sécurité
- Code Metrics Agent (CMA) : calcule les métriques de code (complexité, duplication, etc.)
- Dependency Vulnerability Agent (DVA) : analyse les vulnérabilités des dépendances via OSV API
- Quality Assurance Agent (QAA) : synthétise toutes les analyses en un rapport d'assurance qualité

Le système détecte automatiquement tous les langages présents dans le repository.
"""

import os
import sys
import asyncio
import argparse
import json
from typing import List, Optional

# Configuration du logging et encodage UTF-8
from src.core.logger import setup_utf8_encoding, log_print

setup_utf8_encoding()

try:
    import google.generativeai as genai
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


def parse_args():
    """Parse les arguments de ligne de commande"""
    parser = argparse.ArgumentParser(
        description="Aetheris by Adryan - Système d'analyse de code multi-agents",
        prog="python main.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  # Analyse complète de la codebase
  python main.py
  
  # Analyser uniquement les fichiers modifiés (depuis GitHub Actions)
  python main.py --changed-files-only --files '["src/file1.py", "src/file2.py"]'
  
  # Analyser une liste de fichiers spécifiques
  python main.py --files src/file1.py,src/file2.py
  
  # Analyser les fichiers d'une PR
  python main.py --changed-files-only --pr-number 123
        """,
    )

    parser.add_argument(
        "--changed-files-only",
        action="store_true",
        help="Analyser uniquement les fichiers modifiés (pour PR/commits)",
    )

    parser.add_argument(
        "--files",
        type=str,
        default=None,
        help="Liste de fichiers à analyser (JSON array ou séparés par virgules). Utilisé avec --changed-files-only",
    )

    parser.add_argument(
        "--pr-number", type=int, default=None, help="Numéro de PR (optionnel, pour information)"
    )

    return parser.parse_args()


async def main():
    """Point d'entrée principal"""
    args = parse_args()

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


if __name__ == "__main__":
    asyncio.run(main())
