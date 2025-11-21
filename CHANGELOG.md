# Changelog

Tous les changements notables de ce projet seront documentés dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère à [Semantic Versioning](https://semver.org/lang/fr/).

## [1.0.5] - 2025-01-XX

### 🚀 Publication sur PyPI

- **Publication sur PyPI** : Le package est maintenant disponible sur PyPI (Python Package Index)
- **Installation simplifiée** : Plus besoin de `--extra-index-url`, installez simplement avec `pip install adryserage-aetheris`
- Correction du workflow de publication (suppression de GitHub Packages avec URL incorrecte)
- Workflow GitHub Actions mis à jour pour publier uniquement sur PyPI

### 📦 Package

- Nom du package : `adryserage-aetheris`
- Commande CLI : `aetheris` (inchangée)
- Installation : `pip install adryserage-aetheris` (depuis PyPI)

## [1.0.4] - 2025-01-XX

### 🔧 Corrections

- Ajout du support PyPI dans le workflow de publication
- Configuration du token PyPI comme secret GitHub
- Mise à jour des workflows avec les dernières versions des actions GitHub (checkout@v4, setup-python@v5)

## [1.0.3] - 2025-01-XX

### 🚀 Publication

- Renommage du package Python en `adryserage-aetheris` pour publication
- Configuration complète du package avec `pyproject.toml`
- Ajout de la commande CLI `aetheris` avec sous-commandes (`aetheris analysis`)
- Workflow GitHub Actions pour publication automatique lors des tags de version
- Documentation mise à jour avec instructions d'installation

## [1.0.2] - 2025-11-21

### 🔧 Corrections

- Correction de la commande `gh pr diff` qui utilisait des flags invalides (`--json` et `--jq` non supportés)
- Remplacement par `gh pr view` avec filtrage approprié pour exclure les fichiers supprimés
- Alignement du comportement entre les modes PR et commit pour exclure les fichiers supprimés (cohérence avec `git diff --diff-filter=ACMR`)

## [1.0.1] - 2025-11-21

### 🔧 Corrections

- Correction du workflow GitHub Actions pour utiliser `gh pr view` au lieu de `gh pr diff` pour récupérer les fichiers modifiés dans les pull requests

## [1.0.0] - 2025-11-21

### ✨ Fonctionnalités

- Ajout du support pour analyser uniquement les fichiers modifiés dans le Code Analyzer
- Support des analyses ciblées pour les Pull Requests et commits
- Mode `--changed-files-only` avec support des fichiers spécifiés via arguments ou variables d'environnement
- Support du numéro de PR pour enrichir les rapports d'analyse

### 📚 Documentation

- Documentation complète du système dans le README.md
- Instructions d'installation et de configuration détaillées
- Guide d'utilisation avec exemples
- Documentation des agents d'analyse et de leurs fonctionnalités

### 🏗️ Infrastructure

- Workflow GitHub Actions pour l'analyse automatique de code
- Support des analyses complètes et ciblées
- Génération automatique de rapports en tant qu'artifacts GitHub

### 🎉 Version initiale

- Système d'analyse de code multi-agents avec 6 agents spécialisés :
  - Code Analysis Expert (CAE)
  - Architect Analysis Agent (AAA)
  - Security Analysis Agent (SSA)
  - Code Metrics Agent (CMA)
  - Dependency Vulnerability Agent (DVA)
  - Quality Assurance Agent (QAA)
- Support de multiples langages de programmation
- Analyse des vulnérabilités via l'API OSV
- Génération de rapports détaillés en Markdown
- Configuration flexible via variables d'environnement



[1.0.5]: https://github.com/adryserage/aetheris/compare/v1.0.4...v1.0.5
[1.0.4]: https://github.com/adryserage/aetheris/compare/v1.0.3...v1.0.4
[1.0.3]: https://github.com/adryserage/aetheris/compare/v1.0.2...v1.0.3
[1.0.2]: https://github.com/adryserage/aetheris/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/adryserage/aetheris/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/adryserage/aetheris/releases/tag/v1.0.0
