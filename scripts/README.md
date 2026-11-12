# Scripts utilitaires

Ce dossier contient des scripts utilitaires pour Aetheris by Adryan.

## extract_release_notes.py

Script pour extraire les notes de release du CHANGELOG.md pour une version donnée. Utilisé par le workflow GitHub Actions pour créer automatiquement des releases GitHub avec les notes du changelog.

### Utilisation

```bash
# Extraire les notes pour une version spécifique
python scripts/extract_release_notes.py 1.1.0

# Les notes sont affichées sur stdout en UTF-8
python scripts/extract_release_notes.py 1.0.0 > release_notes.md

# Lire un autre fichier que le CHANGELOG.md du dépôt
python scripts/extract_release_notes.py 4.0.0 /chemin/vers/CHANGELOG.md
```

Le script sort avec le code 1 si le CHANGELOG ou la section de la version est introuvable. Quand la section contient « Changements incompatibles », il place en tête un avertissement en anglais et en français qui indique d'épingler `adryserage-aetheris==3.0.0` pour garder les commandes d'analyse.

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

Ce script est utilisé automatiquement par le workflow `.github/workflows/release.yml` qui se déclenche lors de la création d'un tag de version (ex: `v1.1.0`). Le workflow:

1. Extrait la version du tag et vérifie qu'elle correspond à celle de `pyproject.toml`
2. Utilise ce script pour extraire les notes du CHANGELOG
3. Crée une release GitHub avec ces notes

