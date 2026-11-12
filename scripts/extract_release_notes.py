#!/usr/bin/env python3
"""
Extrait les notes de release du CHANGELOG.md pour une version donnée.

Usage: python extract_release_notes.py <version> [chemin/vers/CHANGELOG.md]
Exemple: python extract_release_notes.py 4.0.0

Codes de sortie : 0 si la section existe, 1 si le CHANGELOG ou la section est introuvable.
Si la section contient « Changements incompatibles », un avertissement bilingue
(anglais et français) est placé en tête des notes.
"""

import re
import sys
from pathlib import Path

BREAKING_HEADING = "### 💥 Changements incompatibles"

BREAKING_WARNING = """\
> **Breaking change for 3.x users.** Version 4 turns Aetheris into an MCP server. \
The analysis commands (`aetheris analysis`, `fix`, `pr`, `issues`, `stats`, `run`) are removed \
and exit with code 2. To keep them, pin `adryserage-aetheris==3.0.0`.
>
> **Changement incompatible pour les utilisateurs de la 3.x.** La version 4 fait d'Aetheris \
un serveur MCP. Les commandes d'analyse (`aetheris analysis`, `fix`, `pr`, `issues`, `stats`, \
`run`) sont retirées et sortent avec le code 2. Pour les garder, fixez \
`adryserage-aetheris==3.0.0`.
"""


def extract_release_notes(changelog_path: Path, version: str) -> str | None:
    """Retourne les notes de la version, ou None si le fichier ou la section manque."""
    if not changelog_path.exists():
        return None

    content = changelog_path.read_text(encoding="utf-8")

    match = re.search(rf"^## \[{re.escape(version)}\]", content, flags=re.MULTILINE)
    if not match:
        return None

    body_start = match.end()
    next_match = re.search(r"^## \[", content[body_start:], flags=re.MULTILINE)
    end_pos = body_start + next_match.start() if next_match else len(content)
    notes = content[match.start() : end_pos]

    # Retire les liens de comparaison en fin de section: [1.1.0]: https://...
    notes = re.sub(r"^\[[^\]]+\]:.*$", "", notes, flags=re.MULTILINE).strip()

    if BREAKING_HEADING in notes:
        notes = f"{BREAKING_WARNING}\n{notes}"
    return notes


def main() -> int:
    if len(sys.argv) < 2:
        print(
            "Usage: python extract_release_notes.py <version> [CHANGELOG.md]",
            file=sys.stderr,
        )
        return 1

    version = sys.argv[1]
    changelog_path = (
        Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).parent.parent / "CHANGELOG.md"
    )

    notes = extract_release_notes(changelog_path, version)
    if notes is None:
        print(f"Aucune section [{version}] dans {changelog_path}", file=sys.stderr)
        return 1

    # sys.stdout.buffer évite les problèmes d'encodage avec les emojis
    sys.stdout.buffer.write(notes.encode("utf-8"))
    sys.stdout.buffer.write(b"\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
