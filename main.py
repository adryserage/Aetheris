#!/usr/bin/env python3
"""
Système d'analyse de code avec plusieurs agents coopérants :
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
    try:
        from duckduckgo_search import DDGS
        WEB_SEARCH_AVAILABLE = True
    except ImportError:
        WEB_SEARCH_AVAILABLE = False
        print("⚠️  Recherche web désactivée. Installez 'duckduckgo-search' pour l'activer: pip install duckduckgo-search")
    try:
        import requests
        REQUESTS_AVAILABLE = True
    except ImportError:
        REQUESTS_AVAILABLE = False
        print("⚠️  'requests' non installé. L'analyse des vulnérabilités sera désactivée: pip install requests")
    try:
        import yaml
        YAML_AVAILABLE = True
    except ImportError:
        YAML_AVAILABLE = False
        print("⚠️  'pyyaml' non installé. L'analyse des dépendances Dart sera limitée: pip install pyyaml")
except ImportError:
    print("❌ Dépendances manquantes. Installez avec: pip install -r requirements.txt")
    sys.exit(1)


# Import de la configuration depuis le module dédié
from src.core.config import AnalysisConfig, load_env_file

# Import de CodeAnalyzer depuis le module dédié
from src.core.analyzer import CodeAnalyzer


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
    files = [f.strip() for f in files_input.split(',') if f.strip()]
    return files


def parse_args():
    """Parse les arguments de ligne de commande"""
    parser = argparse.ArgumentParser(
        description='Système d\'analyse de code multi-agents',
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
        """
    )
    
    parser.add_argument(
        '--changed-files-only',
        action='store_true',
        help='Analyser uniquement les fichiers modifiés (pour PR/commits)'
    )
    
    parser.add_argument(
        '--files',
        type=str,
        default=None,
        help='Liste de fichiers à analyser (JSON array ou séparés par virgules). Utilisé avec --changed-files-only'
    )
    
    parser.add_argument(
        '--pr-number',
        type=int,
        default=None,
        help='Numéro de PR (optionnel, pour information)'
    )
    
    return parser.parse_args()


async def main():
    """Point d'entrée principal"""
    args = parse_args()
    
    log_print("=" * 60)
    log_print("🚀 Démarrage de l'analyse de code")
    log_print("=" * 60)
    log_print()
    
    # Charger le fichier .env s'il existe
    env_vars = load_env_file('.env')
    
    # Charger les variables d'environnement (fichier .env en priorité, puis système)
    gemini_api_key = env_vars.get('GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY')
    
    if not gemini_api_key:
        log_print("❌ Variable d'environnement GEMINI_API_KEY non définie")
        log_print("   Options:")
        log_print("   1. Créez un fichier .env avec: GEMINI_API_KEY=votre_cle")
        log_print("   2. Ou définissez-la avec: export GEMINI_API_KEY=votre_cle (Linux/Mac)")
        log_print("   3. Ou définissez-la avec: $env:GEMINI_API_KEY='votre_cle' (PowerShell)")
        log_print("   4. Ou configurez-la dans GitHub Secrets (pour GitHub Actions)")
        sys.exit(1)
    
    # Appliquer les variables du .env à l'environnement pour les autres configs
    for key, value in env_vars.items():
        if key not in os.environ:
            os.environ[key] = value
    
    # Parser les fichiers modifiés depuis les arguments ou l'environnement GitHub Actions
    changed_files: List[str] = []
    analyze_changed_only = args.changed_files_only
    
    if analyze_changed_only:
        # Priorité: argument --files, puis variable d'environnement CHANGED_FILES
        files_input = args.files or os.getenv('CHANGED_FILES')
        changed_files = parse_changed_files(files_input)
        
        if not changed_files:
            log_print("⚠️  Mode --changed-files-only activé mais aucun fichier spécifié")
            log_print("   Utilisez --files ou définissez CHANGED_FILES dans l'environnement")
            sys.exit(1)
    
    # Obtenir le numéro de PR depuis les arguments ou l'environnement GitHub
    pr_number = args.pr_number
    if not pr_number:
        pr_number_str = os.getenv('PR_NUMBER')
        if pr_number_str:
            try:
                pr_number = int(pr_number_str)
            except ValueError:
                pass
    
    config = AnalysisConfig(
        gemini_api_key=gemini_api_key,
        gemini_model=os.getenv('GEMINI_MODEL', 'gemini-3-pro-preview'),
        batch_size=int(os.getenv('BATCH_SIZE', '10')),
        max_retries=int(os.getenv('MAX_RETRIES', '3')),
        timeout_seconds=int(os.getenv('TIMEOUT_SECONDS', '60')),
        output_dir=os.getenv('OUTPUT_DIR', 'docs/analyses'),
        architecture_report_path=os.getenv('ARCHITECTURE_REPORT', 'docs/architecture_overview.md'),
        root_dir=os.getenv('ROOT_DIR', '.'),
        enable_web_search=os.getenv('ENABLE_WEB_SEARCH', 'true').lower() == 'true',
        max_web_results=int(os.getenv('MAX_WEB_RESULTS', '3')),
        enable_security_analysis=os.getenv('ENABLE_SECURITY_ANALYSIS', 'true').lower() == 'true',
        enable_metrics_analysis=os.getenv('ENABLE_METRICS_ANALYSIS', 'true').lower() == 'true',
        enable_dependency_vulnerability=os.getenv('ENABLE_DEPENDENCY_VULNERABILITY', 'true').lower() == 'true',
        enable_code_generation=os.getenv('ENABLE_CODE_GENERATION', 'true').lower() == 'true',
        analyze_changed_files_only=analyze_changed_only,
        changed_files=changed_files,
        pr_number=pr_number
    )
    
    log_print(f"📁 Répertoire racine: {config.root_dir}")
    log_print(f"📂 Répertoire de sortie: {config.output_dir}")
    log_print(f"🤖 Modèle Gemini: {config.gemini_model}")
    
    if analyze_changed_only:
        log_print(f"🔍 Mode: Analyse des fichiers modifiés uniquement ({len(changed_files)} fichier(s))")
        if pr_number:
            log_print(f"📋 PR #{pr_number}")
    else:
        log_print("🔍 Mode: Analyse complète de la codebase")
    
    log_print()
    
    analyzer = CodeAnalyzer(config)
    await analyzer.run()
    
    log_print()
    log_print("=" * 60)
    log_print("✅ Analyse terminée avec succès!")
    log_print("=" * 60)


if __name__ == '__main__':
    asyncio.run(main())
