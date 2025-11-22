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

## extract_release_notes.py

Script pour extraire les notes de release du CHANGELOG.md pour une version donnée. Utilisé par le workflow GitHub Actions pour créer automatiquement des releases GitHub avec les notes du changelog.

### Utilisation

```bash
# Extraire les notes pour une version spécifique
python scripts/extract_release_notes.py 1.1.0

# Les notes sont affichées sur stdout en UTF-8
python scripts/extract_release_notes.py 1.0.0 > release_notes.md
```

### Format attendu du CHANGELOG

Le script attend un format de CHANGELOG conforme à [Keep a Changelog](https://keepachangelog.com/):

```markdown
## [1.1.0] - 2025-01-15

### ✨ Nouvelles fonctionnalités

- ...

### 🔧 Modifications

- ...
```

### Intégration avec GitHub Actions

Ce script est utilisé automatiquement par le workflow `.github/workflows/create-release.yml` qui se déclenche lors de la création d'un tag de version (ex: `v1.1.0`). Le workflow:

1. Extrait la version du tag
2. Utilise ce script pour extraire les notes du CHANGELOG
3. Crée une release GitHub avec ces notes

## create_missing_releases.py

Script pour créer automatiquement toutes les releases GitHub manquantes pour les tags existants. Utile pour créer rétroactivement des releases pour des tags qui n'ont pas encore de release associée.

### Prérequis

- Token GitHub avec permission `repo` (pour les repos privés) ou `public_repo` (pour les repos publics)
- Accès au repository Git

### Utilisation

```bash
# Mode dry-run (affiche ce qui serait fait sans créer réellement)
python scripts/create_missing_releases.py --dry-run

# Créer toutes les releases manquantes
export GITHUB_TOKEN=votre_token_github
python scripts/create_missing_releases.py

# Ou spécifier le token directement
python scripts/create_missing_releases.py --token votre_token_github

# Spécifier manuellement le repository
python scripts/create_missing_releases.py --owner adryserage --repo aetheris
```

### Fonctionnement

Le script:

1. **Liste tous les tags Git locaux** - Récupère tous les tags du repository
2. **Vérifie les releases existantes** - Interroge l'API GitHub pour voir quelles releases existent déjà
3. **Identifie les tags sans release** - Compare les tags locaux avec les releases existantes
4. **Extrait les notes du CHANGELOG** - Pour chaque tag manquant, extrait les notes correspondantes
5. **Crée les releases** - Utilise l'API GitHub pour créer les releases avec les notes extraites

### Obtenir un token GitHub

1. Allez sur GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Cliquez sur "Generate new token (classic)"
3. Donnez un nom au token (ex: "Create Releases")
4. Sélectionnez la permission `repo` (pour les repos privés) ou `public_repo` (pour les repos publics)
5. Cliquez sur "Generate token"
6. Copiez le token et utilisez-le avec le script

### Exemple de sortie

```
📦 Repository: adryserage/aetheris
🔑 Token: ***abcd
🧪 Mode: PRODUCTION

🔍 Récupération des tags Git...
   Trouvé 11 tags: v1.0.0, v1.0.1, v1.0.2, ...

🔍 Vérification des releases existantes sur GitHub...
   3 releases existantes: v1.0.8, v1.0.9, v1.1.0

📝 8 releases à créer: v1.0.0, v1.0.1, v1.0.2, ...

📦 Traitement de v1.0.0 (version 1.0.0)...
  ✅ Release créée: https://github.com/adryserage/aetheris/releases/tag/v1.0.0
...
```
