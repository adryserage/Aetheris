# Scripts utilitaires

## analyze_changes.py

Script pour analyser les fichiers modifiés dans Git. Utilisé principalement par le workflow GitHub Actions en mode diff.

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

### Notes

Le script filtre automatiquement les fichiers pour ne garder que ceux qui doivent être analysés :

- Extensions de code source supportées
- Exclusion des fichiers générés, node_modules, etc.
- Exclusion des fichiers binaires et trop volumineux
