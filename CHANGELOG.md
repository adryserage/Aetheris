# Changelog

Tous les changements notables de ce projet seront documentés dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère à [Semantic Versioning](https://semver.org/lang/fr/).

## [1.0.1] - 2025-11-21

### 🔧 Corrections
- Correction du workflow GitHub Actions pour utiliser `gh pr view` au lieu de `gh pr diff` pour récupérer les fichiers modifiés dans les pull requests

## [1.0.0] - 2025-01-XX

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

## [0.1.0] - 2025-01-XX

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

[1.0.1]: https://github.com/adryserage/code_reviewer/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/adryserage/code_reviewer/compare/v0.1.0...v1.0.0
[0.1.0]: https://github.com/adryserage/code_reviewer/releases/tag/v0.1.0

