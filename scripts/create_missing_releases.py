#!/usr/bin/env python3
"""
Script pour créer automatiquement toutes les releases GitHub manquantes
pour les tags existants.

Usage:
    python scripts/create_missing_releases.py [--dry-run] [--token GITHUB_TOKEN]

Le script:
1. Liste tous les tags Git locaux
2. Vérifie quelles releases existent déjà sur GitHub
3. Pour chaque tag sans release, extrait les notes du CHANGELOG.md
4. Crée la release via l'API GitHub

Configuration:
    - GITHUB_TOKEN: Token GitHub avec permission 'repo' ou 'public_repo'
    - GITHUB_REPOSITORY: Format 'owner/repo' (détecté automatiquement depuis Git)
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests


def get_git_remote_url() -> Optional[str]:
    """Récupère l'URL du remote origin."""
    try:
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True,
            text=True,
            check=True,
        )
        url = result.stdout.strip()
        # Convertir SSH en HTTPS si nécessaire
        if url.startswith("git@"):
            url = url.replace(":", "/").replace("git@", "https://")
        return url
    except subprocess.CalledProcessError:
        return None


def extract_repo_from_url(url: str) -> Optional[Tuple[str, str]]:
    """Extrait owner/repo depuis une URL GitHub."""
    # Format: https://github.com/owner/repo.git ou https://github.com/owner/repo
    patterns = [
        r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?/?$",
        r"git@github\.com:([^/]+)/([^/]+?)(?:\.git)?/?$",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return (match.group(1), match.group(2))
    return None


def get_repository_info() -> Tuple[str, str]:
    """Récupère les informations du repository (owner, repo)."""
    # Essayer depuis la variable d'environnement
    repo_env = os.getenv("GITHUB_REPOSITORY")
    if repo_env:
        parts = repo_env.split("/")
        if len(parts) == 2:
            return (parts[0], parts[1])

    # Essayer depuis Git
    url = get_git_remote_url()
    if url:
        repo_info = extract_repo_from_url(url)
        if repo_info:
            return repo_info

    # Par défaut (basé sur le projet)
    return ("adryserage", "aetheris")


def get_all_tags() -> List[str]:
    """Récupère tous les tags Git locaux, triés par version."""
    try:
        result = subprocess.run(
            ["git", "tag", "-l"],
            capture_output=True,
            text=True,
            check=True,
        )
        tags = [tag.strip() for tag in result.stdout.strip().split("\n") if tag.strip()]
        # Trier par version (semver)
        tags.sort(key=lambda x: tuple(map(int, x.lstrip("v").split("."))))
        return tags
    except subprocess.CalledProcessError:
        return []


def get_existing_releases(owner: str, repo: str, token: str) -> List[str]:
    """Récupère la liste des tags qui ont déjà une release."""
    url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    existing_tags = []
    page = 1
    per_page = 100

    while True:
        params = {"page": page, "per_page": per_page}
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            releases = response.json()

            if not releases:
                break

            for release in releases:
                tag_name = release.get("tag_name")
                if tag_name:
                    existing_tags.append(tag_name)

            if len(releases) < per_page:
                break

            page += 1
        except requests.RequestException as e:
            print(f"❌ Erreur lors de la récupération des releases: {e}", file=sys.stderr)
            break

    return existing_tags


def extract_release_notes(version: str) -> str:
    """Extrait les notes de release du CHANGELOG.md."""
    project_root = Path(__file__).parent.parent
    changelog_path = project_root / "CHANGELOG.md"

    if not changelog_path.exists():
        return f"Release {version}"

    content = changelog_path.read_text(encoding="utf-8")

    # Pattern pour trouver la section de la version
    version_pattern = rf"## \[{re.escape(version)}\]"
    match = re.search(version_pattern, content)
    if not match:
        return f"Release {version}"

    start_pos = match.start()
    next_version_pattern = r"## \[[\d.]+\]"
    next_match = re.search(next_version_pattern, content[start_pos + len(match.group()) :])

    if next_match:
        end_pos = start_pos + len(match.group()) + next_match.start()
        notes = content[start_pos:end_pos].strip()
    else:
        notes = content[start_pos:].strip()

    # Nettoyer les notes (supprimer les liens de comparaison)
    notes = re.sub(r"^\[[\d.]+\]:.*$", "", notes, flags=re.MULTILINE)
    notes = notes.strip()

    return notes if notes else f"Release {version}"


def create_release(
    owner: str, repo: str, tag: str, notes: str, token: str, dry_run: bool = False
) -> bool:
    """Crée une release GitHub."""
    url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    # Déterminer si c'est une pre-release
    is_prerelease = any(marker in tag for marker in ["-alpha", "-beta", "-rc", "-pre"])

    data = {
        "tag_name": tag,
        "name": f"Release {tag}",
        "body": notes,
        "draft": False,
        "prerelease": is_prerelease,
    }

    if dry_run:
        print(f"  [DRY-RUN] Créerait la release {tag}")
        print(f"  [DRY-RUN] Notes (premiers 100 caractères): {notes[:100]}...")
        return True

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        release = response.json()
        print(f"  ✅ Release créée: {release.get('html_url', 'N/A')}")
        return True
    except requests.RequestException as e:
        print(f"  ❌ Erreur lors de la création: {e}", file=sys.stderr)
        if hasattr(e.response, "text"):
            print(f"  Détails: {e.response.text}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Créer automatiquement toutes les releases GitHub manquantes"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Afficher ce qui serait fait sans créer réellement les releases",
    )
    parser.add_argument(
        "--token",
        help="Token GitHub (ou utiliser la variable d'environnement GITHUB_TOKEN)",
    )
    parser.add_argument(
        "--owner",
        help="Propriétaire du repository (détecté automatiquement si non spécifié)",
    )
    parser.add_argument(
        "--repo",
        help="Nom du repository (détecté automatiquement si non spécifié)",
    )

    args = parser.parse_args()

    # Récupérer le token
    token = args.token or os.getenv("GITHUB_TOKEN")
    if not token:
        print("❌ Token GitHub requis", file=sys.stderr)
        print("   Options:", file=sys.stderr)
        print("   1. Utilisez --token VOTRE_TOKEN", file=sys.stderr)
        print("   2. Ou définissez GITHUB_TOKEN dans l'environnement", file=sys.stderr)
        sys.exit(1)

    # Récupérer les infos du repository
    if args.owner and args.repo:
        owner, repo = args.owner, args.repo
    else:
        owner, repo = get_repository_info()
        if args.owner:
            owner = args.owner
        if args.repo:
            repo = args.repo

    print(f"📦 Repository: {owner}/{repo}")
    print(f"🔑 Token: {'***' + token[-4:] if len(token) > 4 else '***'}")
    print(f"🧪 Mode: {'DRY-RUN' if args.dry_run else 'PRODUCTION'}")
    print()

    # Récupérer tous les tags
    print("🔍 Récupération des tags Git...")
    all_tags = get_all_tags()
    print(f"   Trouvé {len(all_tags)} tags: {', '.join(all_tags)}")
    print()

    # Récupérer les releases existantes
    print("🔍 Vérification des releases existantes sur GitHub...")
    existing_releases = get_existing_releases(owner, repo, token)
    print(f"   {len(existing_releases)} releases existantes: {', '.join(existing_releases)}")
    print()

    # Identifier les tags sans release
    missing_tags = [tag for tag in all_tags if tag not in existing_releases]
    if not missing_tags:
        print("✅ Tous les tags ont déjà une release!")
        return

    print(f"📝 {len(missing_tags)} releases à créer: {', '.join(missing_tags)}")
    print()

    # Créer les releases manquantes
    success_count = 0
    for tag in missing_tags:
        version = tag.lstrip("v")
        print(f"📦 Traitement de {tag} (version {version})...")

        # Extraire les notes du CHANGELOG
        notes = extract_release_notes(version)
        if not notes or notes == f"Release {version}":
            print(
                f"  ⚠️  Aucune note trouvée dans le CHANGELOG, utilisation d'un message par défaut"
            )

        # Créer la release
        if create_release(owner, repo, tag, notes, token, args.dry_run):
            success_count += 1
        print()

    print("=" * 60)
    if args.dry_run:
        print(f"🧪 DRY-RUN: {success_count}/{len(missing_tags)} releases seraient créées")
    else:
        print(f"✅ {success_count}/{len(missing_tags)} releases créées avec succès")
    print("=" * 60)


if __name__ == "__main__":
    main()
