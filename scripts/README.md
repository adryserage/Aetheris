# Scripts utilitaires

Ce dossier contient des scripts utilitaires pour Aetheris by Allowebs.

## analyze_changes.py

Script pour analyser les fichiers modifiés dans Git. Utilisé principalement par le workflow GitHub Actions en mode diff pour identifier les fichiers à analyser.

### Utilisation

```bash
# Analyser les fichiers modifiés depuis le dernier commit
python scripts/analyze_changes.py

# Analyser les fichiers modifiés entre deux branches
python scripts/analyze_changes.py --base origin/main --head HEAD

# Sauvegarder la liste dans un fichier
python scripts/analyze_changes.py --output changed_files.txt
```

### Options

- `--base REF` : Référence Git de base (ex: `origin/main`, `HEAD~1`)
- `--head REF` : Référence Git de tête (défaut: `HEAD`)
- `--root DIR` : Répertoire racine du projet (défaut: `.`)
- `--output FILE` : Fichier de sortie pour la liste des fichiers

### Filtrage automatique

Le script filtre automatiquement les fichiers pour ne garder que ceux qui doivent être analysés :

- **Extensions supportées** : `.dart`, `.ts`, `.tsx`, `.js`, `.jsx`, `.py`, `.java`, `.kt`, `.swift`, `.go`, `.rs`, `.cpp`, `.c`, `.h`, `.cs`, `.php`, `.rb`, `.sh`, `.yaml`, `.yml`, `.json`, `.xml`, `.md`, `.sql`, `.html`, `.css`, `.scss`, `.sass`, `.vue`, `.svelte`
- **Exclusions** : 
  - Dossiers : `node_modules`, `.git`, `.venv`, `venv`, `__pycache__`, `build`, `dist`, `.next`, `.dart_tool`, `.gradle`
  - Fichiers générés : `.min.js`, `.min.css`, `.bundle.js`, `.chunk.js`, `.g.dart`, `.freezed.dart`, `.pb.dart`, `.d.ts`

### Intégration avec Aetheris

Ce script est utilisé par le workflow GitHub Actions pour déterminer quels fichiers analyser lors des Pull Requests ou commits. Il peut également être utilisé localement pour préparer une liste de fichiers à analyser avec `aetheris analysis --changed-files-only --files ...`.
