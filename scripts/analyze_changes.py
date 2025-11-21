#!/usr/bin/env python3
"""
Script pour analyser les fichiers modifiés dans un commit ou une PR.
Utilisé par le workflow GitHub Actions en mode diff.
"""

import os
import sys
import subprocess
from typing import List, Optional


def get_changed_files(base_ref: Optional[str] = None, head_ref: Optional[str] = None) -> List[str]:
    """
    Récupère la liste des fichiers modifiés entre deux références Git.

    Args:
        base_ref: Référence de base (ex: 'origin/main', 'HEAD~1')
        head_ref: Référence de tête (ex: 'HEAD', 'origin/feature')

    Returns:
        Liste des chemins de fichiers modifiés
    """
    try:
        if base_ref and head_ref:
            # Comparer deux références spécifiques
            result = subprocess.run(
                ["git", "diff", "--name-only", "--diff-filter=ACMR", base_ref, head_ref],
                capture_output=True,
                text=True,
                check=True,
            )
        elif base_ref:
            # Comparer avec une référence de base
            result = subprocess.run(
                ["git", "diff", "--name-only", "--diff-filter=ACMR", base_ref, "HEAD"],
                capture_output=True,
                text=True,
                check=True,
            )
        else:
            # Comparer avec le commit précédent
            result = subprocess.run(
                ["git", "diff", "--name-only", "--diff-filter=ACMR", "HEAD~1", "HEAD"],
                capture_output=True,
                text=True,
                check=False,  # Peut échouer si pas d'historique
            )

        if result.returncode != 0:
            # Si la commande échoue, essayer de récupérer les fichiers du dernier commit
            result = subprocess.run(
                ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"],
                capture_output=True,
                text=True,
                check=False,
            )

        files = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
        return files

    except subprocess.CalledProcessError as e:
        print(f"⚠️  Erreur lors de la récupération des fichiers modifiés: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"⚠️  Erreur inattendue: {e}", file=sys.stderr)
        return []


def filter_code_files(files: List[str], root_dir: str = ".") -> List[str]:
    """
    Filtre les fichiers pour ne garder que ceux qui doivent être analysés.

    Args:
        files: Liste des fichiers modifiés
        root_dir: Répertoire racine du projet

    Returns:
        Liste des fichiers de code à analyser
    """
    code_extensions = {
        ".dart",
        ".ts",
        ".tsx",
        ".js",
        ".jsx",
        ".py",
        ".java",
        ".kt",
        ".swift",
        ".go",
        ".rs",
        ".cpp",
        ".c",
        ".h",
        ".cs",
        ".php",
        ".rb",
        ".sh",
        ".yaml",
        ".yml",
        ".json",
        ".xml",
        ".md",
        ".sql",
        ".html",
        ".css",
        ".scss",
        ".sass",
        ".vue",
        ".svelte",
    }

    excluded_patterns = [
        "node_modules",
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        "build",
        "dist",
        ".next",
        ".dart_tool",
        ".gradle",
        ".min.js",
        ".min.css",
        ".bundle.js",
        ".chunk.js",
        ".g.dart",
        ".freezed.dart",
        ".pb.dart",
        ".d.ts",
    ]

    filtered = []
    for file_path in files:
        # Vérifier les patterns exclus
        if any(pattern in file_path for pattern in excluded_patterns):
            continue

        # Vérifier l'extension
        ext = os.path.splitext(file_path)[1].lower()
        if ext in code_extensions or ext == "":
            # Construire le chemin absolu
            full_path = os.path.join(root_dir, file_path)
            if os.path.exists(full_path):
                filtered.append(full_path)

    return filtered


def main():
    """Point d'entrée principal"""
    import argparse

    parser = argparse.ArgumentParser(description="Analyse les fichiers modifiés dans Git")
    parser.add_argument("--base", type=str, help="Référence Git de base (ex: origin/main)")
    parser.add_argument(
        "--head", type=str, default="HEAD", help="Référence Git de tête (défaut: HEAD)"
    )
    parser.add_argument("--root", type=str, default=".", help="Répertoire racine du projet")
    parser.add_argument("--output", type=str, help="Fichier de sortie pour la liste des fichiers")

    args = parser.parse_args()

    # Récupérer les fichiers modifiés
    changed_files = get_changed_files(args.base, args.head)

    if not changed_files:
        print("ℹ️  Aucun fichier modifié détecté")
        sys.exit(0)

    # Filtrer les fichiers de code
    code_files = filter_code_files(changed_files, args.root)

    if not code_files:
        print("ℹ️  Aucun fichier de code à analyser parmi les fichiers modifiés")
        sys.exit(0)

    # Afficher ou sauvegarder la liste
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            for file_path in code_files:
                f.write(f"{file_path}\n")
        print(f"✅ Liste sauvegardée dans {args.output}")
    else:
        # Afficher la liste (une par ligne) pour être utilisé par d'autres scripts
        for file_path in code_files:
            print(file_path)

    print(f"📋 {len(code_files)} fichier(s) de code à analyser", file=sys.stderr)


if __name__ == "__main__":
    main()
