# Changelog

Tous les changements notables de ce projet seront documentés dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère à [Semantic Versioning](https://semver.org/lang/fr/).

## [2.0.1] - 2025-01-16

### 🔧 Corrections

- **Migration de dépendance** : Remplacement de `duckduckgo-search` par `ddgs` (package renommé)
- **Correction modèle Gemini** : Changement du modèle par défaut de `gemini-1.5-flash` vers `gemini-1.5-pro` pour compatibilité avec l'API v1beta
- **Mise à jour dépendances** : `google-generativeai>=0.8.5` pour meilleur support des modèles récents

### 📦 Dépendances

- `ddgs>=1.0.0` remplace `duckduckgo-search>=6.0.0`
- `google-generativeai>=0.8.5` (au lieu de >=0.8.0)

## [2.0.0] - 2025-01-16

### ✨ Nouvelles fonctionnalités

- **Orchestrateur dédié** : Système d'orchestration séparé pour une meilleure maintenabilité et testabilité
- **Système de cache** : Cache basé sur git SHA + timestamp pour réduire les coûts API de 60-80%
- **Parallélisation intelligente** : Analyse des fichiers indépendants en parallèle basée sur le graphe de dépendances
- **Système de priorités** : Priorisation automatique des fichiers modifiés dans les PR (HIGH) et leurs dépendances (MEDIUM)
- **Métriques et monitoring** : Collecte complète de métriques de performance avec export JSON
- **Analyse incrémentale améliorée** : Détection automatique des fichiers dépendants avec profondeur configurable
- **Gestion d'erreurs améliorée** : Circuit breaker et backoff exponentiel pour une meilleure résilience

### 🔧 Modifications

- **Architecture** : Refactorisation de `CodeAnalyzer` pour utiliser un orchestrateur interne
- **Workflow** : Système de workflow avec étapes, dépendances et hooks
- **Configuration** : Nouvelles options (`enable_cache`, `cache_ttl_days`, `analyze_dependent_files`, `max_dependency_depth`, `enable_metrics`, `enable_priority_analysis`)
- **BaseAgent** : Intégration du circuit breaker pour éviter les appels répétés en cas d'erreur
- **Orchestrateur** : Support des hooks pour extensibilité et collecte de métriques

### 📦 Nouveaux modules

- `src/core/orchestrator.py` : Orchestrateur principal avec système de workflow
- `src/core/cache.py` : Système de cache avec stockage disque
- `src/core/error_handler.py` : Gestion d'erreurs avec circuit breaker
- `src/core/parallel_analyzer.py` : Parallélisation intelligente basée sur dépendances
- `src/core/priority_manager.py` : Gestionnaire de priorités pour PR reviews
- `src/core/metrics.py` : Collecteur de métriques de performance

### 📝 Documentation

- Documentation complète du système de plugins/hooks dans `docs/PLUGINS.md`
- Exemples d'utilisation et guide pour créer des plugins personnalisés

### 🔄 Compatibilité

- **Backward compatible** : L'API publique de `CodeAnalyzer` reste inchangée
- Les nouvelles fonctionnalités sont activées par défaut mais peuvent être désactivées via configuration

## [1.1.0] - 2025-01-15

### ✨ Nouvelles fonctionnalités

- **Affichage du reasoning** : Possibilité d'afficher le processus de raisonnement des modèles AI (si disponible)
- **Support OpenAI o1** : Support du reasoning pour les modèles o1-preview et o1-mini d'OpenAI
- **Panneau de reasoning** : Affichage du reasoning dans un panneau Rich dédié avec syntax highlighting

### 🔧 Modifications

- **AIProvider** : Ajout de la méthode `generate_content_with_reasoning()` pour récupérer le reasoning
- **BaseAgent** : Ajout de `_call_ai_with_reasoning()` pour utiliser le reasoning si activé
- **Configuration** : Ajout de l'option `show_reasoning` dans `AnalysisConfig`
- **Agents** : Passage de `progress_manager` aux agents pour afficher le reasoning

### 📝 Documentation

- Mise à jour du README avec explication du reasoning
- Ajout de la variable d'environnement `SHOW_REASONING` dans la documentation

## [1.0.9] - 2025-01-15

### ✨ Nouvelles fonctionnalités

- **Barre de progression moderne** : Ajout d'une barre de progression interactive avec Rich pour un suivi visuel clair de l'analyse
- **Affichage en temps réel** : Progression détaillée pour chaque étape (scan, analyse, rapports)
- **Statistiques visuelles** : Affichage du temps écoulé, temps restant et pourcentage de progression

### 🔧 Modifications

- **CodeAnalyzer** : Intégration de `ProgressManager` pour remplacer les logs simples par des barres de progression
- **Points d'entrée** : `main.py` et `src/cli.py` créent automatiquement un `ProgressManager` si le terminal le supporte
- **Fallback automatique** : Si Rich n'est pas disponible ou si on n'est pas dans un terminal interactif, le système utilise les logs simples

### 📦 Dépendances

- Ajout de `rich>=13.0.0` pour les barres de progression modernes

### 📝 Documentation

- Mise à jour du README avec description de la barre de progression

## [1.0.8] - 2025-01-15

### ✨ Nouvelles fonctionnalités

- **Support multi-fournisseurs AI** : Ajout du support pour OpenAI, Claude (Anthropic) et Gemini
- **Choix du modèle** : Possibilité de choisir le modèle AI selon le fournisseur sélectionné
- **Abstraction des providers** : Architecture modulaire permettant d'ajouter facilement de nouveaux fournisseurs AI
- **Documentation des coûts** : Ajout d'un tableau détaillé des coûts d'analyse dans le README
- **Modèles à jour** : Mise à jour avec les derniers modèles disponibles (Gemini 2.5 Pro, GPT-4o, Claude 3.5 Sonnet)

### 🔧 Modifications

- **Configuration** : Remplacement de `gemini_api_key` et `gemini_model` par `ai_api_key` et `ai_model` génériques
- **Variables d'environnement** : Ajout de `AI_PROVIDER` pour choisir le fournisseur (gemini, openai, claude)
- **BaseAgent** : Refactorisation pour utiliser l'abstraction `AIProvider` au lieu de Gemini directement
- **CodeGenerator** : Adaptation pour utiliser l'abstraction `AIProvider`

### 📦 Dépendances

- Ajout de `openai>=1.0.0` pour le support OpenAI
- Ajout de `anthropic>=0.25.0` pour le support Claude

### 📝 Documentation

- Ajout de la section "Choix du fournisseur AI" dans le README
- Ajout du tableau des modèles supportés par fournisseur
- Ajout de la section "Coûts d'analyse" avec estimations pour différents scénarios
- Mise à jour des instructions de configuration pour les différents fournisseurs

### 🔄 Compatibilité

- **Breaking change** : Les variables `GEMINI_API_KEY` et `GEMINI_MODEL` sont remplacées par `AI_PROVIDER`, `AI_API_KEY` (selon provider) et `AI_MODEL`
- Pour la rétrocompatibilité, si `AI_PROVIDER` n'est pas défini, le système utilise Gemini par défaut

## [1.0.7] - 2025-11-21

### 🔧 Corrections et améliorations

- **Dépendance obligatoire** : `ddgs` (anciennement `duckduckgo-search`) est maintenant une dépendance obligatoire au lieu d'optionnelle
- **Simplification du code** : Suppression des vérifications conditionnelles pour `ddgs` dans tout le codebase
- **Amélioration des imports** : Simplification des imports dans `main.py` et `src/cli.py` avec gestion d'erreur unifiée
- **Suppression des avertissements inutiles** : L'avertissement pour `ddgs` ne s'affiche plus si la recherche web est désactivée dans la configuration

### 📦 Dépendances

- `ddgs>=1.0.0` (anciennement `duckduckgo-search>=6.0.0`) déplacé des dépendances optionnelles vers les dépendances principales dans `pyproject.toml` et `requirements.txt`

### 📝 Documentation

- Mise à jour du README pour indiquer que `ddgs` est une dépendance obligatoire

## [1.0.6] - 2025-11-21

### 🔧 Corrections et améliorations

- **Workflows manuels uniquement** : Les workflows `code-review.yml` et `run-aetheris.yml` ne s'exécutent maintenant que manuellement
- **Installation PyPI** : Le workflow `run-aetheris.yml` utilise maintenant PyPI au lieu de GitHub Packages
- **Documentation** : Mise à jour complète de README, CHANGELOG, .gitignore, .gitattributes et scripts
- **Correction URLs** : Correction des URLs du repository dans pyproject.toml
- **Amélioration .gitignore** : Ajout des fichiers de packaging Python (build/, dist/, \*.egg-info, etc.)
- **Amélioration .gitattributes** : Ajout des règles de fin de ligne pour différents types de fichiers

### 📝 Documentation

- Mise à jour du README avec les liens PyPI et repository GitHub
- Documentation améliorée des scripts utilitaires
- CHANGELOG mis à jour avec toutes les versions

## [1.0.5] - 2025-11-21

### 🚀 Publication sur PyPI

- **Publication sur PyPI** : Le package est maintenant disponible sur PyPI (Python Package Index)
- **Installation simplifiée** : Plus besoin de `--extra-index-url`, installez simplement avec `pip install adryserage-aetheris`
- Correction du workflow de publication (suppression de GitHub Packages avec URL incorrecte)
- Workflow GitHub Actions mis à jour pour publier uniquement sur PyPI

### 📦 Package

- Nom du package : `adryserage-aetheris`
- Commande CLI : `aetheris` (inchangée)
- Installation : `pip install adryserage-aetheris` (depuis PyPI)

## [1.0.4] - 2025-11-21

### 🔧 Corrections

- Ajout du support PyPI dans le workflow de publication
- Configuration du token PyPI comme secret GitHub
- Mise à jour des workflows avec les dernières versions des actions GitHub (checkout@v4, setup-python@v5)

## [1.0.3] - 2025-11-21

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

[2.0.0]: https://github.com/adryserage/aetheris/compare/v1.1.0...v2.0.0
[1.1.0]: https://github.com/adryserage/aetheris/compare/v1.0.9...v1.1.0
[1.0.9]: https://github.com/adryserage/aetheris/compare/v1.0.8...v1.0.9
[1.0.8]: https://github.com/adryserage/aetheris/compare/v1.0.7...v1.0.8
[1.0.7]: https://github.com/adryserage/aetheris/compare/v1.0.6...v1.0.7
[1.0.6]: https://github.com/adryserage/aetheris/compare/v1.0.5...v1.0.6
[1.0.5]: https://github.com/adryserage/aetheris/compare/v1.0.4...v1.0.5
[1.0.4]: https://github.com/adryserage/aetheris/compare/v1.0.3...v1.0.4
[1.0.3]: https://github.com/adryserage/aetheris/compare/v1.0.2...v1.0.3
[1.0.2]: https://github.com/adryserage/aetheris/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/adryserage/aetheris/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/adryserage/aetheris/releases/tag/v1.0.0
