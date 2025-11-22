#!/usr/bin/env python3
"""
Script pour extraire les notes de release du CHANGELOG.md pour une version donnée.
Usage: python extract_release_notes.py <version>
Exemple: python extract_release_notes.py 1.1.0
"""

import re
import sys
from pathlib import Path


def extract_release_notes(changelog_path: Path, version: str) -> str:
    """
    Extrait les notes de release pour une version donnée du CHANGELOG.

    Args:
        changelog_path: Chemin vers le fichier CHANGELOG.md
        version: Version à extraire (ex: "1.1.0")

    Returns:
        Les notes de release formatées en Markdown
    """
    if not changelog_path.exists():
        return f"Release {version}"

    content = changelog_path.read_text(encoding="utf-8")

    # Pattern pour trouver la section de la version
    # Format attendu: ## [1.1.0] - 2025-01-15
    version_pattern = rf"## \[{re.escape(version)}\]"

    # Trouver le début de la section de version
    match = re.search(version_pattern, content)
    if not match:
        return f"Release {version}"

    start_pos = match.start()

    # Trouver la fin de la section (début de la prochaine version ou fin du fichier)
    next_version_pattern = r"## \[[\d.]+\]"
    next_match = re.search(next_version_pattern, content[start_pos + len(match.group()) :])

    if next_match:
        end_pos = start_pos + len(match.group()) + next_match.start()
        notes = content[start_pos:end_pos].strip()
    else:
        # C'est la dernière version, prendre jusqu'à la fin
        notes = content[start_pos:].strip()

    # Nettoyer les notes (supprimer les liens de comparaison à la fin)
    # Format: [1.1.0]: https://github.com/...
    notes = re.sub(r"^\[[\d.]+\]:.*$", "", notes, flags=re.MULTILINE)
    notes = notes.strip()

    return notes if notes else f"Release {version}"


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_release_notes.py <version>", file=sys.stderr)
        sys.exit(1)

    version = sys.argv[1]

    # Trouver le CHANGELOG.md (à la racine du projet)
    project_root = Path(__file__).parent.parent
    changelog_path = project_root / "CHANGELOG.md"

    notes = extract_release_notes(changelog_path, version)
    # Utiliser sys.stdout.buffer pour éviter les problèmes d'encodage avec les emojis
    sys.stdout.buffer.write(notes.encode("utf-8"))
    sys.stdout.buffer.write(b"\n")


if __name__ == "__main__":
    main()
